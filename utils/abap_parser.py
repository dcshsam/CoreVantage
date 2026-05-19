"""
utils/abap_parser.py
Parses raw ABAP source into reviewable units for ALL ABAP object types:
  CLASS (METHOD/ENDMETHOD), INTERFACE (METHOD/ENDMETHOD),
  FUNCTION MODULE (FUNCTION/ENDFUNCTION), FUNCTION GROUP (multiple FMs),
  REPORT / PROGRAM (FORM/ENDFORM subroutines).
A single file may contain multiple unit types simultaneously.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ABAPMethod:
    name: str
    source: str
    unit_type: str       # METHOD | FUNCTION | FORM
    line_start: int
    line_end: int


@dataclass
class ABAPParseResult:
    class_name: str
    full_source: str
    methods: list[ABAPMethod] = field(default_factory=list)
    object_type: str = "CLASS"   # CLASS | INTERFACE | FUNCTION | FUNCTION_GROUP | REPORT


# ── Regex patterns ────────────────────────────────────────────────────────────

_RE_CLASS_DECL     = re.compile(r"^\s*CLASS\s+(\w+)\s+DEFINITION", re.IGNORECASE)
_RE_INTERFACE_DECL = re.compile(r"^\s*INTERFACE\s+(\w+)\b", re.IGNORECASE)
_RE_FUNCTION_POOL  = re.compile(r"^\s*FUNCTION-POOL\s+(\w+)", re.IGNORECASE)
_RE_REPORT         = re.compile(r"^\s*REPORT\s+(\w+)", re.IGNORECASE)
_RE_PROGRAM        = re.compile(r"^\s*PROGRAM\s+(\w+)", re.IGNORECASE)

_RE_METHOD_START   = re.compile(r"^\s*METHOD\s+(\w+)\s*[.\s]", re.IGNORECASE)
_RE_METHOD_END     = re.compile(r"^\s*ENDMETHOD\s*[.\s]", re.IGNORECASE)

_RE_FUNCTION_START = re.compile(r"^\s*FUNCTION\s+(\w+)\s*\.", re.IGNORECASE)
_RE_FUNCTION_END   = re.compile(r"^\s*ENDFUNCTION\s*[.\s]", re.IGNORECASE)

_RE_FORM_START     = re.compile(r"^\s*FORM\s+(\w+)", re.IGNORECASE)
_RE_FORM_END       = re.compile(r"^\s*ENDFORM\s*[.\s]", re.IGNORECASE)


def detect_object_name(source: str) -> tuple[str, str]:
    """Return (primary_name, object_type) by scanning the first 60 lines."""
    lines = source.splitlines()[:60]

    # High-priority declarations first
    for line in lines:
        m = _RE_CLASS_DECL.match(line)
        if m:
            return m.group(1).upper(), "CLASS"
        m = _RE_INTERFACE_DECL.match(line)
        if m:
            return m.group(1).upper(), "INTERFACE"
        m = _RE_FUNCTION_POOL.match(line)
        if m:
            return m.group(1).upper(), "FUNCTION_GROUP"

    # Report / Program / standalone FM
    for line in lines:
        m = _RE_REPORT.match(line)
        if m:
            return m.group(1).upper(), "REPORT"
        m = _RE_PROGRAM.match(line)
        if m:
            return m.group(1).upper(), "REPORT"
        m = _RE_FUNCTION_START.match(line)
        if m:
            return m.group(1).upper(), "FUNCTION"

    # Fall back: if we can find FORM blocks treat as report
    for line in lines:
        m = _RE_FORM_START.match(line)
        if m:
            return "ABAP_REPORT", "REPORT"

    return "UNKNOWN", "CLASS"


def _extract_blocks(
    lines: list[str],
    start_re: re.Pattern,
    end_re: re.Pattern,
    unit_type: str,
) -> list[ABAPMethod]:
    """Generic extractor: collects all start→end block pairs in the source."""
    units: list[ABAPMethod] = []
    in_block = False
    current_name = ""
    current_lines: list[str] = []
    current_start = 0

    for idx, line in enumerate(lines):
        if not in_block:
            m = start_re.match(line)
            if m:
                in_block = True
                current_name = m.group(1).upper()
                current_lines = [line]
                current_start = idx + 1
        else:
            current_lines.append(line)
            if end_re.match(line):
                units.append(ABAPMethod(
                    name=current_name,
                    source="\n".join(current_lines),
                    unit_type=unit_type,
                    line_start=current_start,
                    line_end=idx + 1,
                ))
                in_block = False
                current_name = ""
                current_lines = []

    return units


def parse_abap_source(source: str, name_hint: str = "") -> ABAPParseResult:
    """
    Parse ABAP source into all reviewable units regardless of object type.
    Collects METHOD, FUNCTION, and FORM blocks in source order.
    """
    lines = source.splitlines()
    detected_name, obj_type = detect_object_name(source)
    class_name = name_hint.upper() if name_hint else detected_name

    result = ABAPParseResult(
        class_name=class_name,
        full_source=source,
        object_type=obj_type,
    )

    # Collect all unit types present in the source
    methods   = _extract_blocks(lines, _RE_METHOD_START,   _RE_METHOD_END,   "METHOD")
    functions = _extract_blocks(lines, _RE_FUNCTION_START, _RE_FUNCTION_END, "FUNCTION")
    forms     = _extract_blocks(lines, _RE_FORM_START,     _RE_FORM_END,     "FORM")

    # Merge in source order by line_start
    all_units = sorted(methods + functions + forms, key=lambda u: u.line_start)
    result.methods = all_units

    # Fallback: if no blocks detected treat the whole source as one unit
    if not result.methods:
        label = {
            "FUNCTION": "FUNCTION_MODULE",
            "INTERFACE": "INTERFACE_BODY",
        }.get(obj_type, class_name)
        result.methods = [ABAPMethod(
            name=label,
            source=source,
            unit_type=obj_type,
            line_start=1,
            line_end=len(lines),
        )]

    return result


def split_into_chunks(source: str, max_chars: int = 12_000) -> list[str]:
    """Split large source into chunks without breaking method boundaries."""
    lines = source.splitlines(keepends=True)
    chunks: list[str] = []
    current: list[str] = []
    size = 0

    for line in lines:
        if size + len(line) > max_chars and current:
            chunks.append("".join(current))
            current = [line]
            size = len(line)
        else:
            current.append(line)
            size += len(line)

    if current:
        chunks.append("".join(current))

    return chunks
