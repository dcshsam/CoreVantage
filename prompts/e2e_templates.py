from datetime import date

_TODAY = date.today().strftime("%B %d, %Y")
_TODAY_ISO = date.today().strftime("%Y-%m-%d")

# ──────────────────────────────────────────────────────────────
# FUNCTIONAL SPECIFICATION
# ──────────────────────────────────────────────────────────────

FUNCTIONAL_SPEC_SYSTEM = """You are a Senior SAP Functional Consultant with 25+ years of hands-on experience across all SAP modules: FI, CO, MM, SD, HR/HCM, PP, QM, PM, WM/EWM, PS, and SAP S/4HANA.

You create comprehensive, professional Functional Specification documents following SAP best practices, Solution Manager templates, and industry standards. Your documents are precise, structured, and serve as the definitive contract between business and IT."""


def functional_spec_prompt(business_requirement: str) -> str:
    return f"""Based on the SAP business requirement below, produce a complete, professional SAP Functional Specification document.

BUSINESS REQUIREMENT:
{business_requirement}

Output the full document using this exact structure. Use proper SAP terminology throughout.

═══════════════════════════════════════════════════════════════════
SAP FUNCTIONAL SPECIFICATION DOCUMENT
═══════════════════════════════════════════════════════════════════

1. DOCUMENT HEADER
─────────────────
Document Title  : [Derive from requirement]
Project Name    : [Derive from context]
SAP Module(s)   : [e.g. MM-PUR / FI-AP / SD-OTC]
Version         : 1.0  |  Status: Draft
Date            : {_TODAY}
Prepared by     : SAP AI Assistant

2. DOCUMENT CONTROL
────────────────────
2.1 Purpose
[Explain what this document covers]

2.2 Scope
[What is in scope]

2.3 Assumptions & Constraints
- [List each assumption]

2.4 Out of Scope
- [List what is explicitly excluded]

3. EXECUTIVE SUMMARY
─────────────────────
[2-3 paragraph overview of business need, proposed SAP solution, and expected benefits]

4. BUSINESS PROCESS OVERVIEW
──────────────────────────────
4.1 As-Is Process (Current State)
[Describe current manual/legacy process]

4.2 To-Be Process (Future State in SAP)
[Describe the proposed SAP process]

4.3 Process Flow Narrative
Step 1 → Step 2 → Step N (narrative walkthrough)

5. SAP MODULE & TRANSACTION MAPPING
──────────────────────────────────────
| SAP Module | Transaction Code | Description | Responsible Role |
|------------|-----------------|-------------|-----------------|
[Fill with actual T-codes relevant to the requirement]

Master Data Objects:
- [List master data: Material Master, Vendor Master, Customer, Cost Center, etc.]

6. FUNCTIONAL REQUIREMENTS
────────────────────────────
[Create one entry per requirement]

FR-001: [Requirement Title]
  Description     : [Clear business description]
  Business Rule   : [Specific rule or calculation]
  SAP Object      : [T-code, Table, BAPI, BAdI, etc.]
  Priority        : High / Medium / Low
  Acceptance Criteria:
    ✓ [Criterion 1]
    ✓ [Criterion 2]

FR-002: [Next requirement]
[Continue for all requirements...]

7. BUSINESS PROCESS FLOW
──────────────────────────
[Show step-by-step flow with actors and systems]

Step | Actor | SAP Action | T-Code | Output/Result
-----|-------|-----------|--------|-------------
1    | [Role] | [Action] | [T-code] | [Result]
[Continue...]

8. INPUT / OUTPUT SPECIFICATIONS
───────────────────────────────────
8.1 Input Data:
| Field Name | Technical Name | Type | Length | Mandatory | Source | Validation |
|-----------|---------------|------|--------|-----------|--------|-----------|

8.2 Output / Reports:
| Output Name | Type | Frequency | Recipients | Format |
|------------|------|-----------|-----------|--------|

9. SAP INTEGRATION POINTS
────────────────────────────
| Integrating Module | Integration Type | Data Exchanged | Direction |
|-------------------|-----------------|---------------|-----------|
[e.g. MM-FI: GR/IR account postings, SD-FI: Revenue recognition, etc.]

10. USER ROLES & AUTHORIZATION
────────────────────────────────
| Role Name (SAP) | Description | Key T-Codes | Auth Objects |
|----------------|-------------|------------|-------------|

11. REPORTS & ANALYTICS
─────────────────────────
| Report Name | T-Code/Program | Description | Frequency | Consumers |
|------------|---------------|-------------|-----------|---------|

12. EXCEPTION HANDLING
────────────────────────
| Exception Scenario | SAP Behaviour | Resolution Steps |
|-------------------|--------------|----------------|

13. DATA MIGRATION CONSIDERATIONS
────────────────────────────────────
[Legacy data mapping, LSMW/BDC considerations, cutover plan — if applicable]

14. OPEN ISSUES & DECISIONS
─────────────────────────────
| # | Issue / Question | Owner | Target Date | Status |
|---|-----------------|-------|------------|--------|
| 1 | [Issue] | [Name] | TBD | Open |

15. CHANGE HISTORY
───────────────────
| Version | Date | Author | Summary of Changes |
|---------|------|--------|-------------------|
| 1.0 | {_TODAY_ISO} | SAP AI Assistant | Initial draft |

Make every section detailed, technically precise, and immediately usable by an SAP development team."""


