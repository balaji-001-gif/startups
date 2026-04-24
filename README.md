# 🚀 StartupOS for ERPNext v15+

> **The all-in-one Frappe/ERPNext custom application for Indian Startups** — DPIIT Compliance, Fundraising OS, Cap Table Management, Financial Intelligence & AI Advisory — built natively on Frappe Framework v15.

[![ERPNext](https://img.shields.io/badge/ERPNext-v15%2B-blue)](https://erpnext.com)
[![Frappe](https://img.shields.io/badge/Frappe-v15%2B-orange)](https://frappeframework.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![India](https://img.shields.io/badge/Built%20For-India-orange)](https://startupindia.gov.in)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Why StartupOS](#why-startupos)
- [Modules](#modules)
- [DocTypes Reference](#doctypes-reference)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Troubleshooting Installation](#troubleshooting-installation)
- [Demo Data](#demo-data)
- [Configuration](#configuration)
- [Module Guide](#module-guide)
- [API Reference](#api-reference)
- [Roles & Permissions](#roles--permissions)
- [Scheduled Tasks](#scheduled-tasks)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**StartupOS** is a purpose-built Frappe Framework custom application designed to sit on top of ERPNext v15+. It addresses the unique operational, legal, and financial lifecycle needs of Indian startups — from DPIIT recognition and ROC compliance, through fundraising pipeline and cap table management, to AI-powered financial forecasting and one-click investor reporting.

---

## Why StartupOS?

| Problem | StartupOS Solution |
|---|---|
| DPIIT/ROC compliance scattered across emails & Excel | Unified compliance hub with calendar & AI alerts |
| No structured fundraising pipeline tool | Investor CRM with 7-stage deal pipeline |
| Cap table managed in spreadsheets | Digital cap table with full transaction history |
| Burn rate/runway computed manually | Live GL-synced runway model with 3 scenarios |
| Legal docs in Google Drive folders | Governed contract repository with expiry alerts |
| No AI advisor for Indian startup law | RAG-powered assistant trained on MCA/SEBI/RBI docs |

---

## Modules

| # | Module | Key Feature |
|---|---|---|
| 1 | **Startup Setup & Compliance Hub** | DPIIT tracker, ROC calendar, self-certification, compliance score |
| 2 | **Fundraising OS** | Investor CRM, 7-stage pipeline, pitch vault, AI investor updates |
| 3 | **Cap Table & Equity Management** | Digital cap table, ESOP grants, dilution simulator |
| 4 | **Financial Tracking & Runway Intelligence** | Burn rate, 3-scenario runway, unit economics, budget vs actuals |
| 5 | **Legal & Governance** | Board minutes, FEMA/FDI compliance, IP tracker, contract repository |
| 6 | **AI Startup Assistant & Insights** | RAG chatbot trained on Indian startup law & finance |
| 7 | **Reports & Exports** | Investor PDFs, DPIIT report, cap table exports, audit pack |

---

## DocTypes Reference

### Module 1 — Compliance (6 DocTypes)

| DocType | Type | Purpose |
|---|---|---|
| `DPIIT Application` | Master | Track DPIIT recognition application & document checklist |
| `DPIIT Document Checklist` | Child Table | Documents checklist for DPIIT Application |
| `Incorporation Checklist` | Master | INC-20A, PAN, TAN, GST, Shops & Establishment status |
| `Regulatory Calendar` | Master | ROC/MCA/GST/TDS/ITR filing deadlines with status |
| `Compliance Score` | Master | AI-computed 0–100 health score per company |
| `Compliance Alert Setting` | Settings | Per-company WhatsApp/email alert configuration |

### Module 2 — Fundraising (5 DocTypes)

| DocType | Type | Purpose |
|---|---|---|
| `Investor` | Master | Investor CRM — Angel / VC / PE profiles |
| `Investor Contact` | Master | Individual contact persons at investor firms |
| `Fundraising Opportunity` | Transaction | 7-stage deal pipeline (Intro → Closed Won) |
| `Investor Update` | Transaction | Monthly/quarterly investor update drafts |
| `Pitch Deck Vault` | Master | Version-controlled pitch deck storage |

### Module 3 — Cap Table (5 DocTypes)

| DocType | Type | Purpose |
|---|---|---|
| `Shareholder` | Master | Shareholders with auto-computed ownership % |
| `Equity Transaction` | Transaction | Immutable log of issuance/transfer/buyback/cancellation |
| `ESOP Grant` | Transaction | Employee stock option grants with vesting schedule |
| `ESOP Vesting Schedule` | Child Table | Monthly vesting events (Pending/Vested/Exercised) |
| `Share Certificate` | Transaction | Physical share certificate records with numbering |

### Module 4 — Financial (4 DocTypes)

| DocType | Type | Purpose |
|---|---|---|
| `Runway Model` | Master | Live burn rate & 3-scenario runway (Base/Optimistic/Pessimistic) |
| `Unit Economics` | Master | ARPU, CAC, LTV, Churn, Payback, Magic Number |
| `Budget Plan` | Transaction | Budget vs actuals with line-item breakdown |
| `Budget Plan Item` | Child Table | Per-category budget and actual amounts |

### Module 5 — Governance (5 DocTypes)

| DocType | Type | Purpose |
|---|---|---|
| `Board Meeting` | Transaction | Schedule and track board meetings with agenda |
| `Board Minutes` | Transaction | Minutes and resolutions linked to meetings |
| `Contract Document` | Master | Contract repository with party, expiry & file |
| `IP Tracker` | Master | Patents, trademarks, copyrights with status |
| `FEMA FDI Tracker` | Transaction | FC-GPR filing, RBI approval & valuation reports |

### Module 6 — AI Assistant (2 DocTypes)

| DocType | Type | Purpose |
|---|---|---|
| `AI Chat Session` | Master | Persisted chat sessions with context injection |
| `AI Chat Message` | Child Table | Individual messages (user / assistant) per session |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│     Founder Portal | Investor Portal | Admin | Mobile PWA       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      API GATEWAY                                │
│         Frappe REST API | Webhooks | OAuth2 | JWT Auth          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                          │
│  Compliance Engine | Fundraising Pipeline | Cap Table Engine    │
│  Financial Engine  | AI Advisory                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       DATA LAYER                                │
│  DocTypes (MariaDB) | File Vault (S3) | Vector Store | Redis    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   INTEGRATION LAYER                             │
│    MCA21 | GSTN | Razorpay | WhatsApp | Tally Export | Zoho    │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|---|---|
| Backend | Frappe v15 (Python 3.11+) |
| ERP Core | ERPNext v15 |
| Database | MariaDB 10.6+ |
| Cache/Queue | Redis 6+ |
| File Storage | S3 / Local / Nextcloud |
| AI/ML | LangChain + OpenAI / Claude |
| Vector Store | Chroma (local) / Pinecone (cloud) |
| PDF Engine | WeasyPrint + Jinja2 |
| Notifications | Frappe Email + WhatsApp API |

---

## Prerequisites

- **Ubuntu** 22.04 LTS
- **Python** 3.11+
- **Node.js** 18 LTS
- **MariaDB** 10.6+
- **Redis** 6+
- **ERPNext** v15.x (fully set up)
- **bench CLI** (latest)

---

## Installation

### Step 1: Set up ERPNext (skip if already installed)

```bash
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
bench new-site startup.example.com
bench get-app erpnext --branch version-15
bench --site startup.example.com install-app erpnext
```

### Step 2: Install StartupOS

```bash
bench get-app startup_os https://github.com/balaji-001-gif/startups.git
bench --site startup.example.com install-app startup_os
```

### Step 3: Run Migrations

```bash
bench --site startup.example.com migrate
```

### Step 4: Install Python Dependencies (Optional AI/PDF modules)

```bash
cd apps/startup_os
pip install -r requirements.txt
```

> **Note:** The heavy AI/ML packages (`langchain`, `openai`, `chromadb`) are **optional**. The app installs and runs fully without them. You only need them if you are enabling the AI Assistant module.

### Step 5: Build Assets & Restart

```bash
bench build --app startup_os
bench restart
```

---

## Troubleshooting Installation

### ❌ `Directory not empty` error on `bench get-app`

A previous failed install left an `apps/startup_os` directory behind.

```bash
rm -rf /home/frappe/f15-bk/apps/startups
rm -rf /home/frappe/f15-bk/apps/startup_os
bench get-app startup_os https://github.com/balaji-001-gif/startups.git
```

---

### ❌ `No module named 'startup_os.reports'`

This was fixed in v0.0.1+. `Reports` was incorrectly listed in `modules.txt`. Make sure you have the latest code:

```bash
cd apps/startup_os && git pull
bench --site <site> install-app startup_os
```

---

### ❌ `No module named 'startup_os.api'`

Fixed in v0.0.1+. The top-level `api.py` was missing. Pull the latest code:

```bash
cd apps/startup_os && git pull
```

---

### ❌ `No module named 'startup_os.compliance.doctype.regulatory_calendar.regulatory_calendar'`

Frappe v15 requires a Python controller `.py` file alongside every DocType `.json`. These were added in v0.0.1+. Pull the latest:

```bash
cd apps/startup_os && git pull
bench --site <site> install-app startup_os
```

---

### ❌ `Duplicate entry 'Compliance' for key 'PRIMARY'`

Previous failed installs left `Module Def` rows in the database. Fix:

```bash
# Option 1 — use --force flag
bench --site <site> install-app startup_os --force

# Option 2 — clean orphaned records manually
bench --site <site> mariadb
```

```sql
DELETE FROM `tabModule Def` WHERE app_name = 'startup_os';
DELETE FROM `tabInstalled Application` WHERE app_name = 'startup_os';
exit;
```

```bash
bench --site <site> install-app startup_os
bench --site <site> migrate
bench restart
```

---

### ❌ `frappe-ui was not found in the package registry`

Fixed in v0.0.1+. `frappe-ui` is a JavaScript library, not a Python package and was incorrectly placed in `requirements.txt`. The fix is already in the latest code.

---

## Demo Data

StartupOS ships with a realistic **Indian SaaS startup** demo dataset for quick evaluation.

### What's Included

| Module | Demo Content |
|---|---|
| **Compliance** | DPIIT Certificate (Recognized) · Full Incorporation Checklist · 7 ROC/GST/TDS/ITR filings · Compliance Score **87/100** |
| **Fundraising** | 3 Investors (Angel, Blume Ventures, Sequoia Capital) · 5 deals across all 7 pipeline stages |
| **Cap Table** | 4 Shareholders — Founders (43%, 34.5%), Angel (14.4%), ESOP Pool (8.6%) on fully-diluted basis |
| **Financial** | Runway Model — ₹90L cash · ₹5L/mo burn · **18-month runway** · Unit Economics — ARPU ₹4,999 · CAC ₹25K · **LTV:CAC 8x** |
| **Governance** | 2 Board Meetings (1 completed with minutes + resolutions) · 3 Contracts · Trademark · FEMA FDI Tracker |
| **Reports** | Draft Investor Update with real MRR narrative and metrics |

### Load Demo Data

```bash
# Pull latest (must have app installed first)
cd apps/startup_os && git pull

# Load demo data
bench --site <site> execute startup_os.setup.demo.run
```

### Remove Demo Data

```bash
bench --site <site> execute startup_os.setup.demo.remove
```

---

## Configuration

### Site Config Parameters

```bash
# AI Provider (at least one required for AI Assistant module)
bench --site <site> set-config openai_api_key "sk-..."
bench --site <site> set-config anthropic_api_key "sk-ant-..."

# Vector Store (default: chroma — local, zero-config)
bench --site <site> set-config vector_store "chroma"
# OR for Pinecone (cloud):
bench --site <site> set-config vector_store "pinecone"
bench --site <site> set-config pinecone_api_key "..."

# File Storage (optional — defaults to local)
bench --site <site> set-config s3_bucket "your-bucket"
bench --site <site> set-config s3_region "ap-south-1"
bench --site <site> set-config aws_access_key_id "..."
bench --site <site> set-config aws_secret_access_key "..."

# WhatsApp Notifications (optional)
bench --site <site> set-config whatsapp_api_token "..."
bench --site <site> set-config whatsapp_phone_id "..."
```

---

## Module Guide

### Module 1 — Startup Setup & Compliance Hub

**Regulatory Filing Coverage:**

| Filing | Form | Due Date |
|---|---|---|
| Annual Return | MGT-7 / MGT-7A | 60 days from AGM |
| Financial Statements | AOC-4 | 30 days from AGM |
| Auditor Appointment | ADT-1 | 15 days from AGM |
| Director Changes | DIR-12 | 30 days of event |
| GST Returns | GSTR-1 / 3B | 11th / 20th monthly |
| TDS Return | 26Q / 24Q | 31st after quarter |
| Income Tax | ITR-6 | 31 Oct (audited) |

**AI Alerts:** The compliance engine runs daily and sends WhatsApp/email alerts at 30, 7, and 1 day before each deadline.

Seed the regulatory calendar for your company with:
```bash
bench --site <site> execute startup_os.compliance.api.seed_regulatory_calendar --kwargs '{"company": "Your Company Name"}'
```

---

### Module 2 — Fundraising OS

**7-Stage Pipeline:**
```
Intro → Meeting → Due Diligence → Term Sheet → Closing → Closed Won / Passed
```

**Automated Actions per Stage:**
- **Due Diligence:** Notify founders, share data room access
- **Term Sheet:** Lock cap table version, notify legal team
- **Closed Won:** Update cap table, dispatch investor update to all existing investors

---

### Module 3 — Cap Table & Equity Management

**ESOP Grant Workflow:**
```
Create Grant → Set Vesting Schedule → Generate Grant Letter PDF
  → Employee Acceptance → Vesting Runs Monthly → Exercise Window
  → Exercise Request → Share Allotment → Cap Table Update
```

**Three Runway Scenarios:**
```
Base Case:     avg of last 3 months burn
Optimistic:    base × 0.75  (25% efficiency gain)
Pessimistic:   base × 1.30  (30% cost overrun)
```

---

### Module 6 — AI Startup Assistant

**Sample Queries:**
```
"Am I eligible for 80-IAC tax exemption?"
"What documents do I need for a seed round?"
"What will my founder ownership be after raising ₹5Cr at ₹20Cr pre-money?"
"When is my next ROC filing due?"
"Has my ESOP cliff date passed for [employee name]?"
"What is the FEMA compliance for a US investor?"
```

---

## API Reference

All APIs use Frappe's standard REST pattern with API Key + API Secret headers:

```http
Authorization: token {api_key}:{api_secret}
Content-Type: application/json
```

### Compliance

```http
GET  /api/method/startup_os.compliance.api.get_compliance_score?company=YourCompany
GET  /api/method/startup_os.compliance.api.get_upcoming_deadlines?company=YourCompany&days=30
GET  /api/method/startup_os.compliance.api.get_dpiit_status?company=YourCompany
POST /api/method/startup_os.compliance.api.mark_filing_complete
     Body: {"filing_name": "REGCAL-001"}
POST /api/method/startup_os.compliance.api.seed_regulatory_calendar
     Body: {"company": "YourCompany"}
```

### Fundraising

```http
GET  /api/method/startup_os.fundraising.api.get_pipeline_summary?company=YourCompany
GET  /api/method/startup_os.fundraising.api.get_investor_list
POST /api/method/startup_os.fundraising.api.move_opportunity
     Body: {"opportunity_name": "FO-001", "new_stage": "Term Sheet"}
POST /api/method/startup_os.fundraising.api.generate_investor_update
     Body: {"company": "YourCompany", "period_type": "Monthly"}
```

### Cap Table

```http
GET  /api/method/startup_os.cap_table.api.get_fully_diluted?company=YourCompany&as_of_date=2025-01-01
POST /api/method/startup_os.cap_table.api.run_dilution_scenario
     Body: {"company": "YourCompany", "new_amount": 30000000, "pre_money": 200000000}
POST /api/method/startup_os.cap_table.api.record_equity_transaction
     Body: {"company": "YourCompany", "shareholder": "SH-001", "transaction_type": "Issuance", ...}
```

### Financial

```http
GET  /api/method/startup_os.financial.api.get_runway?company=YourCompany
GET  /api/method/startup_os.financial.api.get_burn_trend?company=YourCompany&months=6
GET  /api/method/startup_os.financial.api.get_unit_economics?company=YourCompany
POST /api/method/startup_os.financial.api.sync_burn_rate
     Body: {"company": "YourCompany"}
POST /api/method/startup_os.financial.api.update_unit_economics
     Body: {"company": "YourCompany", "arpu": 4999, "cac": 25000, "churn_rate": 2.5}
```

### Governance

```http
GET  /api/method/startup_os.governance.api.get_board_meeting_list?company=YourCompany
GET  /api/method/startup_os.governance.api.get_expiring_contracts?company=YourCompany&days=30
POST /api/method/startup_os.governance.api.create_board_meeting
     Body: {"company": "YourCompany", "meeting_date": "2025-06-15", "agenda": "..."}
POST /api/method/startup_os.governance.api.submit_minutes
     Body: {"meeting_name": "BM-001", "minutes": "...", "resolutions": "..."}
```

### AI Assistant

```http
POST /api/method/startup_os.ai_assistant.api.chat
     Body: {"message": "What is my compliance score?", "session_id": "sess_xxx"}
GET  /api/method/startup_os.ai_assistant.api.get_chat_history?session_id=sess_xxx
```

---

## Roles & Permissions

Roles are auto-created on installation via `after_install`.

| Role | Description |
|---|---|
| `Startup Founder` | Full access to all modules except admin functions |
| `Startup CFO` | Full access to financial modules; read-only cap table |
| `Startup Legal` | Full access to governance & compliance; read-only financials |
| `Startup Investor` | Portal access — own rows in cap table, invited data room only |
| `Startup Admin` | Super-user with delete rights |

Assign via: **HR > User > User Roles**

---

## Scheduled Tasks

Configured in `hooks.py`:

```python
scheduler_events = {
    "daily": [
        "startup_os.financial.forecasting.update_all_runway_models",
        "startup_os.compliance.utils.check_upcoming_deadlines",
        "startup_os.cap_table.calculator.recompute_vesting_schedules",
    ],
    "weekly": [
        "startup_os.ai_assistant.rag_engine.refresh_knowledge_base",
        "startup_os.compliance.utils.compute_compliance_scores",
    ],
    "monthly": [
        "startup_os.financial.forecasting.compute_unit_economics",
        "startup_os.fundraising.report_generator.prompt_investor_update",
    ]
}
```

---

## Repository Structure

```
startup_os/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
└── startup_os/
    ├── __init__.py          # App version (0.0.1)
    ├── hooks.py             # App config, scheduler, doc_events
    ├── modules.txt          # Module registry
    ├── patches.txt          # Migration patches
    ├── install.py           # after_install: creates roles, seeds calendar
    ├── api.py               # Top-level scheduler stubs
    ├── compliance/
    │   ├── doctype/         # 6 DocTypes
    │   ├── api.py           # Compliance REST endpoints
    │   └── utils.py         # Compliance scoring & deadline alerts
    ├── fundraising/
    │   ├── doctype/         # 5 DocTypes
    │   ├── api.py           # Pipeline & investor update endpoints
    │   └── report_generator.py
    ├── cap_table/
    │   ├── doctype/         # 5 DocTypes
    │   ├── api.py           # Fully-diluted view & dilution simulator
    │   └── calculator.py    # Vesting schedule & ownership recomputation
    ├── financial/
    │   ├── doctype/         # 4 DocTypes
    │   ├── api.py           # Runway, burn trend, unit economics
    │   └── forecasting.py   # GL-synced burn rate calculations
    ├── governance/
    │   ├── doctype/         # 5 DocTypes
    │   └── api.py           # Board meetings, contracts, FEMA
    ├── ai_assistant/
    │   ├── doctype/         # 2 DocTypes
    │   ├── api.py           # Chat endpoint & session history
    │   ├── rag_engine.py    # RAG engine with context injection
    │   └── vector_store.py  # Chroma / Pinecone abstraction
    ├── workspace/
    │   └── startup_os/
    │       └── startup_os.json  # Frappe Desk workspace
    ├── patches/
    │   └── v0_0/
    │       └── setup_roles.py
    └── setup/
        └── demo.py          # Demo data loader/remover
```

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Follow [Frappe Contribution Guidelines](https://github.com/frappe/frappe/wiki/Contribution-Guidelines)
4. Write tests in `startup_os/tests/`
5. Run tests: `bench --site test.localhost run-tests --app startup_os`
6. Submit a Pull Request

### Coding Standards
- Follow PEP 8 for Python
- Use `frappe.throw()` for user-facing errors (never raw exceptions)
- All DocTypes must have `autoname` defined
- All API methods must use `@frappe.whitelist()` decorator
- Every DocType `.json` must have a corresponding `.py` controller (even if empty)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Support

- 📧 Email: support@startupos.in
- 📖 Docs: https://docs.startupos.in
- 🐛 Issues: https://github.com/balaji-001-gif/startups/issues
- 💬 Community: https://discuss.startupos.in

---

*Built with ❤️ for Indian Startups | Powered by Frappe Framework*
