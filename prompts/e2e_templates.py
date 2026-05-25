from datetime import date

_TODAY = date.today().strftime("%B %d, %Y")
_TODAY_ISO = date.today().strftime("%Y-%m-%d")

# ──────────────────────────────────────────────────────────────
# FUNCTIONAL SPECIFICATION SYSTEM (UPGRADED - SAP + AI READY)
# ──────────────────────────────────────────────────────────────

FUNCTIONAL_SPEC_SYSTEM = """You are a Senior SAP Functional Consultant with 25+ years of experience across SAP ECC and S/4HANA, including deep expertise in MM, SD, FI, CO, EWM, WM, PP, QM, PM and SAP integration scenarios.

You specialize in:
- Writing high-quality Functional Specifications (FS)
- Designing SAP enhancements, interfaces, RF processes, and migration solutions
- Handling S/4HANA simplification impacts (SAP Notes, removed functionality)
- Designing automation and AI-enabled SAP processes

Your documents act as a contract between Business and IT and must be:
- Structured and precise
- Technically accurate
- Implementation-ready for ABAP developers
- Aligned with SAP best practices and real project scenarios
"""


def functional_spec_prompt(business_requirement: str) -> str:
    return f"""Based on the SAP business requirement below, produce a complete, professional SAP Functional Specification document.

BUSINESS REQUIREMENT:
{business_requirement}

Output the full document using this exact structure. Use real SAP tables, T-codes, enhancement techniques, and practical logic wherever applicable.

═══════════════════════════════════════════════════════════════════
SAP FUNCTIONAL SPECIFICATION DOCUMENT
═══════════════════════════════════════════════════════════════════

1. DOCUMENT HEADER
─────────────────
Document Title  : [Derived clearly from requirement]
Project Name    : [Derived or generic SAP project]
SAP Module(s)   : [e.g. MM / EWM / SD / FI / Cross-module]
Version         : 1.0  |  Status: Draft
Date            : {_TODAY}
Prepared by     : SAP AI Assistant

2. DOCUMENT CONTROL
────────────────────
2.1 Purpose
Explain the purpose of this FS clearly (enhancement, interface, automation, AI solution).

2.2 Scope
Define what is covered (process, system, transactions, modules).

2.3 Assumptions & Constraints
- Master data availability
- SAP configuration dependencies
- Any SAP Note / S/4 behavior constraints

2.4 Out of Scope
- Clearly define exclusions

3. EXECUTIVE SUMMARY
─────────────────────
Write 2–3 strong paragraphs covering:
- Business problem
- SAP limitation or gap (if any)
- Proposed solution (enhancement/interface/AI)
- Business benefit (automation, accuracy, compliance, efficiency)

4. BUSINESS PROCESS OVERVIEW
──────────────────────────────

4.1 As-Is Process (Current State)
Describe real business process and system behavior including:
- Transactions (e.g. MIGO, RFUI, ME31L)
- Pain points (manual effort, errors, restrictions)

4.2 To-Be Process (Future State)
Describe SAP process after enhancement:
- Automation / validation / AI decision
- System-driven actions

4.3 Process Flow Narrative
Provide step-by-step flow:
Step 1 → Step 2 → Step 3 → Final Output

5. SAP MODULE & TRANSACTION MAPPING
──────────────────────────────────────
| SAP Module | Transaction Code | Description | Responsible Role |
|------------|-----------------|-------------|-----------------|

Include real examples like:
- MIGO, /SCWM/RFUI, ME31L, VL31N, custom Z programs

Master Data Objects:
- Material Master (MARA, MARC)
- Vendor Master (LFA1)
- Purchasing Info (EINA)
- Others based on scenario

6. FUNCTIONAL REQUIREMENTS
────────────────────────────

FR-001: [Requirement Title]
  Description     : Clear business requirement
  Business Rule   : Detailed logic (thresholds, validation, calculations)
  SAP Object      : Table / FM / BAdI / Program (e.g. EKPO, T160M, /SCWM/TO_READ_HU)
  Priority        : High / Medium / Low
  Acceptance Criteria:
    ✓ System performs expected action
    ✓ No manual intervention required
    ✓ Error handled properly

(Include multiple FRs if needed)

7. DETAILED FUNCTIONAL LOGIC (MANDATORY – CORE SECTION)
────────────────────────────────────────────────────────

Step 1: Trigger/Event
- T-code / Batch Job / Interface / RF Screen

Step 2: Data Retrieval
- Tables (EKKO, EKPO, MARC, /SCWM/* etc.)

Step 3: Validation Logic
- Threshold (TVARVC)
- Status checks
- Error conditions

Step 4: Core Processing Logic
Use structured logic like:

IF condition A:
   perform action A
ELSE:
   perform action B

Include:
- Calculations (quantity/value)
- Currency handling (if any)
- Function modules (e.g. CONVERT_TO_LOCAL_CURRENCY)

Step 5: Decision / AI Logic (IMPORTANT)
If applicable, include:

| Input Data | Logic Type | Decision |
|-----------|-----------|----------|
| SAP data | Rule / ML | Output |

Example:
- Predict exhaustion
- Suggest action
- Auto-trigger process

Step 6: Update Logic
- Tables updated
- Documents created (PO, SA, WT, Material Doc)

Step 7: Exception Handling
- Error → Warning conversion (if applicable)
- Logging
- Retry logic

8. BUSINESS PROCESS FLOW TABLE
──────────────────────────
| Step | Actor | SAP Action | T-Code | Output |
|------|------|-----------|--------|--------|

9. TECHNICAL OBJECTS
────────────────────
| Object Type | Name |
|------------|------|
| Program | Z_* |
| Enhancement | BAdI / User Exit / Implicit |
| Function Module | |
| Class/Method | |

10. INPUT / OUTPUT SPECIFICATIONS
───────────────────────────────────

10.1 Input Data:
| Field Name | Technical Name | Mandatory | Source | Validation |

10.2 Output:
| Output | Type | Description |
|--------|------|------------|
| Document | SAP | |
| Email | Notification | |
| Report | ALV | |

11. NOTIFICATIONS / ALERTS
──────────────────────────

Trigger Condition:
[When email or alert fires]

Recipient Logic:
- MRP Controller (T024D)
- Distribution List (TVARVC)

Include:
- Subject
- Email body summary

12. SAP INTEGRATION POINTS
────────────────────────────
| Module | Description | Data |
|--------|------------|------|

Examples:
- MM ↔ FI
- EWM ↔ MM
- External Interface

13. USER ROLES & AUTHORIZATION
────────────────────────────────
| Role | Description | T-Codes |

14. BATCH JOB / EXECUTION
──────────────────────────
| Job Name | Frequency | Description |

15. EXCEPTION HANDLING
────────────────────────
| Scenario | System Action |

16. DATA MIGRATION (IF APPLICABLE)
────────────────────────────────────
- Legacy mapping
- Upload approach

17. ASSUMPTIONS & LIMITATIONS
─────────────────────────────

18. TEST SCENARIOS
──────────────────
| Scenario | Expected Result |

19. OPEN ISSUES
────────────────
| Issue | Owner | Status |

20. CHANGE HISTORY
───────────────────
| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | {_TODAY_ISO} | SAP AI Assistant | Initial Version |

═══════════════════════════════════════════════════════════════════

Ensure:
✔ Real SAP examples are used  
✔ Logic is implementation-ready  
✔ Suitable for ABAP developer handover  
✔ Covers migration + enhancement + AI scenario  
✔ No vague or generic descriptions
"""

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