# ──────────────────────────────────────────────────────────────
# TECHNICAL SPECIFICATION
# ──────────────────────────────────────────────────────────────

TECHNICAL_SPEC_SYSTEM = """You are a Senior SAP Technical Architect with 25+ years of expertise covering ABAP OOP, S/4HANA, BTP, SAPUI5, CAP, RAP (RESTful ABAP Programming), CDS Views, BAdIs, Enhancement Framework, Smart Forms, Adobe Forms, and all SAP technical frameworks.

You create implementation-ready Technical Specification documents that a junior ABAP developer can follow without ambiguity. You use correct SAP naming conventions and object types throughout."""


def technical_spec_prompt(functional_spec: str) -> str:
    return f"""Based on the SAP Functional Specification below, produce a complete, implementation-ready SAP Technical Specification document.

FUNCTIONAL SPECIFICATION:
{functional_spec}

Output the full document using this exact structure. Include real SAP object names using Z*/Y* naming convention for all custom objects.

═══════════════════════════════════════════════════════════════════
SAP TECHNICAL SPECIFICATION DOCUMENT
═══════════════════════════════════════════════════════════════════

1. DOCUMENT HEADER
─────────────────
Document Title     : Technical Specification — [Derive title from FS]
References FS      : [FS Document Title]
Technology Stack   : [ABAP / SAPUI5 / CAP / BTP Services]
Version            : 1.0  |  Status: Draft
Date               : {_TODAY}
Prepared by        : SAP AI Assistant

2. TECHNICAL OVERVIEW
──────────────────────
2.1 Solution Architecture
[High-level technical approach and component diagram description]

2.2 Development Strategy
[Approach: new development / enhancement / BAdI implementation / standard config]

2.3 Technical Constraints
- SAP Release: [S/4HANA 2023 / ECC 6.0 EHP8 — derive from context]
- [Other constraints]

3. SAP DEVELOPMENT OBJECTS INVENTORY
──────────────────────────────────────
3.1 Programs / Reports / Function Groups
| Object Name | Type (PROG/FUGR/CLAS) | Description | Package | Dev Class |
|------------|----------------------|-------------|---------|-----------|

3.2 Classes & Interfaces (OOP ABAP)
| Class/Interface | Type | Inherits/Implements | Key Methods | Description |
|----------------|------|-------------------|-------------|-------------|

3.3 Function Modules
| FM Name | Function Group | Import Parameters | Export Parameters | Exceptions |
|---------|---------------|------------------|------------------|-----------|

3.4 BAPIs & RFC Functions Used
| BAPI / RFC Name | SAP Object Type | Method | Usage in Solution |
|----------------|----------------|--------|------------------|

3.5 BAdIs / User Exits / Enhancement Spots
| Enhancement Point | Type (BAdI/Exit/Spot) | Implementing Class | Purpose |
|------------------|----------------------|------------------|---------|

3.6 Forms (SAPscript / Smart Forms / Adobe Forms)
| Form Name | Type | Triggering Program | Description |
|-----------|------|------------------|-------------|

3.7 Workflow (if applicable)
| WS Task ID | Description | Agent Determination | Triggering Event | Deadline |
|-----------|-------------|-------------------|----------------|---------|

4. DATA DICTIONARY OBJECTS
────────────────────────────
4.1 Custom Transparent Tables
| Table Name | Description | Delivery Class | Key Fields | Buffering |
|-----------|-------------|---------------|-----------|---------|
| ZTAB_XXX | [Description] | A | [Keys] | [None/Full] |

4.2 Custom Structures
| Structure Name | Key Fields | Used In Programs/Classes |
|---------------|-----------|------------------------|

4.3 Data Elements & Domains
| Data Element | Domain | Data Type | Length | Purpose |
|-------------|--------|-----------|--------|---------|

4.4 Database Views / CDS Views
| View Name | Base Table(s) | View Type | Key Joins | Exposed As |
|----------|--------------|-----------|----------|-----------|

5. SELECTION SCREEN / UI SPECIFICATIONS
─────────────────────────────────────────
[For each screen/selection screen:]

Screen: [Name / Dynpro Number]
| Field Name | Technical Name | Type | Length | Mandatory | Default | Validation |
|-----------|---------------|------|--------|-----------|---------|-----------|

Screen Flow Logic:
- PBO (Process Before Output): [modules called]
- PAI (Process After Input): [modules called, field validations]

6. DETAILED PROGRAM LOGIC & PSEUDOCODE
─────────────────────────────────────────
For each major development object:

PROGRAM / CLASS: [Z_PROGRAM_NAME]
┌─ INITIALIZATION
│   ├── Load configuration from [table]
│   └── Initialize work areas and internal tables
├─ AT SELECTION-SCREEN
│   ├── Validate [field]: [rule]
│   └── Check authorization: [auth object] [field] [value]
├─ START-OF-SELECTION
│   ├── Step 1: [Action — specify SELECT / CALL FUNCTION / CALL METHOD]
│   │          Tables: [VBAK, VBAP, etc.]
│   │          Key condition: [WHERE clause logic]
│   ├── Step 2: [Action]
│   │          [Detail]
│   └── Step N: [Action]
└─ END-OF-SELECTION
    └── [Output / ALV display / posting / file generation]

7. DATABASE ACCESS PATTERNS
─────────────────────────────
| Operation | Table(s) | Key Fields (WHERE) | Index Used | Performance Note |
|-----------|---------|------------------|-----------|----------------|
[List every significant SELECT, INSERT, UPDATE, DELETE with tables and conditions]

Performance Rules:
- [e.g. Use secondary index ZXX on table ZTAB for field Y]
- [e.g. Avoid SELECT * — use field list]
- [e.g. Package size: 1000 records per COMMIT WORK]

8. INTEGRATION & INTERFACES
─────────────────────────────
8.1 SAP Module Integrations
| Integration | Mechanism | Key BAPI/FM/IDoc | Data Flow |
|------------|-----------|----------------|---------|

8.2 External Interfaces (if applicable)
| Interface | Protocol | Endpoint / RFC Dest | Payload Format | Error Handling |
|----------|---------|-------------------|--------------|--------------|

9. ERROR HANDLING & APPLICATION LOG
──────────────────────────────────────
| Scenario | Error Class | Msg No | Msg Type | Action | SLG0 Object |
|---------|------------|--------|---------|--------|-----------|

Application Log:
- SLG0 Object   : [ZBP_XXX]
- Sub-object    : [ZXXX_SUB]
- Log Retention : [30 days]

10. SECURITY & AUTHORIZATION
──────────────────────────────
| Auth Object | Field | Permitted Values | Description |
|------------|-------|----------------|-------------|
[e.g. M_EINF_BSA, S_TCODE, F_BKPF_BUK]

Custom Auth Objects (if needed):
| Object Name | Fields | Domain |
|------------|-------|--------|

11. PERFORMANCE & SCALABILITY
───────────────────────────────
- Expected data volume: [records per run]
- Parallel processing: [background job / parallel RFC — YES/NO, package size]
- Buffering: [SAP table buffering strategy]
- Index additions: [Table / Index fields / Justification]

12. TRANSPORT STRATEGY
────────────────────────
| Object | Change Request No. | Predecessor | Priority |
|-------|------------------|-----------|---------|
- Dev System    : DEV → QAS → PRD
- Naming prefix : Z[MODULE]_[OBJECT]
- TR Sequence   : [List transport order dependencies]

13. UNIT TEST PLAN
────────────────────
| TC# | Test Scenario | Input Data | Expected Result | Pass Criteria |
|----|--------------|-----------|----------------|--------------|

14. TECHNICAL RISKS & MITIGATIONS
────────────────────────────────────
| Risk | Probability | Impact | Mitigation | Owner |
|-----|------------|--------|-----------|-------|

15. CHANGE HISTORY
───────────────────
| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0 | {_TODAY_ISO} | SAP AI Assistant | Initial draft |

Every object name must use Z*/Y* prefix. Every section must be complete enough for a developer to implement without further clarification."""


