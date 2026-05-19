"""
CoreShift SAP Readiness Check 2 Report Parser
Parses the Excel/CSV report exported from SAP Readiness Check 2
and converts it into structured analysis data.
"""

from __future__ import annotations
import io
import logging
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

SHEET_PRIORITY = [
    "Custom Code",
    "Custom Code Analysis",
    "ABAP",
    "Business Process",
    "Business Scenarios",
    "Simplification Items",
]

SEVERITY_MAP = {
    "E": "CRITICAL",
    "W": "HIGH",
    "I": "MEDIUM",
    "1": "CRITICAL",
    "2": "HIGH",
    "3": "MEDIUM",
    "error":   "CRITICAL",
    "warning": "HIGH",
    "info":    "MEDIUM",
}


@dataclass
class ReadinessItem:
    object_name:    str
    object_type:    str
    severity:       str
    description:    str
    simplification: str = ""
    check_id:       str = ""
    package:        str = ""
    responsible:    str = ""


@dataclass
class ReadinessReport:
    source_file:        str
    total_objects:      int
    critical_count:     int
    high_count:         int
    medium_count:       int
    items:              List[ReadinessItem] = field(default_factory=list)
    summary_text:       str = ""
    available_sheets:   List[str] = field(default_factory=list)

    @property
    def readiness_score(self) -> int:
        if self.total_objects == 0:
            return 100
        penalty = self.critical_count * 20 + self.high_count * 8 + self.medium_count * 3
        return max(0, min(100, 100 - penalty))


def parse_readiness_check(file_bytes: bytes, filename: str) -> ReadinessReport:
    """
    Parse a SAP Readiness Check 2 Excel/CSV export.
    Returns a structured ReadinessReport.
    """
    fname_lower = filename.lower()

    if fname_lower.endswith(".csv"):
        return _parse_csv(file_bytes, filename)
    elif fname_lower.endswith((".xlsx", ".xls")):
        return _parse_excel(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Please upload .xlsx, .xls, or .csv.")


def _parse_excel(file_bytes: bytes, filename: str) -> ReadinessReport:
    try:
        xls = pd.ExcelFile(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Could not open Excel file: {e}")

    available_sheets = xls.sheet_names
    items: List[ReadinessItem] = []

    # Try to find the most relevant sheet
    target_sheet = None
    for priority in SHEET_PRIORITY:
        for sheet in available_sheets:
            if priority.lower() in sheet.lower():
                target_sheet = sheet
                break
        if target_sheet:
            break

    sheets_to_parse = [target_sheet] if target_sheet else available_sheets[:3]

    for sheet in sheets_to_parse:
        try:
            df = xls.parse(sheet, header=None)
            items.extend(_extract_items_from_df(df))
        except Exception as exc:
            logger.debug("Could not parse sheet '%s': %s", sheet, exc)

    return _build_report(items, filename, available_sheets)


def _parse_csv(file_bytes: bytes, filename: str) -> ReadinessReport:
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig", on_bad_lines="skip")
        items = _extract_items_from_df(df)
        return _build_report(items, filename, [])
    except Exception as e:
        raise ValueError(f"Could not parse CSV: {e}")


def _extract_items_from_df(df: pd.DataFrame) -> List[ReadinessItem]:
    items: List[ReadinessItem] = []
    if df.empty:
        return items

    # Normalise column names
    df.columns = [str(c).strip().lower() for c in df.columns]
    col_map = _detect_columns(df.columns.tolist())

    for _, row in df.iterrows():
        try:
            obj_name = str(row.get(col_map.get("object", ""), "")).strip()
            if not obj_name or obj_name in ("nan", "", "Object"):
                continue

            severity_raw = str(row.get(col_map.get("severity", ""), "I")).strip()
            severity = SEVERITY_MAP.get(severity_raw.upper(),
                        SEVERITY_MAP.get(severity_raw.lower(), "MEDIUM"))

            items.append(ReadinessItem(
                object_name=obj_name,
                object_type=str(row.get(col_map.get("type", ""), "PROG")).strip(),
                severity=severity,
                description=str(row.get(col_map.get("description", ""), "")).strip()[:500],
                simplification=str(row.get(col_map.get("simplification", ""), "")).strip()[:200],
                check_id=str(row.get(col_map.get("check_id", ""), "")).strip(),
                package=str(row.get(col_map.get("package", ""), "")).strip(),
            ))
        except Exception:
            continue

    return items


def _detect_columns(cols: List[str]) -> dict:
    """Map logical column names to actual column headers using fuzzy matching."""
    mapping: dict = {}
    patterns = {
        "object":       ["object", "program", "function", "class", "name", "object name"],
        "type":         ["type", "object type", "kind"],
        "severity":     ["severity", "status", "prio", "priority", "level", "message type"],
        "description":  ["description", "message", "text", "detail", "check text"],
        "simplification": ["simplification", "simplification item", "sl item"],
        "check_id":     ["check id", "check", "id", "key"],
        "package":      ["package", "devclass", "development class"],
    }
    for logical, keywords in patterns.items():
        for kw in keywords:
            match = next((c for c in cols if kw in c), None)
            if match:
                mapping[logical] = match
                break
    return mapping


def _build_report(items: List[ReadinessItem], filename: str,
                  available_sheets: List[str]) -> ReadinessReport:
    critical = sum(1 for i in items if i.severity == "CRITICAL")
    high     = sum(1 for i in items if i.severity == "HIGH")
    medium   = sum(1 for i in items if i.severity == "MEDIUM")

    summary = (
        f"Parsed {len(items)} objects from '{filename}'. "
        f"Critical: {critical}, High: {high}, Medium: {medium}."
    )

    return ReadinessReport(
        source_file=filename,
        total_objects=len(items),
        critical_count=critical,
        high_count=high,
        medium_count=medium,
        items=items,
        summary_text=summary,
        available_sheets=available_sheets,
    )
