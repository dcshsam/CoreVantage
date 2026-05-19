"""
CoreShift Clean Core Analysis & Remediation Engine
Combines rule-based scanning with LLM-powered insights and auto-remediation.
"""

from __future__ import annotations
import difflib
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from core.abap_rules import (
    scan_code, compute_clean_core_level, compute_migration_score,
    Violation, LEVEL_META, SEVERITY_ORDER,
)

if TYPE_CHECKING:
    from core.llm_client import LLMClient


@dataclass
class CleanCoreResult:
    program_name:       str
    total_lines:        int
    violations:         List[Violation]
    clean_core_level:   str              # A, B, C, D
    migration_score:    int              # 0-100
    llm_analysis:       str  = ""
    remediated_code:    str  = ""
    diff_html:          str  = ""
    change_summary:     str  = ""

    # Convenience counters
    @property
    def critical_count(self): return sum(1 for v in self.violations if v.severity == "CRITICAL")
    @property
    def high_count(self):     return sum(1 for v in self.violations if v.severity == "HIGH")
    @property
    def medium_count(self):   return sum(1 for v in self.violations if v.severity == "MEDIUM")
    @property
    def low_count(self):      return sum(1 for v in self.violations if v.severity == "LOW")
    @property
    def total_violations(self): return len(self.violations)

    @property
    def level_meta(self): return LEVEL_META.get(self.clean_core_level, LEVEL_META["D"])

    def violations_by_category(self) -> dict:
        cats: dict = {}
        for v in self.violations:
            cats.setdefault(v.category, []).append(v)
        return cats


def analyse(
    code:         str,
    program_name: str = "Unknown",
    llm_client:   Optional["LLMClient"] = None,
    categories:   Optional[List[str]] = None,
) -> CleanCoreResult:
    """
    Full analysis pipeline:
    1. Rule-based scan (always runs)
    2. LLM enrichment (if client provided)
    """
    from prompts.clean_code import ANALYSIS_SYSTEM, ANALYSIS_USER

    violations    = scan_code(code, categories=categories)
    cc_level      = compute_clean_core_level(violations)
    mig_score     = compute_migration_score(violations)
    total_lines   = len(code.splitlines())

    result = CleanCoreResult(
        program_name=program_name,
        total_lines=total_lines,
        violations=violations,
        clean_core_level=cc_level,
        migration_score=mig_score,
    )

    if llm_client and violations:
        violations_summary = _format_violations_for_prompt(violations[:20])
        try:
            result.llm_analysis = llm_client.complete(
                ANALYSIS_SYSTEM,
                ANALYSIS_USER.format(
                    violations_summary=violations_summary,
                    code=code[:8000],
                ),
                max_tokens=2048,
            )
        except Exception as exc:
            result.llm_analysis = f"*LLM analysis unavailable: {exc}*"

    return result


def remediate(
    code:       str,
    violations: List[Violation],
    llm_client: "LLMClient",
) -> tuple[str, str]:
    """
    Returns (remediated_code, diff_html).
    Uses LLM to generate a compliant version of the code.
    """
    from prompts.clean_code import REMEDIATION_SYSTEM, REMEDIATION_USER

    violations_list = "\n".join(
        f"- [{v.rule_id}] Line {v.line_number}: {v.rule.name} — {v.remediation}"
        for v in violations[:30]
    )

    remediated = llm_client.complete(
        REMEDIATION_SYSTEM,
        REMEDIATION_USER.format(
            violations_list=violations_list,
            code=code[:10000],
        ),
        max_tokens=4096,
        temperature=0.05,
    )

    # Strip any markdown fences the LLM may have added
    remediated = _strip_code_fences(remediated)
    diff_html  = generate_diff_html(code, remediated)
    return remediated, diff_html


def generate_diff_html(original: str, remediated: str) -> str:
    """Generates a side-by-side HTML diff with colour coding."""
    orig_lines = original.splitlines(keepends=True)
    remed_lines = remediated.splitlines(keepends=True)

    differ = difflib.unified_diff(orig_lines, remed_lines, lineterm="",
                                  fromfile="Original", tofile="Remediated", n=3)
    diff_lines = list(differ)

    if not diff_lines:
        return "<p style='color:#888'>No changes — code is already compliant.</p>"

    rows: List[str] = []
    for line in diff_lines:
        line_e = _html_escape(line.rstrip("\n"))
        if line.startswith("+++") or line.startswith("---"):
            rows.append(f'<div class="diff-header">{line_e}</div>')
        elif line.startswith("@@"):
            rows.append(f'<div class="diff-hunk">{line_e}</div>')
        elif line.startswith("+"):
            rows.append(f'<div class="diff-add">+ {line_e[1:]}</div>')
        elif line.startswith("-"):
            rows.append(f'<div class="diff-del">- {line_e[1:]}</div>')
        else:
            rows.append(f'<div class="diff-ctx">  {line_e[1:]}</div>')

    return (
        '<div class="diff-container">'
        + "".join(rows)
        + "</div>"
    )


def compute_remediation_coverage(original_violations: List[Violation],
                                  remediated_code: str) -> float:
    """Estimates % of violations fixed by checking if patterns still present."""
    if not original_violations:
        return 100.0
    remaining = scan_code(remediated_code)
    remaining_ids = {(v.rule_id, v.line_number) for v in remaining}
    fixed = sum(1 for v in original_violations
                if (v.rule_id, v.line_number) not in remaining_ids)
    return round(fixed / len(original_violations) * 100, 1)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _format_violations_for_prompt(violations: List[Violation]) -> str:
    lines = []
    for v in violations:
        lines.append(
            f"[{v.rule_id}] {v.rule.name} (Line {v.line_number}, {v.severity})\n"
            f"  Code: {v.line_content[:100]}\n"
            f"  Fix:  {v.remediation[:120]}"
        )
    return "\n\n".join(lines)


def _strip_code_fences(text: str) -> str:
    import re
    text = re.sub(r'^```(?:abap|ABAP)?\s*\n', '', text.strip(), flags=re.MULTILINE)
    text = re.sub(r'\n```\s*$', '', text.strip(), flags=re.MULTILINE)
    return text.strip()


def _html_escape(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