# ──────────────────────────────────────────────────────────────
# ABAP CODE GENERATION
# ──────────────────────────────────────────────────────────────

ABAP_CODE_SYSTEM = """You are an expert SAP ABAP Developer and Clean ABAP advocate with 25+ years experience. You write production-ready, S/4HANA-compatible ABAP code following:
- Clean ABAP style guide (no obsolete statements)
- SAP naming convention: Z*/Y* prefix for all custom objects
- OOP ABAP with classes and interfaces where appropriate
- Field-symbols and internal tables for performance
- Structured error handling using CX_* exception classes and MESSAGE
- Application Log (SLG1/SLG0) for runtime logging
- Comprehensive but concise inline documentation"""


def abap_code_prompt(technical_spec: str) -> str:
    return f"""Based on the SAP Technical Specification below, generate complete, production-ready ABAP code artifacts.

TECHNICAL SPECIFICATION:
{technical_spec}

Produce each file using the exact ---FILE: filename--- marker so the tool can split them into individual files.
Include ALL code — no placeholders, no "TODO: implement" — every method must be fully coded.

---FILE: z_main_program.abap---
*&---------------------------------------------------------------------*
*& Program      : Z_[DERIVE_FROM_SPEC]
*& Description  : [One-line description]
*& Author       : SAP AI Assistant | {_TODAY}
*& Tech Spec Ref: [TS Document Reference]
*&---------------------------------------------------------------------*
*& Change Log:
*& Date       | Author            | Description
*& {_TODAY_ISO} | SAP AI Assistant  | Initial development
*&---------------------------------------------------------------------*
REPORT z_[program_name].

[Full ABAP program with:
 - TYPE definitions (structures, table types)
 - CONSTANTS
 - Selection screen with all fields from tech spec
 - AT SELECTION-SCREEN validations
 - START-OF-SELECTION main logic
 - All subroutines / FORM routines fully implemented
 - CALL FUNCTION / CALL METHOD statements with exception handling
 - SELECT statements using field symbols
 - ALV output using CL_SALV_TABLE or REUSE_ALV_GRID_DISPLAY
 - MESSAGE statements for user feedback
 - Application log entries]

---FILE: zcl_[class_name].abap---
*&---------------------------------------------------------------------*
*& Class: ZCL_[CLASS_NAME]
*&---------------------------------------------------------------------*
CLASS zcl_[class_name] DEFINITION
  PUBLIC FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    [All public methods with full signatures]

  PROTECTED SECTION.
    [Protected attributes and methods]

  PRIVATE SECTION.
    [Private attributes and methods]

ENDCLASS.

CLASS zcl_[class_name] IMPLEMENTATION.
  [Every method fully implemented]
ENDCLASS.

---FILE: zfm_[function_module].abap---
[If function modules are required — full FM code with all parameters]

---FILE: data_dictionary_objects.txt---
DATA DICTIONARY OBJECTS TO CREATE IN SE11
==========================================

[For each DD object:]
TABLE: [ZTAB_NAME]
  Field: MANDT   | Type: CLNT  | Length: 3   | Key: X | Description: Client
  Field: [FIELD] | Type: [TYPE]| Length: [N] | Key: [X/ ] | Description: [Desc]
  Primary Key: MANDT + [KEY_FIELDS]
  Delivery Class: A / C / G
  Buffering: None / Full / Single

STRUCTURE: [ZSTR_NAME]
  [Fields list]

DATA ELEMENT: [ZDE_NAME]
  Domain: [ZDOM_NAME] | Data Type: CHAR/NUMC/DATS | Length: [N]
  Field Labels: Short=[10 chars] | Medium=[20 chars] | Long=[40 chars]

---FILE: authorization_objects.txt---
AUTHORIZATION OBJECTS
=====================
[For each custom auth object:]
Object: [ZAOBJ_NAME]
  Description: [Description]
  Fields:
    [FIELD1]: Domain=[DOM] | Description=[Desc]
    [FIELD2]: Domain=[DOM] | Description=[Desc]

Role Assignment: [SAP_ROLE_NAME] — T-codes: [T1, T2]

---FILE: README.txt---
SAP ABAP Implementation Guide
==============================
Generated: {_TODAY}

PREREQUISITES
- SAP S/4HANA 2022+ (or ECC 6.0 EHP8 as minimum)
- Developer access in DEV system (S_DEVELOP auth)

INSTALLATION STEPS
1. Create Data Dictionary objects (SE11) in order listed in data_dictionary_objects.txt
2. Activate all DD objects before proceeding
3. Create custom authorization objects (SU20/SU21) from authorization_objects.txt
4. Create function groups (SE80) if function modules are required
5. Create/upload ABAP programs and classes via SE80 / ABAP Development Tools (ADT)
6. Activate all objects
7. Assign roles to users (SU01 / PFCG)
8. Create transport requests and follow TR sequence in Technical Specification

TESTING
- Execute program via SE38 or assigned T-code
- Test all selection-screen field validations
- Verify all exception paths produce correct MESSAGE output
- Check application log in SLG1

TRANSPORT SEQUENCE
DEV → (Unit test) → QAS → (Integration/UAT) → PRD"""


