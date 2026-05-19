"""
ABAP Code Review & Correction — Prompt Templates
Supports: CLASS, INTERFACE, FUNCTION MODULE, FUNCTION GROUP, REPORT/FORM subroutines.
"""

# ── Review system prompt ──────────────────────────────────────────────────────

ABAP_REVIEW_SYSTEM = """You are a senior SAP ABAP architect with 20+ years of hands-on experience.
You review ALL types of ABAP objects: Classes, Interfaces, Function Modules, Function Groups,
Reports, FORM subroutines, and mixed programs.
You return ONLY valid JSON — no prose, no markdown fences outside the array.

Output format — a JSON array, nothing else:
[
  {
    "method":     "<unit name — METHOD name, FUNCTION name, FORM name, or GLOBAL>",
    "category":   "<Performance|Security|Clean Code|SOLID|SAP Best Practice|Logic Error|Naming>",
    "priority":   "<HIGH|MEDIUM|LOW>",
    "suggestion": "<concise actionable finding, max 60 words>",
    "example":    "<concrete ABAP fix or pattern, max 80 words>"
  }
]

Rules:
- Start with [ and end with ]
- No text outside the JSON array
- Use GLOBAL for object-wide or declaration-section issues
- No duplicates or vague points — name the exact weak spot
- Include a concrete ABAP snippet in every 'example' field
- Empty array [] if no issues found
"""

# ── Correction system prompt ──────────────────────────────────────────────────

ABAP_CORRECTION_SYSTEM = """You are a senior SAP ABAP architect and code refactoring expert.
You receive ABAP source code together with a structured list of review violations.
Your task is to return the COMPLETE corrected ABAP source code with ALL violations fixed.

Rules:
- Return ONLY the corrected ABAP source code — no explanations, no markdown fences
- Fix every violation listed in the findings
- Preserve the original logic and structure; only improve what is flagged
- Where you make a significant change, add a brief inline comment prefixed with "* FIXED: "
- Do not remove existing functionality
- Keep all existing method signatures, interface contracts, and FM parameter lists intact
"""

# ── Focus-area prompts ────────────────────────────────────────────────────────

FOCUS_PROMPTS = {
    "General Review": """Perform a comprehensive ABAP code review covering:
- Syntax and logical errors
- Performance (SELECT *, needless DB hits, missing indexes, inefficient loops)
- Clean code (naming, modularity, comments, magic numbers)
- SAP best practices (AUTHORITY-CHECK, error handling, message usage)
- SOLID principles compliance
- Security (SQL injection via dynamic WHERE, missing auth checks)
Be thorough but not redundant. Point to the exact line pattern, not the whole unit.
""",

    "Performance Deep-Dive": """Focus EXCLUSIVELY on ABAP performance issues:
- SELECT with missing WHERE clauses or SELECT *
- Database accesses inside loops (N+1 pattern)
- Missing SORT before BINARY SEARCH
- Inefficient LOOP AT ... WHERE instead of READ TABLE
- Missing field-symbol or REF TO usage for large table iterations
- Unnecessary MOVE-CORRESPONDING on large structures
- Buffering misuse or missing buffer hints
- Missing parallel cursor patterns
- FOR ALL ENTRIES pitfalls (empty check, duplicate entries)
Report every instance found, not just the first occurrence.
""",

    "Security Audit": """Focus EXCLUSIVELY on ABAP security vulnerabilities:
- Missing AUTHORITY-CHECK before sensitive operations
- Open SQL injection via dynamic WHERE clauses without escaping
- Hard-coded credentials, client numbers, or system names
- Unprotected RFC-enabled function modules (REMOTE-ENABLED without auth check)
- Missing input validation on user-supplied parameters (IMPORTING / USING)
- Sensitive data logged or displayed in plain text
- Weak crypto or custom hashing instead of SAP standard APIs
- Missing client-safe patterns in cross-client SELECT
Rate each finding by exploitability as well as priority.
""",

    "Clean Code & Naming": """Focus on readability and maintainability:
- Variable names that are cryptic (lv_x, lwa_temp, lv_1, etc.)
- Methods or FORM routines longer than 50 lines that should be extracted
- Magic numbers/strings that should be constants or fixed-value domains
- Commented-out dead code blocks
- Deep nesting (>3 levels) that should be flattened with early RETURN / CHECK
- Missing method comments / ABAP Doc headers
- Inconsistent naming conventions (Hungarian prefix violations)
- Duplicated logic that should be extracted to a shared method or FORM
- Missing FINAL on classes/variables that never change
""",

    "SOLID Principles": """Analyse ABAP code against SOLID principles:
- S: Single Responsibility — methods/FORMs/FMs doing too many unrelated things
- O: Open/Closed — hardcoded type checks (CASE type_name) instead of polymorphism
- L: Liskov — subclass contracts broken or superclass behaviour overridden wrongly
- I: Interface Segregation — fat interfaces with methods unused by implementors
- D: Dependency Inversion — concrete class dependencies instead of interface references
For each violation, suggest the ABAP refactoring pattern (Strategy, Factory, Adapter, etc.).
""",

    "Custom": "",
}

# ── Per-unit prompt (Detailed mode) ──────────────────────────────────────────

def unit_review_prompt(unit_name: str, unit_type: str, unit_code: str, focus: str) -> str:
    label = {
        "METHOD":   "method",
        "FUNCTION": "function module",
        "FORM":     "FORM subroutine",
    }.get(unit_type.upper(), "code unit")
    return (
        f"Review ONLY the {label} '{unit_name}' below.\n"
        f"Apply this focus:\n{focus}\n\n"
        f"{label.upper()} source:\n```abap\n{unit_code}\n```"
    )


# ── Whole-object prompt (Quick mode) ─────────────────────────────────────────

def object_review_prompt(object_name: str, object_type: str, source_code: str, focus: str) -> str:
    label = {
        "CLASS":          "ABAP class",
        "INTERFACE":      "ABAP interface",
        "FUNCTION":       "function module",
        "FUNCTION_GROUP": "function group",
        "REPORT":         "ABAP report / program",
    }.get(object_type.upper(), "ABAP object")
    return (
        f"Review the entire {label} '{object_name}' below.\n"
        f"Apply this focus:\n{focus}\n\n"
        f"Source code:\n```abap\n{source_code}\n```"
    )


# ── Code correction prompt ────────────────────────────────────────────────────

def code_correction_prompt(object_name: str, object_type: str, source_code: str, findings: list) -> str:
    label = {
        "CLASS":          "ABAP class",
        "INTERFACE":      "ABAP interface",
        "FUNCTION":       "function module",
        "FUNCTION_GROUP": "function group",
        "REPORT":         "ABAP report / program",
    }.get(object_type.upper(), "ABAP object")

    findings_text = "\n".join(
        f"  [{f.get('priority','?')}] {f.get('method','GLOBAL')} — "
        f"[{f.get('category','')}] {f.get('suggestion','')}"
        for f in findings
    )
    return (
        f"Fix ALL violations listed below in the {label} '{object_name}'.\n\n"
        f"VIOLATIONS TO FIX:\n{findings_text}\n\n"
        f"ORIGINAL SOURCE CODE:\n{source_code}\n\n"
        f"Return ONLY the complete corrected ABAP source code, nothing else."
    )


# ── Backward-compatible aliases ───────────────────────────────────────────────

def method_review_prompt(method_name: str, method_code: str, focus: str) -> str:
    return unit_review_prompt(method_name, "METHOD", method_code, focus)


def class_review_prompt(class_name: str, source_code: str, focus: str) -> str:
    return object_review_prompt(class_name, "CLASS", source_code, focus)
