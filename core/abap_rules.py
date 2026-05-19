"""
CoreShift ABAP Rules Engine
35+ rules covering Clean Core compliance, ECC→S/4 migration,
security vulnerabilities, and performance anti-patterns.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional

# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Rule:
    id:           str
    name:         str
    category:     str       # CLEAN_CORE | S4_MIGRATION | SECURITY | PERFORMANCE
    severity:     str       # CRITICAL | HIGH | MEDIUM | LOW | INFO
    description:  str
    patterns:     List[str]
    remediation:  str
    example_bad:  str = ""
    example_good: str = ""
    # Clean Core maturity level impact (D = worst, A = compliant)
    cc_level:     str = ""  # D, C, B, A or "" if not applicable
    s4_impact:    bool = False
    tags:         List[str] = field(default_factory=list)


@dataclass
class Violation:
    rule:         Rule
    line_number:  int
    line_content: str
    context:      str = ""  # surrounding lines for display

    @property
    def rule_id(self): return self.rule.id
    @property
    def severity(self): return self.rule.severity
    @property
    def category(self): return self.rule.category
    @property
    def description(self): return self.rule.description
    @property
    def remediation(self): return self.rule.remediation
    @property
    def s4_impact(self): return self.rule.s4_impact
    @property
    def cc_level(self): return self.rule.cc_level


# ── Severity ordering ─────────────────────────────────────────────────────────
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
SEVERITY_COLORS = {
    "CRITICAL": "#BB0000",
    "HIGH":     "#E9730C",
    "MEDIUM":   "#C87400",
    "LOW":      "#0070F2",
    "INFO":     "#6D6D6D",
}
SEVERITY_BG = {
    "CRITICAL": "#FFEAEA",
    "HIGH":     "#FFF3EA",
    "MEDIUM":   "#FFF8E0",
    "LOW":      "#E8F4FF",
    "INFO":     "#F5F5F5",
}

# ── Ruleset ───────────────────────────────────────────────────────────────────

ALL_RULES: List[Rule] = [

    # ── CLEAN CORE RULES ─────────────────────────────────────────────────────

    Rule(
        id="CC-001",
        name="Direct Access to SAP Standard Tables",
        category="CLEAN_CORE",
        severity="HIGH",
        cc_level="D",
        description="SELECT/INSERT/UPDATE/DELETE directly on SAP standard tables bypasses the official API layer and creates upgrade risks. "
                    "SAP can change table structures (e.g. MATNR field grew to 40 chars in S/4HANA 2023) or replace tables with views during releases, breaking custom code. "
                    "ATC CLOUD_READINESS check will flag this as a Level D violation.",
        patterns=[
            r'\bSELECT\b.*\bFROM\s+(MARA|MARM|MARC|MVKE|MAKT|MLAN|MBEW|'
            r'EKKO|EKPO|EKET|EKES|EKBE|'
            r'BKPF|BSEG|BSAK|BSIK|BSAS|BSIS|'
            r'VBAK|VBAP|VBEP|VBKD|VBPA|VBFA|VBRK|VBRP|'
            r'KNA1|KNB1|KNVV|LFA1|LFB1|'
            r'T001|T001W|CSKS|CSKA|CSKB)\b',
            r'\b(INSERT|UPDATE|DELETE|MODIFY)\s+(?:INTO\s+)?(MARA|MARM|MARC|EKKO|EKPO|BKPF|BSEG|VBAK|VBAP|KNA1|LFA1|T001)\b',
        ],
        remediation="Replace direct table access with released SAP APIs (Level A target): "
                    "(1) BAPIs: BAPI_MATERIAL_*, BAPI_ACC_*, BAPI_SALESORDER_* for writes. "
                    "(2) CDS I_* views (e.g. I_SalesOrder, I_MaterialStock) for reads — these are upgrade-safe released APIs. "
                    "(3) RAP Entity Manipulation Language (EML) for transactional write scenarios. "
                    "Check api.sap.com SAP Business Accelerator Hub for the released API covering your business object.",
        example_bad="SELECT * FROM MARA WHERE MATNR = lv_matnr.",
        example_good="\" Option 1 – BAPI (Level B)\nCALL FUNCTION 'BAPI_MATERIAL_GET_DETAIL' EXPORTING MATERIAL = lv_matnr.\n\" Option 2 – CDS view (Level A)\nSELECT SINGLE material, materialname FROM i_product WHERE material = @lv_matnr INTO @DATA(ls_mat).",
        tags=["database", "api", "upgrade-risk", "level-d"],
    ),

    Rule(
        id="CC-002",
        name="Native SQL (EXEC SQL)",
        category="CLEAN_CORE",
        severity="CRITICAL",
        cc_level="D",
        description="EXEC SQL bypasses Open SQL optimisations, buffering, and database independence. "
                    "Not supported in SAP HANA-native scenarios and creates database portability issues.",
        patterns=[r'\bEXEC\s+SQL\b', r'\bNATIVE\s+SQL\b', r'\bENDEXEC\b'],
        remediation="Replace with Open SQL. Use ADBC (ABAP Database Connectivity) only when truly necessary for HANA-specific features.",
        example_bad="EXEC SQL.\n  SELECT * INTO :lt_data FROM MARA\nENDEXEC.",
        example_good="SELECT * FROM MARA INTO TABLE @DATA(lt_data).",
        tags=["database", "native-sql", "portability"],
    ),

    Rule(
        id="CC-003",
        name="Hardcoded SAP Client",
        category="CLEAN_CORE",
        severity="HIGH",
        cc_level="C",
        description="Hardcoded client numbers (000, 100, 200, etc.) make code non-portable across landscapes "
                    "and can cause security issues in multi-client systems.",
        patterns=[
            r'\bCLIENT\s*=\s*[\'"]?\d{3}[\'"]?',
            r"'[0-9]{3}'\s*\.\s*\"client",
            r'\bSY-MANDT\b.*=\s*[\'\"]\d{3}[\'\"]',
        ],
        remediation="Remove client specifications and let ABAP use the current client (SY-MANDT) automatically, "
                    "or use CROSS-CLIENT ACCESS only when genuinely required.",
        example_bad="SELECT * FROM T001 CLIENT SPECIFIED WHERE MANDT = '100'.",
        example_good="SELECT * FROM T001 WHERE BUKRS = lv_bukrs.",
        tags=["security", "portability", "client"],
    ),

    Rule(
        id="CC-004",
        name="SELECT * (All Columns)",
        category="CLEAN_CORE",
        severity="MEDIUM",
        cc_level="C",
        description="SELECT * fetches unnecessary columns, wastes network bandwidth, memory, and prevents "
                    "database query optimisation. Clean Core requires explicit field lists.",
        patterns=[r'\bSELECT\s+\*\s+FROM\b'],
        remediation="Specify only the fields you need. Use FIELDS addition or inline SELECT with explicit column list.",
        example_bad="SELECT * FROM VBAK INTO TABLE lt_orders.",
        example_good="SELECT vbeln, erdat, netwr FROM vbak INTO TABLE @DATA(lt_orders).",
        tags=["performance", "database"],
    ),

    Rule(
        id="CC-005",
        name="SELECT Inside LOOP (N+1 Problem)",
        category="CLEAN_CORE",
        severity="HIGH",
        cc_level="C",
        description="Database SELECT inside a LOOP creates N+1 round trips to the database — "
                    "a critical performance anti-pattern that degrades with data volume.",
        patterns=[
            r'(?:LOOP\s+AT\s+\w+[\s\S]{0,200}?SELECT)|(?:SELECT[\s\S]{0,200}?LOOP\s+AT)',
        ],
        remediation="Move SELECT outside the LOOP. Use FOR ALL ENTRIES IN or JOIN to fetch all needed data in one query.",
        example_bad="LOOP AT lt_orders INTO ls_order.\n  SELECT * FROM VBAP WHERE VBELN = ls_order-vbeln.\nENDLOOP.",
        example_good="SELECT vbeln, posnr, netwr FROM vbap\n  FOR ALL ENTRIES IN @lt_orders\n  WHERE vbeln = @lt_orders-vbeln\n  INTO TABLE @DATA(lt_items).",
        tags=["performance", "database", "n+1"],
    ),

    Rule(
        id="CC-006",
        name="FORM Subroutines (Obsolete Procedural Programming)",
        category="CLEAN_CORE",
        severity="MEDIUM",
        cc_level="C",
        description="FORM/ENDFORM subroutines are an obsolete procedural concept. SAP Clean Core requires "
                    "ABAP Objects (methods) for all new development. PERFORM is also deprecated. "
                    "In ABAP Cloud (BTP ABAP), FORM routines are syntax-restricted and will not compile.",
        patterns=[r'^\s*FORM\s+\w+', r'^\s*PERFORM\s+\w+'],
        remediation="Replace FORM subroutines with class static methods or instance methods. "
                    "For RAP scenarios, implement logic inside the behavior implementation class (CCIMP include). "
                    "For standalone utilities, create a global function group-free class ZCL_<DOMAIN>_UTILITY.",
        example_bad="FORM calculate_total USING iv_amount TYPE p CHANGING ev_total TYPE p.\n  \" logic\nENDFORM.",
        example_good="CLASS lcl_calculator DEFINITION.\n  PUBLIC SECTION.\n    CLASS-METHODS calculate_total\n      IMPORTING iv_amount TYPE p\n      RETURNING VALUE(rv_total) TYPE p.\nENDCLASS.\nCLASS lcl_calculator IMPLEMENTATION.\n  METHOD calculate_total.\n    rv_total = iv_amount * 1.19.\n  ENDMETHOD.\nENDCLASS.",
        tags=["clean-code", "abap-objects", "modern-abap", "abap-cloud"],
    ),

    Rule(
        id="CC-007",
        name="MESSAGE Statement (Non-Exception Based Error Handling)",
        category="CLEAN_CORE",
        severity="MEDIUM",
        cc_level="C",
        description="The MESSAGE statement is UI-layer dependent and cannot be used in APIs, background jobs, "
                    "or service layers. Clean Core requires exception-class-based error handling.",
        patterns=[
            r'\bMESSAGE\s+[A-Z]\d+\s*\(',
            r'\bMESSAGE\s+(?:TYPE\s+)?[\'\"]*[EAWIX][\'\"]*',
        ],
        remediation="Replace MESSAGE with RAISE EXCEPTION TYPE cx_<your_exception>. "
                    "Create custom exception classes inheriting from CX_STATIC_CHECK or CX_DYNAMIC_CHECK.",
        example_bad="MESSAGE e001(zmy_msg) WITH lv_detail.",
        example_good="RAISE EXCEPTION TYPE zcx_my_error\n  EXPORTING\n    textid  = zcx_my_error=>invalid_input\n    detail  = lv_detail.",
        tags=["error-handling", "exceptions", "api-readiness"],
    ),

    Rule(
        id="CC-008",
        name="Missing AUTHORITY-CHECK",
        category="CLEAN_CORE",
        severity="HIGH",
        cc_level="C",
        description="Programs that read or modify sensitive business data without AUTHORITY-CHECK "
                    "bypass SAP's authorization concept, violating Clean Core security requirements.",
        patterns=[
            r'\bCALL\s+TRANSACTION\b(?!.*AUTHORITY-CHECK)',
            r'\bSUBMIT\s+\w+(?!.*AUTHORITY-CHECK)',
        ],
        remediation="Add AUTHORITY-CHECK OBJECT before sensitive operations. "
                    "Use CHECK sy-subrc = 0 after each authority check.",
        example_bad="CALL TRANSACTION 'FB01'.",
        example_good="AUTHORITY-CHECK OBJECT 'F_BKPF_BUK'\n  ID 'BUKRS' FIELD lv_bukrs\n  ID 'ACTVT' FIELD '01'.\nIF sy-subrc <> 0.\n  RAISE EXCEPTION TYPE zcx_not_authorized.\nENDIF.\nCALL TRANSACTION 'FB01'.",
        tags=["security", "authorization", "compliance"],
    ),

    Rule(
        id="CC-009",
        name="Direct Modification of SAP Standard Objects",
        category="CLEAN_CORE",
        severity="CRITICAL",
        cc_level="D",
        description="Modifying standard SAP repository objects (programs in SAP namespace) "
                    "is the #1 upgrade blocker and a Level D Clean Core violation. "
                    "These modifications are overwritten during upgrades and cannot be deployed in S/4HANA Cloud. "
                    "SAP Joule AI (S/4HANA 2025) can suggest RAP-based replacements for common modification patterns.",
        patterns=[
            r'^\s*MODIFICATION\s+ID\b',
            r'\bCLASS\s+(?:SAP|CL_|IF_)\w+\s+IMPLEMENTATION\b.*?MODIFICATION',
        ],
        remediation="Replace modifications with SAP-compliant Clean Core extension techniques (Level A target): "
                    "(1) RAP BAdIs — the strategic replacement for all enhancement needs in S/4HANA. "
                    "(2) Explicit enhancement spots (ENHANCEMENT-POINT / ENHANCEMENT-SECTION). "
                    "(3) BTE (Business Transaction Events) for FI/CO scenarios. "
                    "Find available BAdIs via SE18 or the SAP Business Accelerator Hub (api.sap.com → On-Stack Extensibility). "
                    "If no BAdI exists, raise an SAP Influence Request — SAP is rapidly releasing new extension points.",
        example_bad="\" Direct modification — overwrites on every upgrade\nCLASS cl_sd_pric_condition IMPLEMENTATION.\n  METHOD calculate.  \" SAP code modified here\nENDCLASS.",
        example_good="\" RAP BAdI implementation — upgrade-safe Level A extension\nCLASS zcl_sd_pric_badi_impl DEFINITION FINAL.\n  PUBLIC SECTION.\n    INTERFACES if_ex_pricing_badi.\nENDCLASS.\nCLASS zcl_sd_pric_badi_impl IMPLEMENTATION.\n  METHOD if_ex_pricing_badi~calculate.\n    \" Custom pricing logic here\n  ENDMETHOD.\nENDCLASS.",
        tags=["modification", "upgrade-risk", "extensions", "level-d", "badi"],
    ),

    Rule(
        id="CC-010",
        name="Classic Dynpro Screen Programming",
        category="CLEAN_CORE",
        severity="HIGH",
        cc_level="D",
        description="Classic ABAP dynpro screens (CALL SCREEN, MODULE, AT SELECTION-SCREEN) "
                    "cannot run in SAP BTP and block the path to Clean Core. SAP Fiori/UI5 is the strategic UI.",
        patterns=[
            r'\bCALL\s+SCREEN\s+\d+',
            r'^\s*MODULE\s+\w+\s+(?:INPUT|OUTPUT)',
            r'\bSET\s+SCREEN\s+\d+',
            r'\bLEAVE\s+TO\s+SCREEN\b',
        ],
        remediation="Migrate to SAP Fiori/UI5 OData services, or use CL_SALV_TABLE for ALV-based output "
                    "without custom dynpro screens.",
        example_bad="CALL SCREEN 0100.",
        example_good="\" Use Fiori app or SALV framework\ncl_salv_table=>factory( IMPORTING r_salv_table = lo_alv\n  CHANGING t_table = lt_data ).\nlo_alv->display( ).",
        tags=["ui", "fiori", "dynpro", "btp-ready"],
    ),

    Rule(
        id="CC-011",
        name="CONCATENATE Statement (Obsolete String Operation)",
        category="CLEAN_CORE",
        severity="LOW",
        cc_level="B",
        description="CONCATENATE is an obsolete statement replaced by modern string expressions "
                    "in ABAP 7.4+. Modern syntax is more readable and type-safe.",
        patterns=[r'^\s*CONCATENATE\b'],
        remediation="Replace CONCATENATE with string template literals: lv_str = |{ lv_a }{ lv_b }|.",
        example_bad="CONCATENATE lv_first ' ' lv_last INTO lv_name.",
        example_good="DATA(lv_name) = |{ lv_first } { lv_last }|.",
        tags=["modern-abap", "syntax", "readability"],
    ),

    Rule(
        id="CC-012",
        name="MOVE-CORRESPONDING (Implicit Field Mapping)",
        category="CLEAN_CORE",
        severity="LOW",
        cc_level="B",
        description="MOVE-CORRESPONDING with implicit field mapping makes code fragile when structures change. "
                    "Adding a field to a structure silently causes unintended data movement.",
        patterns=[r'\bMOVE-CORRESPONDING\b'],
        remediation="Use explicit field assignments or CORRESPONDING #( ) with MAPPING/EXCEPT additions "
                    "to document intent explicitly.",
        example_bad="MOVE-CORRESPONDING ls_source TO ls_target.",
        example_good="ls_target = CORRESPONDING #( ls_source MAPPING bukrs = kompany_code ).",
        tags=["modern-abap", "data-mapping", "readability"],
    ),

    Rule(
        id="CC-013",
        name="Dynamic SQL Without Input Sanitisation",
        category="CLEAN_CORE",
        severity="CRITICAL",
        cc_level="D",
        description="Dynamic Open SQL with unsanitised user input creates ABAP injection vulnerabilities "
                    "(analogous to SQL injection). CWE-89 / SAP Security Note 1520747.",
        patterns=[
            r'\bSELECT\b.*\bWHERE\b.*\(?.*&\s*lv_',
            r'cl_abap_dyn_prog=>(?!check_whitelist|escape)',
            r'\(.*\)\s*=\s*lv_\w+\s*\.\s*\"?\s*dynamic',
        ],
        remediation="Always validate/whitelist dynamic table and field names using CL_ABAP_DYN_PROG=>CHECK_WHITELIST_TAB "
                    "or CL_ABAP_DYN_PROG=>ESCAPE_QUOTES. Never concatenate user input directly into WHERE clauses.",
        example_bad="SELECT * FROM (lv_tabname) INTO TABLE lt_data WHERE (lv_where).",
        example_good="cl_abap_dyn_prog=>check_whitelist_tab(\n  val           = lv_tabname\n  whitelist_tab = lt_allowed_tables ).\nSELECT * FROM (lv_tabname) INTO TABLE @DATA(lt_data).",
        tags=["security", "injection", "owasp"],
    ),

    Rule(
        id="CC-014",
        name="Hardcoded Text Literals",
        category="CLEAN_CORE",
        severity="LOW",
        cc_level="B",
        description="Hardcoded text literals in ABAP code prevent translation and make maintenance harder. "
                    "SAP requires text elements or message classes for all user-visible texts.",
        patterns=[
            r"(?:WRITE|MESSAGE)\s+['\"][A-Za-z]{5,}",
            r"(?:FORMAT|WRITE)\s+.*['\"][A-Z][a-z]{4,}",
        ],
        remediation="Move text literals to text elements (Text tab in SE38) or message classes. "
                    "Use TEXT-001, MESSAGE i001(zmy_msg), or string templates with translatable text.",
        example_bad="WRITE: 'Processing complete, please check the results'.",
        example_good="WRITE: TEXT-001.  \" Translatable text element",
        tags=["i18n", "translation", "ui"],
    ),

    # ── S/4HANA MIGRATION RULES ───────────────────────────────────────────────

    Rule(
        id="S4-001",
        name="SAP Logical Database (Deprecated in S/4HANA)",
        category="S4_MIGRATION",
        severity="HIGH",
        cc_level="D",
        s4_impact=True,
        description="Logical Databases (LDB) are deprecated in SAP S/4HANA. "
                    "Programs using LDB will not work as expected and must be rewritten. "
                    "In ABAP Cloud (BTP/S/4HANA Cloud), LOGICAL DATABASE syntax is forbidden. "
                    "LDBs also hide the authorization check — replace it explicitly.",
        patterns=[
            r'LOGICAL\s+DATABASE\s+\w+',
            r'^\s*NODES\s*:',
            r'^\s*GET\s+\w+\.',
        ],
        remediation="Replace LDB with ABAP SQL push-down pattern using CDS views and ABAP HANA features: "
                    "(1) Write an I_ CDS view (or a custom CDS view) that joins the same tables the LDB traversed. "
                    "(2) Use ABAP SQL SELECT on the CDS view instead of LDB nodes. "
                    "(3) Add explicit AUTHORITY-CHECK OBJECT statements for every authorization object the LDB previously checked automatically. "
                    "For FI/CO reports, use CDS views I_JournalEntry, I_PurchaseOrder, etc. from the SAP Business Accelerator Hub.",
        example_bad="REPORT zmy_report.\nLOGICAL DATABASE F1L.\nNODES: bkpf, bseg.\nGET bkpf. WRITE bkpf-belnr.",
        example_good="\" CDS-based replacement\nSELECT belnr, bukrs, bldat, waers\n  FROM i_journalentry\n  WHERE companycode = @lv_bukrs\n  INTO TABLE @DATA(lt_entries).\nAUTHORITY-CHECK OBJECT 'F_BKPF_BUK' ID 'BUKRS' FIELD lv_bukrs ID 'ACTVT' FIELD '03'.\nIF sy-subrc <> 0. RAISE EXCEPTION TYPE zcx_not_authorized. ENDIF.",
        tags=["ldb", "deprecated", "s4-blocker", "cds", "push-down"],
    ),

    Rule(
        id="S4-002",
        name="Classic BDC (Batch Data Communication)",
        category="S4_MIGRATION",
        severity="HIGH",
        cc_level="D",
        s4_impact=True,
        description="Classic BDC recordings are fragile, GUI-dependent, and unreliable in S/4HANA "
                    "where screen layouts may have changed. They are not supported via Fiori or BTP. "
                    "BDC screen sequences break silently after UI changes or S/4HANA simplifications.",
        patterns=[
            r'\bPERFORM\s+bdc_dynpro\b',
            r'\bPERFORM\s+bdc_field\b',
            r'\bCALL\s+TRANSACTION\b.*\bUSING\b.*\bMODE\b',
            r'\bDATA\s+bdcdata',
            r'\bTABLES\s+bdcdata',
        ],
        remediation="Replace BDC with stable, API-based alternatives: "
                    "(1) BAPIs — e.g. BAPI_SALESORDER_CREATEFROMDAT2, BAPI_PO_CREATE1, BAPI_ACC_DOCUMENT_POST. "
                    "(2) RAP EML (Entity Manipulation Language) — the strategic S/4HANA Cloud approach: "
                    "MODIFY ENTITY <entity_name> CREATE FIELDS ( ) WITH VALUE #( ... ). "
                    "(3) IDoc mass processing for high-volume data loads. "
                    "Check api.sap.com Business Accelerator Hub for the BAPI or RAP BO covering your transaction.",
        example_bad="CALL TRANSACTION 'VA01' USING lt_bdcdata MODE 'N' UPDATE 'S'.",
        example_good="\" BAPI replacement (Level B)\nCALL FUNCTION 'BAPI_SALESORDER_CREATEFROMDAT2'\n  EXPORTING order_header_in = ls_header\n  TABLES return = lt_return.\nCALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = abap_true.\n\" RAP EML replacement (Level A)\nMODIFY ENTITY i_salesordertp CREATE\n  FIELDS ( soldtoparty ) WITH VALUE #( ( %cid = '1' soldtoparty = lv_kunnr ) )\n  MAPPED DATA(ls_mapped) FAILED DATA(ls_failed) REPORTED DATA(ls_reported).",
        tags=["bdc", "transaction", "s4-migration", "eml", "rap"],
    ),

    Rule(
        id="S4-003",
        name="SAP Script Forms (Deprecated Print Forms)",
        category="S4_MIGRATION",
        severity="MEDIUM",
        cc_level="C",
        s4_impact=True,
        description="SAP Script (SSF_FUNCTION_MODULE_NAME, OPEN_FORM, WRITE_FORM, CLOSE_FORM) "
                    "is deprecated. Use SmartForms or Adobe Document Services (ADS) in S/4HANA.",
        patterns=[
            r'\bOPEN_FORM\b',
            r'\bWRITE_FORM\b',
            r'\bCLOSE_FORM\b',
            r'\bSSF_FUNCTION_MODULE_NAME\b',
            r'\bCALL\s+FUNCTION\s+[\'"]OPEN_FORM[\'"]',
        ],
        remediation="Migrate SAP Script forms to SmartForms (CL_SMARTFORMS) or "
                    "Adobe Forms (FP_FUNCTION_MODULE_NAME) for S/4HANA compatibility.",
        example_bad="CALL FUNCTION 'OPEN_FORM' EXPORTING form = 'ZORDER_FORM'.",
        example_good="CALL FUNCTION 'SSF_FUNCTION_MODULE_NAME'\n  EXPORTING formname = 'ZSF_ORDER'\n  IMPORTING fm_name = lv_fm_name.\nCALL FUNCTION lv_fm_name ...",
        tags=["forms", "print", "smartforms", "s4-migration"],
    ),

    Rule(
        id="S4-004",
        name="Classic ALV Grid (CL_GUI_ALV_GRID)",
        category="S4_MIGRATION",
        severity="MEDIUM",
        cc_level="C",
        s4_impact=True,
        description="CL_GUI_ALV_GRID requires classic dynpro and does not work in S/4HANA Fiori context. "
                    "SALV framework or CDS-based Fiori lists are the S/4HANA way.",
        patterns=[
            r'\bCL_GUI_ALV_GRID\b',
            r'\bCL_GUI_ALV_LIST\b',
            r'\bSLIST_ALV_GRID_DISPLAY\b',
            r"CALL\s+FUNCTION\s+'REUSE_ALV_GRID_DISPLAY'",
        ],
        remediation="Replace with CL_SALV_TABLE (no dynpro required), or migrate the report "
                    "to a Fiori analytical list page backed by a CDS view.",
        example_bad="CREATE OBJECT lo_alv TYPE cl_gui_alv_grid\n  EXPORTING i_parent = lo_container.",
        example_good="cl_salv_table=>factory(\n  IMPORTING r_salv_table = DATA(lo_salv)\n  CHANGING  t_table     = lt_data ).\nlo_salv->display( ).",
        tags=["alv", "ui", "fiori", "s4-migration"],
    ),

    Rule(
        id="S4-005",
        name="Obsolete TABLES Statement in Function Modules",
        category="S4_MIGRATION",
        severity="MEDIUM",
        cc_level="C",
        s4_impact=True,
        description="The TABLES statement in function module interfaces is obsolete. "
                    "S/4HANA requires CHANGING or EXPORTING TABLE parameters instead.",
        patterns=[r'^\s*FUNCTION\s+\w+\.[\s\S]{0,200}?^\s*TABLES\b'],
        remediation="Convert TABLES parameters to CHANGING TYPE TABLE OF or EXPORTING TYPE TABLE OF "
                    "in the function module interface.",
        example_bad="FUNCTION z_get_materials.\n  TABLES\n    et_materials TYPE ztt_material.",
        example_good="FUNCTION z_get_materials.\n  EXPORTING\n    et_materials TYPE ztt_material.",
        tags=["function-module", "interface", "s4-migration"],
    ),

    Rule(
        id="S4-006",
        name="Non-Unicode Compliant Syntax",
        category="S4_MIGRATION",
        severity="HIGH",
        cc_level="C",
        s4_impact=True,
        description="S/4HANA runs exclusively in Unicode mode. Code using TYPE X, fixed-length "
                    "character operations, or string-to-hex conversions may behave differently.",
        patterns=[
            r'\bTYPE\s+X\s+LENGTH\s+\d+',
            r'\bTRANSLATE\b.*\bUSING\b',
            r'\bOVERLAY\b',
        ],
        remediation="Replace TYPE X with XSTRING for variable-length binary data. "
                    "Use CL_ABAP_CONV_CODEPAGE for character conversions.",
        example_bad="DATA: lv_hex TYPE x LENGTH 4.",
        example_good="DATA: lv_hex TYPE xstring.",
        tags=["unicode", "encoding", "s4-migration"],
    ),

    Rule(
        id="S4-007",
        name="Deprecated HR Infotype Direct Access",
        category="S4_MIGRATION",
        severity="HIGH",
        cc_level="D",
        s4_impact=True,
        description="Direct SELECT on PA* (Personnel Administration) and HRP* (HR Objects) tables "
                    "is deprecated in S/4HANA. HCM data must be accessed through function modules or BAdIs.",
        patterns=[
            r'\bSELECT\b.*\bFROM\s+(PA\d{4}|HRP\d{4}|PAPT|PAPTX)\b',
        ],
        remediation="Use HR_READ_INFOTYPE function module or HRPA_READ_INFOTYPE for PA table access. "
                    "For HRP tables, use CL_HRPAD_READ_INFOTYPE.",
        example_bad="SELECT * FROM pa0002 WHERE pernr = lv_pernr.",
        example_good="CALL FUNCTION 'HR_READ_INFOTYPE'\n  EXPORTING pernr = lv_pernr  infty = '0002'\n  TABLES infty_tab = lt_p0002.",
        tags=["hr", "hcm", "infotype", "s4-migration"],
    ),

    Rule(
        id="S4-008",
        name="OCCURS Clause (Obsolete Internal Table Declaration)",
        category="S4_MIGRATION",
        severity="LOW",
        cc_level="B",
        s4_impact=True,
        description="OCCURS n in DATA declarations is obsolete since ABAP 7.0. "
                    "In S/4HANA it is ignored but creates confusion and potential issues with tools.",
        patterns=[r'\bOCCURS\s+\d+', r'\bTABLES\b.*\bOCCURS\b'],
        remediation="Remove OCCURS clause. Modern ABAP internal tables are dynamic by default.",
        example_bad="DATA: lt_orders TYPE TABLE OF vbak OCCURS 0.",
        example_good="DATA: lt_orders TYPE TABLE OF vbak.",
        tags=["syntax", "obsolete", "s4-migration"],
    ),

    Rule(
        id="S4-009",
        name="FIELD-GROUPS Statement (Obsolete)",
        category="S4_MIGRATION",
        severity="MEDIUM",
        cc_level="C",
        s4_impact=True,
        description="FIELD-GROUPS / INSERT / EXTRACT / SORT EXTRACT are completely obsolete in S/4HANA. "
                    "These constructs are not supported in ABAP on HANA.",
        patterns=[
            r'^\s*FIELD-GROUPS\b',
            r'^\s*INSERT\s+\w+\s+(?:INCLUDING\s+\w+\s+)?INTO\s+\w+\.',
            r'^\s*EXTRACT\b',
            r'\bSORT\s+EXTRACT\b',
        ],
        remediation="Replace FIELD-GROUPS with standard internal tables (SORTED TABLE or HASHED TABLE). "
                    "Use SORT lt_data BY key1 key2 for sorting.",
        example_bad="FIELD-GROUPS: header, position.\nINSERT header.",
        example_good="TYPES: BEGIN OF ty_record, bukrs TYPE bukrs, belnr TYPE belnr_d, END OF ty_record.\nDATA lt_records TYPE SORTED TABLE OF ty_record WITH UNIQUE KEY bukrs belnr.",
        tags=["field-groups", "obsolete", "s4-migration"],
    ),

    Rule(
        id="S4-010",
        name="Classic User Exit (Obsolete Enhancement)",
        category="S4_MIGRATION",
        severity="MEDIUM",
        cc_level="C",
        s4_impact=True,
        description="Classic User Exits (CALL CUSTOMER-FUNCTION, INCLUDE ZXXX) are maintained "
                    "in SAP source code and create modification risk. BADIs are the S/4HANA standard. "
                    "In S/4HANA Cloud, User Exits do not exist — RAP BAdIs are the only extension mechanism. "
                    "SAP Joule AI (S/4HANA 2025) can identify the correct RAP BAdI for a given User Exit.",
        patterns=[
            r'\bCALL\s+CUSTOMER-FUNCTION\b',
            r'^\s*INCLUDE\s+Z[A-Z0-9]{4,}',
        ],
        remediation="Migrate to RAP BAdIs — the Clean Core Level A extension standard for S/4HANA: "
                    "(1) Find the correct BAdI via SE18 (transaction) or the SAP Business Accelerator Hub "
                    "(api.sap.com → On-Stack Extensibility → Business Object Interface). "
                    "(2) Create a BAdI implementation class (ZCL_<NAME>_IMPL) that implements the BAdI interface. "
                    "(3) Use the kernel BAdI pattern: GET BADI ... CALL BADI for classic ABAP, "
                    "or implement the BDEF behavior method directly in ABAP Cloud. "
                    "If no BAdI exists, raise an SAP Influence Request.",
        example_bad="CALL CUSTOMER-FUNCTION '001' EXPORTING material = lv_matnr.",
        example_good="\" Classic BAdI (Level B)\nGET BADI lo_badi TYPE if_ex_material_check.\nCALL BADI lo_badi->check_material EXPORTING iv_material = lv_matnr.\n\" RAP BAdI (Level A — for ABAP Cloud)\n\" Implement IF_SD_SALESORDER~BEFORE_SAVE in BDEF behavior class zcl_z_so_badi_impl.",
        tags=["user-exit", "badi", "enhancement", "s4-migration", "rap", "level-a"],
    ),

    Rule(
        id="S4-011",
        name="MATNR / Material Number Field Length (18 → 40 chars)",
        category="S4_MIGRATION",
        severity="MEDIUM",
        cc_level="C",
        s4_impact=True,
        description="In SAP S/4HANA (from S/4 2023), the MATNR domain was extended from 18 to 40 characters. "
                    "Custom code using fixed-length TYPE C LENGTH 18 or LIKE MARA-MATNR for material number fields, "
                    "or string comparisons trimmed to 18 chars, may silently truncate material numbers. "
                    "This is a known S/4HANA Simplification Item.",
        patterns=[
            r'\bTYPE\s+C\s+LENGTH\s+18\b',
            r'\bMAXLEN\s*=\s*18\b',
            r'(?i)\bmatnr\b.*?\bLENGTH\b.*?18',
        ],
        remediation="Declare material-number variables using the ABAP Dictionary domain MATNR or type MARA-MATNR "
                    "(which inherits the correct length automatically). "
                    "Replace TYPE C LENGTH 18 with TYPE MATNR. "
                    "For string operations, use the full-length field: CONDENSE lv_matnr NO-GAPS, not SUBSTRING. "
                    "Test with materials created in S/4HANA with > 18 character IDs.",
        example_bad="DATA: lv_material TYPE c LENGTH 18.  \" Will truncate 40-char MATNR.",
        example_good="DATA: lv_material TYPE matnr.  \" Inherits correct 40-char length from domain.",
        tags=["matnr", "field-length", "s4-2023", "simplification"],
    ),

    Rule(
        id="S4-012",
        name="Missing ATC ABAP Cloud Readiness Marker",
        category="S4_MIGRATION",
        severity="LOW",
        cc_level="B",
        s4_impact=True,
        description="Programs that mix ABAP Cloud-incompatible statements (SELECT from standard tables, "
                    "FORM routines, MESSAGE statements) without a clear migration comment or ATC exemption "
                    "create invisible technical debt. The ABAP Test Cockpit CLOUD_READINESS variant "
                    "classifies such code as Level C or D automatically.",
        patterns=[
            r'^\s*PROGRAM\s+\w+\.',
            r'^\s*REPORT\s+\w+\.',
        ],
        remediation="Run ABAP Test Cockpit (ATC) with the CLOUD_READINESS check variant (transaction SCI or ABAP ADT). "
                    "This automatically classifies each finding as Level A–D. "
                    "For S/4HANA 2023+ systems, SAP Note 3565942 delivers the clean core ATC checks. "
                    "Prioritize: fix all Level D findings first (transport blockers), then Level C (warnings), "
                    "then Level B (informational). Target: only Level A findings for new development.",
        example_bad="\" No ATC execution — clean core compliance level unknown.",
        example_good="\" After running ATC CLOUD_READINESS:\n\" Level A: 0 findings — fully upgrade-safe\n\" Level B: 2 findings — classic BAPIs, governance-approved\n\" Level C: 0 findings — all internal API calls eliminated\n\" Level D: 0 findings — no modifications",
        tags=["atc", "cloud-readiness", "governance", "s4-2023"],
    ),

    Rule(
        id="CC-015",
        name="ABAP Cloud Forbidden Syntax (ABAP for Cloud Development)",
        category="CLEAN_CORE",
        severity="HIGH",
        cc_level="D",
        description="Certain ABAP statements are forbidden in ABAP Cloud (BTP ABAP Environment and S/4HANA Cloud). "
                    "These include CALL TRANSACTION, CALL SCREEN, SUBMIT, WRITE, COMMIT WORK in certain contexts, "
                    "and CREATE OBJECT (use NEW instead). Using them blocks BTP deployment.",
        patterns=[
            r'^\s*SUBMIT\s+\w+',
            r'^\s*WRITE\s+(?!:.*TO\s)',
            r'^\s*CALL\s+SCREEN\b',
        ],
        remediation="Replace forbidden ABAP Cloud statements with cloud-compliant alternatives: "
                    "(1) SUBMIT → Replace with direct class instantiation or RAP action call. "
                    "(2) WRITE → Use string variables and return values instead of spool output. "
                    "(3) CALL SCREEN → Use Fiori Elements UI5 app backed by OData V4 service. "
                    "(4) CREATE OBJECT → Replace with the NEW operator: DATA(lo_obj) = NEW zcl_myclass( ).",
        example_bad="SUBMIT zreport_old WITH selection_screen.  \" Forbidden in ABAP Cloud",
        example_good="\" Trigger logic directly via class method\nDATA(lo_handler) = NEW zcl_report_logic( ).\nlo_handler->execute( iv_bukrs = lv_bukrs ).",
        tags=["abap-cloud", "btp", "forbidden-syntax", "level-d"],
    ),

    Rule(
        id="CC-016",
        name="Direct Write to S/4HANA Simplified Tables (Now Views)",
        category="CLEAN_CORE",
        severity="CRITICAL",
        cc_level="D",
        description="Several ECC database tables were replaced by database views in S/4HANA as part of the "
                    "Simplification List. Inserting or updating these tables directly causes runtime errors. "
                    "Common simplified tables: CDHDR/CDPOS (change docs), KNA1/LFA1 in certain scenarios, "
                    "REGUP/REGUD (payment), and HR infotype tables.",
        patterns=[
            r'\b(INSERT|UPDATE|MODIFY|DELETE)\s+(?:INTO\s+)?(REGUP|REGUD|BSEC|BSED|BSEM)\b',
            r'\b(INSERT|UPDATE|MODIFY)\s+(?:INTO\s+)?(CDHDR|CDPOS)\b',
        ],
        remediation="Use the official SAP API for write operations on simplified tables. "
                    "Check the S/4HANA Simplification Database (transaction SYCM or SAP Note 2229651) "
                    "for the complete list of simplified objects and their recommended replacements. "
                    "For FI documents: use BAPI_ACC_DOCUMENT_POST. "
                    "For change documents: they are written automatically by standard SAP — do not write CDHDR/CDPOS directly.",
        example_bad="INSERT INTO cdhdr VALUES ls_cdhdr.  \" Runtime error in S/4HANA — CDHDR is a view",
        example_good="\" Change documents are written automatically by SAP when you use standard BAPIs/RAP.\n\" Use BAPI_ACC_DOCUMENT_POST for FI postings — change docs created by framework.",
        tags=["simplified-tables", "s4-views", "s4-blocker", "level-d"],
    ),

    # ── SECURITY RULES ────────────────────────────────────────────────────────

    Rule(
        id="SEC-001",
        name="Dynamic ABAP Code Generation",
        category="SECURITY",
        severity="CRITICAL",
        description="GENERATE SUBROUTINE POOL and INSERT REPORT with dynamic content "
                    "can execute arbitrary ABAP code and is a critical security vulnerability (Code Injection).",
        patterns=[
            r'\bGENERATE\s+SUBROUTINE\s+POOL\b',
            r'\bINSERT\s+REPORT\b.*\bFROM\b',
        ],
        remediation="Eliminate dynamic code generation. If unavoidable, apply strict input validation "
                    "and use only whitelisted, controlled code templates. Log all executions.",
        example_bad="GENERATE SUBROUTINE POOL lt_code NAME lv_prog_name.",
        example_good="\" Restructure logic to avoid dynamic code. Use Strategy pattern instead.",
        tags=["security", "code-injection", "owasp-top10"],
    ),

    Rule(
        id="SEC-002",
        name="OS Command Execution",
        category="SECURITY",
        severity="CRITICAL",
        description="Executing OS commands (CALL 'SYSTEM', WS_EXECUTE, CALL FUNCTION 'SXPG_COMMAND_EXECUTE') "
                    "with user-controlled parameters can lead to OS command injection.",
        patterns=[
            r"CALL\s+FUNCTION\s+'SXPG_COMMAND_EXECUTE'",
            r"CALL\s+FUNCTION\s+'WS_EXECUTE'",
            r"\bCALL\s+'SYSTEM'\b",
        ],
        remediation="Avoid OS command execution where possible. If required, use SM69 external command "
                    "definitions and never pass user-controlled data as parameters.",
        example_bad="CALL FUNCTION 'SXPG_COMMAND_EXECUTE' EXPORTING commandname = lv_user_input.",
        example_good="\" Define command in SM69, reference by fixed name only.\nCALL FUNCTION 'SXPG_COMMAND_EXECUTE'\n  EXPORTING commandname = 'ZFIXED_CMD_NAME'.",
        tags=["security", "os-command", "injection"],
    ),

    Rule(
        id="SEC-003",
        name="Unvalidated File Operations",
        category="SECURITY",
        severity="HIGH",
        description="OPEN DATASET with user-controlled file paths can lead to path traversal attacks "
                    "and unauthorized file access on the application server.",
        patterns=[
            r'\bOPEN\s+DATASET\b.*\(lv_\w+\)',
            r'\bOPEN\s+DATASET\b.*USING\b',
        ],
        remediation="Validate file paths against an allowed directory list. "
                    "Use CL_ABAP_FILE_ACCESS to validate paths. Log all file operations.",
        example_bad="OPEN DATASET lv_filepath FOR OUTPUT IN TEXT MODE.",
        example_good="\" Validate path is within allowed directory\ncl_abap_file_access=>check_read_permission( lv_filepath ).\nOPEN DATASET lv_filepath FOR OUTPUT IN TEXT MODE.",
        tags=["security", "file-access", "path-traversal"],
    ),

    Rule(
        id="SEC-004",
        name="RFC Destination Hardcoded",
        category="SECURITY",
        severity="MEDIUM",
        description="Hardcoded RFC destination names make remote calls environment-specific "
                    "and may expose system topology information.",
        patterns=[
            r"DESTINATION\s+'[A-Z]{2,}\w+'",
        ],
        remediation="Read RFC destination from Customizing table (via SELECT) or use "
                    "logical destination abstractions that resolve per environment.",
        example_bad="CALL FUNCTION 'BAPI_MATERIAL_GETLIST' DESTINATION 'PRD_BACKEND'.",
        example_good="SELECT SINGLE dest FROM ztconfig WHERE key = 'BACKEND_RFC'\n  INTO lv_dest.\nCALL FUNCTION 'BAPI_MATERIAL_GETLIST' DESTINATION lv_dest.",
        tags=["security", "rfc", "hardcoded"],
    ),

    # ── PERFORMANCE RULES ─────────────────────────────────────────────────────

    Rule(
        id="PF-001",
        name="Missing WHERE Clause (Full Table Scan)",
        category="PERFORMANCE",
        severity="HIGH",
        description="SELECT without a WHERE clause or with a non-selective condition performs "
                    "a full table scan — catastrophic on large HANA tables.",
        patterns=[
            r'\bSELECT\b(?!.*\bWHERE\b).*\bFROM\b.*\bINTO\b',
        ],
        remediation="Always add a WHERE clause with indexed fields. "
                    "Check table key fields with SE11 and ensure your WHERE uses primary or secondary key fields.",
        example_bad="SELECT * FROM ekpo INTO TABLE lt_po_items.",
        example_good="SELECT ebeln, ebelp, matnr FROM ekpo\n  WHERE ebeln = @lv_po_number\n  INTO TABLE @DATA(lt_po_items).",
        tags=["performance", "database", "full-table-scan"],
    ),

    Rule(
        id="PF-002",
        name="COMMIT WORK Without Error Handling",
        category="PERFORMANCE",
        severity="MEDIUM",
        description="COMMIT WORK without checking for lock failures or ROLLBACK handling "
                    "can leave data in inconsistent state, especially in S/4HANA with lock objects.",
        patterns=[
            r'\bCOMMIT\s+WORK\b(?!.*AND\s+WAIT)',
        ],
        remediation="Use COMMIT WORK AND WAIT to ensure synchronous update, "
                    "and always check for BAPI return messages before committing.",
        example_bad="COMMIT WORK.",
        example_good="CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'\n  EXPORTING wait = abap_true\n  IMPORTING return = ls_return.\nIF ls_return-type = 'E'.\n  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.\nENDIF.",
        tags=["performance", "data-consistency", "luw"],
    ),

    Rule(
        id="PF-003",
        name="BYPASSING BUFFER (Database Buffer Bypass)",
        category="PERFORMANCE",
        severity="MEDIUM",
        description="BYPASSING BUFFER forces every SELECT to bypass the SAP table buffer, "
                    "creating unnecessary database round trips for buffered tables.",
        patterns=[r'\bBYPASSING\s+BUFFER\b'],
        remediation="Remove BYPASSING BUFFER unless you have a specific reason (e.g., critical real-time data). "
                    "Ensure the table has appropriate buffering set in SE11.",
        example_bad="SELECT * FROM t001 BYPASSING BUFFER INTO TABLE lt_companies.",
        example_good="SELECT * FROM t001 INTO TABLE @DATA(lt_companies).",
        tags=["performance", "buffer", "database"],
    ),

    Rule(
        id="PF-004",
        name="Unparameterised FOR ALL ENTRIES",
        category="PERFORMANCE",
        severity="HIGH",
        description="FOR ALL ENTRIES IN with an empty internal table results in a full table scan "
                    "in classic ABAP (SAP converts it to WHERE 1=1). Always check IS NOT INITIAL first.",
        patterns=[r'\bFOR\s+ALL\s+ENTRIES\s+IN\s+@?\w+(?!.*IS\s+NOT\s+INITIAL)'],
        remediation="Always guard FOR ALL ENTRIES with: IF lt_table IS NOT INITIAL. ... ENDIF.",
        example_bad="SELECT ebeln FROM ekpo FOR ALL ENTRIES IN lt_orders\n  WHERE ebeln = lt_orders-vbeln.",
        example_good="IF lt_orders IS NOT INITIAL.\n  SELECT ebeln FROM ekpo\n    FOR ALL ENTRIES IN @lt_orders\n    WHERE ebeln = @lt_orders-vbeln\n    INTO TABLE @DATA(lt_items).\nENDIF.",
        tags=["performance", "for-all-entries", "full-table-scan"],
    ),
]

# ── Helper functions ──────────────────────────────────────────────────────────

def rules_by_category(category: str) -> List[Rule]:
    return [r for r in ALL_RULES if r.category == category]


def rules_by_severity(severity: str) -> List[Rule]:
    return [r for r in ALL_RULES if r.severity == severity]


def get_rule(rule_id: str) -> Optional[Rule]:
    return next((r for r in ALL_RULES if r.id == rule_id), None)


def scan_code(code: str, categories: Optional[List[str]] = None) -> List[Violation]:
    """
    Apply all rules (built-in + enabled custom) to the provided ABAP code.
    Returns sorted list of Violation objects (most severe first).
    """
    from core.custom_rules import get_active_custom_rule_objects
    all_rules = ALL_RULES + get_active_custom_rule_objects()
    lines  = code.splitlines()
    active = [r for r in all_rules if (categories is None or r.category in categories)]
    violations: List[Violation] = []

    for rule in active:
        for pattern in rule.patterns:
            try:
                flags = re.IGNORECASE | re.MULTILINE
                # For multi-line patterns, search the whole code
                if r'[\s\S]' in pattern or r'\n' in pattern:
                    for m in re.finditer(pattern, code, flags | re.DOTALL):
                        line_num = code[:m.start()].count('\n') + 1
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                        ctx_start = max(0, line_num - 3)
                        ctx_end   = min(len(lines), line_num + 2)
                        context   = "\n".join(lines[ctx_start:ctx_end])
                        # Avoid duplicate violations for same rule+line
                        if not any(v.rule_id == rule.id and v.line_number == line_num for v in violations):
                            violations.append(Violation(rule=rule, line_number=line_num,
                                                        line_content=line_content.strip(), context=context))
                else:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, flags):
                            ctx_start = max(0, line_num - 3)
                            ctx_end   = min(len(lines), line_num + 2)
                            context   = "\n".join(lines[ctx_start:ctx_end])
                            if not any(v.rule_id == rule.id and v.line_number == line_num for v in violations):
                                violations.append(Violation(rule=rule, line_number=line_num,
                                                            line_content=line.strip(), context=context))
            except re.error:
                continue

    violations.sort(key=lambda v: (SEVERITY_ORDER.get(v.severity, 99), v.line_number))
    return violations


def compute_clean_core_level(violations: List[Violation]) -> str:
    """
    Returns A (compliant) → D (critical blocker).
    D: Any CRITICAL or Level-D violations
    C: HIGH violations present
    B: Only MEDIUM/LOW violations
    A: No violations or INFO only
    """
    cc_violations = [v for v in violations if v.category in ("CLEAN_CORE", "S4_MIGRATION")]
    if any(v.severity == "CRITICAL" or v.rule.cc_level == "D" for v in cc_violations):
        return "D"
    if any(v.severity == "HIGH" for v in cc_violations):
        return "C"
    if any(v.severity == "MEDIUM" for v in cc_violations):
        return "B"
    return "A"


def compute_migration_score(violations: List[Violation]) -> int:
    """
    Returns 5 (high risk) → 100 (fully ready for S/4HANA migration).
    Penalties are capped so the score never collapses to 0 for fixable code.
    """
    s4_violations = [v for v in violations if v.s4_impact or v.category == "S4_MIGRATION"]
    if not s4_violations:
        return 100
    weights = {"CRITICAL": 20, "HIGH": 12, "MEDIUM": 6, "LOW": 2, "INFO": 1}
    penalty = sum(weights.get(v.severity, 0) for v in s4_violations)
    # Cap max deduction at 90 so the scale reads 5–100, not 0–100
    return max(5, 100 - min(penalty, 90))


LEVEL_META = {
    "A": {"label": "Level A — Fully Compliant",   "color": "#188918", "bg": "#E8F5E9", "icon": "✅"},
    "B": {"label": "Level B — Mostly Compliant",  "color": "#0070F2", "bg": "#E3F2FD", "icon": "🔵"},
    "C": {"label": "Level C — Needs Attention",   "color": "#C87400", "bg": "#FFF8E0", "icon": "⚠️"},
    "D": {"label": "Level D — Upgrade Blocker",   "color": "#BB0000", "bg": "#FFEAEA", "icon": "🔴"},
}