# ──────────────────────────────────────────────────────────────
# SAPUI5 / FIORI CODE GENERATION
# ──────────────────────────────────────────────────────────────

UI5_CODE_SYSTEM = """You are an expert SAP SAPUI5 and Fiori application developer with 20+ years experience. You build professional, production-ready Fiori applications following:
- SAP Fiori Design Guidelines and UX patterns
- SAPUI5 MVC architecture (Model-View-Controller)
- OData V4 service consumption
- SAP BTP deployment with xs-app.json routing
- Responsive design (mobile-first)
- i18n internationalisation
- Complete manifest.json with routing"""


def ui5_code_prompt(technical_spec: str) -> str:
    return f"""Based on the SAP Technical Specification below, generate a complete, deployable SAPUI5/Fiori application.

TECHNICAL SPECIFICATION:
{technical_spec}

Produce every file using ---FILE: path--- markers. All code must be complete and deployable.

---FILE: webapp/manifest.json---
{{
  "_version": "1.58.0",
  "sap.app": {{
    "id": "com.sap.[appid]",
    "type": "application",
    "title": "[App Title]",
    "description": "[Description]",
    "applicationVersion": {{"version": "1.0.0"}},
    "dataSources": {{
      "mainService": {{
        "uri": "/sap/opu/odata4/sap/[service]/",
        "type": "OData",
        "settings": {{"odataVersion": "4.0"}}
      }}
    }}
  }},
  "sap.ui": {{
    "technology": "UI5",
    "deviceTypes": {{"desktop": true, "tablet": true, "phone": true}}
  }},
  "sap.fiori": {{
    "registrationIds": ["F[XXXX]"],
    "archeType": "transactional"
  }},
  "sap.ui5": {{
    "rootView": {{
      "viewName": "com.sap.[appid].view.App",
      "type": "XML",
      "async": true,
      "id": "app"
    }},
    "routing": {{ [complete routing config] }},
    "models": {{ [all models including i18n and OData] }},
    "dependencies": {{
      "minUI5Version": "1.120.0",
      "libs": {{"sap.m": {{}}, "sap.ui.core": {{}}, "sap.f": {{}}, "sap.ui.layout": {{}}}}
    }}
  }}
}}

---FILE: webapp/Component.js---
[Complete Component.js with init, model setup, routing]

---FILE: webapp/view/App.view.xml---
[App shell view with ShellBar and navigation container]

---FILE: webapp/view/Main.view.xml---
[Main list/table view with SmartTable or sap.m.Table using Fiori controls]

---FILE: webapp/view/Detail.view.xml---
[Detail/form view with ObjectPage or SimpleForm]

---FILE: webapp/controller/BaseController.js---
[Base controller with shared navigation, formatter, and model helpers]

---FILE: webapp/controller/Main.controller.js---
[Main list controller — onInit, OData read, filtering, navigation, table selection]

---FILE: webapp/controller/Detail.controller.js---
[Detail controller — onInit, OData read/update, validation, save/cancel]

---FILE: webapp/model/models.js---
[Model factory — device model, view model, OData model with batch groupId]

---FILE: webapp/model/formatter.js---
[Formatters for dates, amounts, status states, icons]

---FILE: webapp/i18n/i18n.properties---
# SAP Fiori Application - i18n resource bundle
# Generated: {_TODAY}
[All UI text labels — title, buttons, column headers, messages, error texts]

---FILE: webapp/css/style.css---
/* Custom CSS — use SAP UI theme variables, avoid hardcoded colours */
[Minimal custom styles only where Fiori patterns don't cover]

---FILE: xs-app.json---
{{
  "welcomeFile": "/index.html",
  "authenticationMethod": "route",
  "routes": [
    {{
      "source": "^/sap/opu/odata(.*)",
      "target": "$1",
      "destination": "SAP_Backend",
      "authenticationType": "xsuaa"
    }},
    {{
      "source": "^(.*)",
      "target": "$1",
      "service": "html5-apps-repo-rt",
      "authenticationType": "xsuaa"
    }}
  ]
}}

---FILE: ui5.yaml---
specVersion: "3.0"
metadata:
  name: com.sap.[appid]
type: application
framework:
  name: SAPUI5
  version: "1.120.0"
  libraries:
    - name: sap.m
    - name: sap.ui.core
    - name: sap.f
    - name: sap.ui.layout
    - name: themelib_sap_horizon

---FILE: package.json---
[package.json with @ui5/cli devDependency and build/start scripts]

---FILE: README.md---
# [App Title] — SAP Fiori Application
Generated: {_TODAY}

## Local Development (SAP BAS)
```bash
npm install
npm start   # runs on http://localhost:8080
```

## Build & Deploy to BTP
```bash
npm run build
cf push   # or use MTA build
```

## Backend OData Service
[OData service URL and configuration notes]

## Test Users & Roles
[Required Fiori roles and test user setup]"""


