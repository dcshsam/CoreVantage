"""
CoreShift — Custom Rule Engine
Admin-managed ABAP rules stored in data/custom_rules.json.
Merged automatically into scan_code() alongside built-in rules.
"""

from __future__ import annotations
import json
import re
import uuid
from pathlib import Path
from typing import List

DATA_DIR         = Path(__file__).parent.parent / "data"
CUSTOM_RULES_FILE = DATA_DIR / "custom_rules.json"

CATEGORIES = ["CLEAN_CORE", "S4_MIGRATION", "SECURITY", "PERFORMANCE"]
SEVERITIES  = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
CC_LEVELS   = ["", "A", "B", "C", "D"]


# ── Persistence ───────────────────────────────────────────────────────────────

def load_custom_rules() -> list[dict]:
    """Return all saved custom rules as raw dicts (including disabled ones)."""
    if not CUSTOM_RULES_FILE.exists():
        return []
    try:
        data = json.loads(CUSTOM_RULES_FILE.read_text(encoding="utf-8"))
        return data.get("rules", [])
    except Exception:
        return []


def _save_custom_rules(rules: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CUSTOM_RULES_FILE.write_text(
        json.dumps({"rules": rules}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _next_id(existing: list[dict]) -> str:
    """Auto-generate next CX-### id."""
    used = set()
    for r in existing:
        rid = r.get("id", "")
        if re.match(r"^CX-\d+$", rid):
            used.add(int(rid.split("-")[1]))
    n = 1
    while n in used:
        n += 1
    return f"CX-{n:03d}"


# ── CRUD ─────────────────────────────────────────────────────────────────────

def create_custom_rule(data: dict) -> tuple[bool, str]:
    rules = load_custom_rules()
    rid = data.get("id", "").strip().upper()
    if not rid:
        rid = _next_id(rules)
    if any(r["id"] == rid for r in rules):
        return False, f"Rule ID '{rid}' already exists."
    if not data.get("name", "").strip():
        return False, "Rule name is required."
    if not data.get("patterns"):
        return False, "At least one detection pattern is required."
    if not data.get("remediation", "").strip():
        return False, "Remediation text is required."

    rule = {
        "id":           rid,
        "name":         data["name"].strip(),
        "category":     data.get("category", "CLEAN_CORE"),
        "severity":     data.get("severity", "MEDIUM"),
        "description":  data.get("description", "").strip(),
        "patterns":     [p.strip() for p in data["patterns"] if p.strip()],
        "remediation":  data["remediation"].strip(),
        "example_bad":  data.get("example_bad", "").strip(),
        "example_good": data.get("example_good", "").strip(),
        "cc_level":     data.get("cc_level", ""),
        "s4_impact":    bool(data.get("s4_impact", False)),
        "tags":         [t.strip() for t in data.get("tags", []) if t.strip()],
        "enabled":      bool(data.get("enabled", True)),
        "created_by":   data.get("created_by", "admin"),
    }
    rules.append(rule)
    _save_custom_rules(rules)
    return True, f"Custom rule {rid} created successfully."


def update_custom_rule(rule_id: str, data: dict) -> tuple[bool, str]:
    rules = load_custom_rules()
    for i, r in enumerate(rules):
        if r["id"] == rule_id:
            rules[i].update({
                "name":         data.get("name", r["name"]).strip(),
                "category":     data.get("category", r["category"]),
                "severity":     data.get("severity", r["severity"]),
                "description":  data.get("description", r.get("description", "")).strip(),
                "patterns":     [p.strip() for p in data.get("patterns", r["patterns"]) if p.strip()],
                "remediation":  data.get("remediation", r["remediation"]).strip(),
                "example_bad":  data.get("example_bad", r.get("example_bad", "")).strip(),
                "example_good": data.get("example_good", r.get("example_good", "")).strip(),
                "cc_level":     data.get("cc_level", r.get("cc_level", "")),
                "s4_impact":    bool(data.get("s4_impact", r.get("s4_impact", False))),
                "tags":         [t.strip() for t in data.get("tags", r.get("tags", [])) if t.strip()],
                "enabled":      bool(data.get("enabled", r.get("enabled", True))),
            })
            _save_custom_rules(rules)
            return True, f"Rule {rule_id} updated."
    return False, f"Rule {rule_id} not found."


def delete_custom_rule(rule_id: str) -> tuple[bool, str]:
    rules = load_custom_rules()
    before = len(rules)
    rules = [r for r in rules if r["id"] != rule_id]
    if len(rules) == before:
        return False, f"Rule {rule_id} not found."
    _save_custom_rules(rules)
    return True, f"Rule {rule_id} deleted."


def toggle_custom_rule(rule_id: str, enabled: bool) -> None:
    rules = load_custom_rules()
    for r in rules:
        if r["id"] == rule_id:
            r["enabled"] = enabled
    _save_custom_rules(rules)


# ── Rule objects (used by scan_code) ─────────────────────────────────────────

def get_active_custom_rule_objects():
    """Return enabled custom rules as Rule dataclass instances."""
    from core.abap_rules import Rule
    result = []
    for r in load_custom_rules():
        if not r.get("enabled", True):
            continue
        try:
            result.append(Rule(
                id=r["id"],
                name=r["name"],
                category=r.get("category", "CLEAN_CORE"),
                severity=r.get("severity", "MEDIUM"),
                description=r.get("description", ""),
                patterns=r.get("patterns", []),
                remediation=r.get("remediation", ""),
                example_bad=r.get("example_bad", ""),
                example_good=r.get("example_good", ""),
                cc_level=r.get("cc_level", ""),
                s4_impact=bool(r.get("s4_impact", False)),
                tags=r.get("tags", []),
            ))
        except Exception:
            pass
    return result
