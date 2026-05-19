"""
CodeVantage S/4HANA Migration Analysis Engine
Analyses ECC ABAP code for S/4HANA compatibility and generates migration plans.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from core.abap_rules import scan_code, compute_migration_score, Violation

if TYPE_CHECKING:
    from core.llm_client import LLMClient

EFFORT_MATRIX = {
    "CRITICAL": {"days": 5, "risk": "HIGH"},
    "HIGH":     {"days": 3, "risk": "MEDIUM"},
    "MEDIUM":   {"days": 1, "risk": "LOW"},
    "LOW":      {"days": 0.5, "risk": "INFO"},
    "INFO":     {"days": 0.1, "risk": "INFO"},
}


@dataclass
class MigrationResult:
    program_name:      str
    total_lines:       int
    violations:        List[Violation]
    readiness_score:   int          # 0-100
    effort_days:       float
    risk_level:        str          # HIGH / MEDIUM / LOW
    approach:          str          # BROWNFIELD / SELECTIVE_DATA / GREENFIELD
    llm_analysis:      str = ""
    migration_plan:    str = ""
    remediated_code:   str = ""
    diff_html:         str = ""

    @property
    def s4_violations(self):
        return [v for v in self.violations if v.category == "S4_MIGRATION" or v.rule.s4_impact]

    @property
    def critical_count(self): return sum(1 for v in self.s4_violations if v.severity == "CRITICAL")
    @property
    def high_count(self):     return sum(1 for v in self.s4_violations if v.severity == "HIGH")
    @property
    def total_violations(self): return len(self.s4_violations)

    def score_color(self) -> str:
        if self.readiness_score >= 80: return "#30D158"
        if self.readiness_score >= 50: return "#FF9F0A"
        return "#FF453A"

    def score_label(self) -> str:
        if self.readiness_score >= 80: return "Migration Ready"
        if self.readiness_score >= 50: return "Needs Remediation"
        return "High Risk — Significant Rework Required"


def analyse(
    code:         str,
    program_name: str = "Unknown",
    llm_client:   Optional["LLMClient"] = None,
) -> MigrationResult:
    """Full S/4HANA migration analysis pipeline."""
    from prompts.s4_migration import ANALYSIS_SYSTEM, ANALYSIS_USER

    all_violations  = scan_code(code, categories=["S4_MIGRATION", "CLEAN_CORE", "PERFORMANCE", "SECURITY"])
    readiness_score = compute_migration_score(all_violations)
    effort_days     = sum(
        EFFORT_MATRIX.get(v.severity, {"days": 1})["days"]
        for v in all_violations if v.category == "S4_MIGRATION" or v.rule.s4_impact
    )
    risk_level = "HIGH" if readiness_score < 50 else ("MEDIUM" if readiness_score < 80 else "LOW")
    approach   = _recommend_approach(all_violations, readiness_score)

    result = MigrationResult(
        program_name=program_name,
        total_lines=len(code.splitlines()),
        violations=all_violations,
        readiness_score=readiness_score,
        effort_days=round(effort_days, 1),
        risk_level=risk_level,
        approach=approach,
    )

    if llm_client:
        vsummary = _format_violations(all_violations[:20])
        try:
            result.llm_analysis = llm_client.complete(
                ANALYSIS_SYSTEM,
                ANALYSIS_USER.format(violations_summary=vsummary, code=code[:8000]),
                max_tokens=2048,
            )
            # Sync readiness score from LLM output (LLM has more context than rule-engine alone)
            llm_score = _parse_llm_score(result.llm_analysis)
            if llm_score is not None:
                result.readiness_score = llm_score
                result.risk_level = "HIGH" if llm_score < 50 else ("MEDIUM" if llm_score < 80 else "LOW")
                result.approach   = _recommend_approach(all_violations, llm_score)
        except Exception as exc:
            result.llm_analysis = f"*LLM analysis unavailable: {exc}*"

    return result


def generate_migration_plan(result: MigrationResult, llm_client: "LLMClient") -> str:
    """Generates a full sprint-by-sprint migration plan using the LLM."""
    from prompts.s4_migration import MIGRATION_PLAN_SYSTEM, MIGRATION_PLAN_USER

    summary = (
        f"Program: {result.program_name}\n"
        f"Lines: {result.total_lines}\n"
        f"Readiness Score: {result.readiness_score}/100\n"
        f"Risk Level: {result.risk_level}\n"
        f"Estimated Effort: {result.effort_days} days\n"
        f"Recommended Approach: {result.approach}"
    )
    return llm_client.complete(
        MIGRATION_PLAN_SYSTEM,
        MIGRATION_PLAN_USER.format(
            analysis_summary=summary,
            violations_summary=_format_violations(result.violations[:30]),
        ),
        max_tokens=3000,
    )


def remediate(
    code:       str,
    violations: List[Violation],
    llm_client: "LLMClient",
) -> tuple[str, str]:
    """Migrate ECC code to S/4HANA. Returns (migrated_code, diff_html)."""
    from prompts.s4_migration import REMEDIATION_SYSTEM, REMEDIATION_USER
    from core.clean_code_engine import generate_diff_html, _strip_code_fences

    vlist = "\n".join(
        f"- [{v.rule_id}] Line {v.line_number}: {v.rule.name} → {v.remediation}"
        for v in violations[:30]
    )
    migrated = llm_client.complete(
        REMEDIATION_SYSTEM,
        REMEDIATION_USER.format(violations_list=vlist, code=code[:10000]),
        max_tokens=4096,
        temperature=0.05,
    )
    migrated  = _strip_code_fences(migrated)
    diff_html = generate_diff_html(code, migrated)
    return migrated, diff_html


def _recommend_approach(violations: List[Violation], score: int) -> str:
    critical = sum(1 for v in violations if v.severity == "CRITICAL")
    if critical > 3 or score < 30:
        return "GREENFIELD"
    if score < 70:
        return "SELECTIVE_DATA"
    return "BROWNFIELD"


def _format_violations(violations: List[Violation]) -> str:
    lines = []
    for v in violations:
        lines.append(
            f"[{v.rule_id}] {v.rule.name} ({v.severity}) — Line {v.line_number}\n"
            f"  {v.line_content[:100]}\n"
            f"  Fix: {v.remediation[:120]}"
        )
    return "\n\n".join(lines)


def _parse_llm_score(text: str) -> Optional[int]:
    """Extract the first nn/100 score from LLM analysis output."""
    match = re.search(r'\b(\d{1,3})/100\b', text)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score
    return None