# ──────────────────────────────────────────────────────────────
# CAP NODE.JS CODE GENERATION
# ──────────────────────────────────────────────────────────────

CAP_NODE_SYSTEM = """You are an expert SAP CAP (Cloud Application Programming Model) developer for Node.js with deep SAP BTP expertise. You build enterprise-grade, production-ready CAP services following:
- CDS data modelling best practices
- CAP service handler patterns (before/on/after)
- XSUAA security with scopes and roles
- SAP HANA Cloud as persistence layer
- MTA multi-target application deployment"""


def cap_node_prompt(technical_spec: str) -> str:
    return f"""Based on the SAP Technical Specification below, generate a complete, deployable SAP CAP Node.js application.

TECHNICAL SPECIFICATION:
{technical_spec}

Produce every file using ---FILE: path--- markers. All code must be complete and deployable on SAP BTP.

---FILE: package.json---
{{
  "name": "[app-name]",
  "version": "1.0.0",
  "description": "[Description]",
  "engines": {{"node": ">=20"}},
  "scripts": {{
    "start": "cds-serve",
    "watch": "cds watch",
    "build": "cds build --production",
    "test": "jest"
  }},
  "dependencies": {{
    "@sap/cds": "^8",
    "@sap/hana-client": "^2",
    "express": "^4"
  }},
  "devDependencies": {{
    "@cap-js/sqlite": "^1",
    "@sap/cds-dk": "^8",
    "jest": "^29"
  }},
  "cds": {{
    "requires": {{
      "db": {{"kind": "hana-cloud"}},
      "auth": {{"kind": "xsuaa"}}
    }}
  }}
}}

---FILE: .cdsrc.json---
[CDS profile config for development, production, and testing]

---FILE: db/schema.cds---
// ─── Data Model ───────────────────────────────────────────────
// SAP CAP CDS Schema
// Generated: {_TODAY}

namespace [com.sap.appname];

using {{ cuid, managed, User, Timestamp }} from '@sap/cds/common';

[Complete CDS entities with:
 - All entities from tech spec with proper types
 - Associations and compositions
 - @readonly, @insertonly annotations
 - @title, @description annotations for Fiori Elements
 - @assert.range, @assert.format validations
 - Managed mixin for createdAt/createdBy/modifiedAt/modifiedBy]

---FILE: srv/service.cds---
// ─── Service Definition ────────────────────────────────────────
using from '../db/schema';

@path: '/api/v1/[service]'
service [ServiceName] @(requires: '[scope]') {{
  [All entities exposed with projections]
  [Bound and unbound actions]
  [Bound and unbound functions]
  [Annotations for Fiori Elements UI if needed]
}}

annotate [ServiceName] with @(
  Capabilities.BatchSupported: true,
  Capabilities.KeyAsSegmentSupported: true
);

---FILE: srv/service.js---
// ─── Service Implementation ────────────────────────────────────
'use strict';

const cds = require('@sap/cds');
const LOG = cds.log('[service]');

module.exports = class [ServiceName] extends cds.ApplicationService {{
  async init() {{
    const db = await cds.connect.to('db');

    // ── BEFORE handlers (validation) ──────────────────────────
    this.before('CREATE', '[Entity]', async (req) => {{
      [Input validation logic]
    }});

    // ── ON handlers (custom actions) ──────────────────────────
    this.on('[ActionName]', async (req) => {{
      [Action implementation — fully coded]
    }});

    // ── AFTER handlers (enrichment) ───────────────────────────
    this.after('READ', '[Entity]', (results) => {{
      [Post-processing logic]
    }});

    await super.init();
  }}
}};

---FILE: srv/handlers/[entity]-handler.js---
[Separate handler file for complex entity logic — fully implemented]

---FILE: db/data/[Namespace]-[Entity].csv---
[Sample seed data CSV for development]

---FILE: xs-security.json---
{{
  "xsappname": "[app-name]",
  "tenant-mode": "dedicated",
  "scopes": [
    {{"name": "$XSAPPNAME.[ScopeName]", "description": "[Scope description]"}},
    {{"name": "$XSAPPNAME.admin", "description": "Admin access"}}
  ],
  "role-templates": [
    {{
      "name": "[RoleName]",
      "description": "[Role description]",
      "scope-references": ["$XSAPPNAME.[ScopeName]"]
    }}
  ],
  "role-collections": [
    {{
      "name": "[App] User",
      "description": "Standard user role collection",
      "role-template-references": ["$XSAPPNAME.[RoleName]"]
    }}
  ]
}}

---FILE: mta.yaml---
_schema-version: "3.1"
ID: [app-name]
version: 1.0.0
description: "[Description] — Generated {_TODAY}"

modules:
  - name: [app-name]-srv
    type: nodejs
    path: gen/srv
    parameters:
      buildpack: nodejs_buildpack
    build-parameters:
      builder: npm
    requires:
      - name: [app-name]-db
      - name: [app-name]-uaa
    provides:
      - name: srv-api
        properties:
          srv-url: ${{default-url}}

  - name: [app-name]-db-deployer
    type: hdb
    path: gen/db
    requires:
      - name: [app-name]-db

resources:
  - name: [app-name]-db
    type: com.sap.xs.hdi-container
    parameters:
      service: hana
      service-plan: hdi-shared

  - name: [app-name]-uaa
    type: org.cloudfoundry.managed-service
    parameters:
      service: xsuaa
      service-plan: application
      path: ./xs-security.json

---FILE: README.md---
# [App Name] — SAP CAP Node.js Application
Generated: {_TODAY}

## Local Development
```bash
npm install
cds watch   # SQLite in-memory, no HANA needed locally
```

## Deploy to SAP BTP
```bash
npm install -g @sap/cds-dk mbt
cds build --production
mbt build
cf deploy mta_archives/[app]_1.0.0.mtar
```

## API Endpoints
Base URL: `[BTP URL]/api/v1/[service]`
[List all entity endpoints and actions]

## Running Tests
```bash
npm test
```"""


