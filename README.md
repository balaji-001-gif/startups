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
- [Modules](#modules)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Module Guide](#module-guide)
- [API Reference](#api-reference)
- [Roles & Permissions](#roles--permissions)
- [Scheduled Tasks](#scheduled-tasks)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**StartupOS** is a purpose-built Frappe Framework custom application designed to sit on top of ERPNext v15+. It addresses the unique operational, legal, and financial lifecycle needs of Indian startups — from DPIIT recognition and ROC compliance, through fundraising pipeline and cap table management, to AI-powered financial forecasting and one-click investor reporting.

### Why StartupOS?

| Problem | StartupOS Solution |
|---|---|
| DPIIT/ROC compliance is scattered across emails & Excel | Unified compliance hub with calendar & AI alerts |
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
| 5 | **Legal & Governance** | Board minutes, FEMA compliance, IP tracker, contract repository |
| 6 | **AI Startup Assistant & Insights** | RAG chatbot trained on Indian startup law & finance |
| 7 | **Reports & Exports** | Investor PDFs, DPIIT report, cap table exports, audit pack |

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
| Frontend | Vue 3 + Frappe UI |
| PDF Engine | WeasyPrint + Jinja2 |
| Notifications | Frappe Email + WhatsApp API |

---

## Prerequisites

Before installing StartupOS, ensure your environment meets:

- **Ubuntu** 22.04 LTS
- **Python** 3.11+
- **Node.js** 18 LTS
- **MariaDB** 10.6+
- **Redis** 6+
- **ERPNext** v15.x (fully set up)
- **bench CLI** (latest)

```bash
pip install frappe-bench
```

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
# Clone the app
bench get-app startup_os https://github.com/balaji-001-gif/startups.git

# Install on your site
bench --site startup.example.com install-app startup_os
```

### Step 3: Run Database Migrations

```bash
bench --site startup.example.com migrate
```

### Step 4: Install Python Dependencies

```bash
cd apps/startup_os
pip install -r requirements.txt
```

### Step 5: Build Frontend Assets

```bash
bench build --app startup_os
```

### Step 6: Restart Services

```bash
bench restart
```

---

## Configuration

### site_config.json Parameters

After installation, set the following in your site configuration:

```bash
# AI Provider Keys (at least one required for AI module)
bench --site startup.example.com set-config openai_api_key "sk-..."
bench --site startup.example.com set-config anthropic_api_key "sk-ant-..."

# Vector Store (choose one)
bench --site startup.example.com set-config vector_store "chroma"  # or "pinecone"
bench --site startup.example.com set-config pinecone_api_key "..."  # if using Pinecone

# File Storage (optional — defaults to local)
bench --site startup.example.com set-config s3_bucket "your-bucket"
bench --site startup.example.com set-config s3_region "ap-south-1"
bench --site startup.example.com set-config aws_access_key_id "..."
bench --site startup.example.com set-config aws_secret_access_key "..."

# WhatsApp Notifications (optional)
bench --site startup.example.com set-config whatsapp_api_token "..."
bench --site startup.example.com set-config whatsapp_phone_id "..."
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

*Built with ❤️ for Indian Startups | Powered by Frappe Framework*.