# ──────────────────────────────────────────────────────────────
# CAP JAVA CODE GENERATION
# ──────────────────────────────────────────────────────────────

CAP_JAVA_SYSTEM = """You are an expert SAP CAP Java developer with deep Spring Boot, SAP BTP, and enterprise Java expertise. You write production-ready CAP Java services following SAP best practices."""


def cap_java_prompt(technical_spec: str) -> str:
    return f"""Based on the SAP Technical Specification below, generate a complete SAP CAP Java application.

TECHNICAL SPECIFICATION:
{technical_spec}

Produce every file using ---FILE: path--- markers. All code must be complete and compilable.

---FILE: pom.xml---
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <artifactId>spring-boot-starter-parent</artifactId>
    <groupId>org.springframework.boot</groupId>
    <version>3.3.0</version>
  </parent>
  <groupId>com.sap.[appname]</groupId>
  <artifactId>[app-name]</artifactId>
  <version>1.0.0</version>
  [Complete pom.xml with CAP Java SDK 3.x, Spring Boot 3, HANA client, XSUAA dependencies]
</project>

---FILE: db/schema.cds---
[Complete CDS data model — same rigour as CAP Node.js schema]

---FILE: srv/service.cds---
[Complete CDS service definition with all entities, actions, functions]

---FILE: srv/src/main/java/com/sap/[appname]/Application.java---
package com.sap.[appname];

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {{
    public static void main(String[] args) {{
        SpringApplication.run(Application.class, args);
    }}
}}

---FILE: srv/src/main/java/com/sap/[appname]/handlers/[Service]Handler.java---
package com.sap.[appname].handlers;

import com.sap.cds.services.handler.EventHandler;
import com.sap.cds.services.handler.annotations.Before;
import com.sap.cds.services.handler.annotations.On;
import com.sap.cds.services.handler.annotations.After;
import com.sap.cds.services.handler.annotations.ServiceName;
import org.springframework.stereotype.Component;
import com.sap.cds.ql.Select;
import com.sap.cds.services.cds.CdsCreateEventContext;
import com.sap.cds.services.cds.CdsReadEventContext;

@Component
@ServiceName("[ServiceName]")
public class [Service]Handler implements EventHandler {{

    [Fully implemented @Before, @On, @After handlers for all entities and actions]
    [Include field validation, business logic, error handling]
}}

---FILE: srv/src/main/resources/application.yaml---
spring:
  config:
    activate:
      on-profile: default
cds:
  datasource:
    auto-config:
      enabled: true
logging:
  level:
    com.sap.cds: INFO
    com.sap.[appname]: DEBUG

---FILE: srv/src/test/java/com/sap/[appname]/[Service]HandlerTest.java---
[JUnit 5 tests for all handler methods — fully implemented]

---FILE: xs-security.json---
[Same structure as CAP Node.js xs-security.json]

---FILE: mta.yaml---
[MTA descriptor for CAP Java — java_buildpack, hdi-container, xsuaa resources]

---FILE: README.md---
# [App Name] — SAP CAP Java Application
Generated: {_TODAY}

## Build & Run Locally
```bash
mvn spring-boot:run
```
Endpoint: http://localhost:8080/

## Deploy to SAP BTP
```bash
mbt build
cf deploy mta_archives/[app]_1.0.0.mtar
```

## Running Tests
```bash
mvn test
```"""
