"""
StartupOS Demo Data Setup
=========================
Populates a realistic Indian startup scenario for demonstration.

Usage:
    bench --site <your-site> execute startup_os.setup.demo.run

What it creates:
    - A sample Indian SaaS startup company
    - DPIIT Application (Recognized)
    - Incorporation Checklist (complete)
    - Regulatory Calendar (7 filings)
    - 3 Investors (Angel + VC)
    - 5 Fundraising Opportunities across stages
    - 4 Shareholders with equity transactions
    - 2 ESOP Grants with vesting schedules
    - Runway Model (18-month runway)
    - Unit Economics (SaaS metrics)
    - 2 Board Meetings (1 completed with minutes)
    - 3 Contracts (SHA, NDA, Vendor)
    - 1 IP Tracker (Trademark)
    - 1 FEMA FDI Tracker
    - 1 Investor Update (Draft)
    - 1 Compliance Score
"""

import frappe
from frappe.utils import today, add_months, add_days, getdate
import datetime

COMPANY_NAME = "BizAxl Technologies Private Limited"
DEMO_TAG = "__startup_os_demo__"


def run():
    """Main entry point. Run via: bench execute startup_os.setup.demo.run"""
    frappe.set_user("Administrator")

    if _demo_already_loaded():
        print("✅ Demo data is already loaded. Skipping.")
        return

    print("🚀 StartupOS: Loading demo data...")

    company = _create_company()
    _create_dpiit_application(company)
    _create_incorporation_checklist(company)
    _create_regulatory_calendar(company)
    investors = _create_investors()
    _create_fundraising_opportunities(company, investors)
    shareholders = _create_shareholders(company)
    _create_equity_transactions(company, shareholders)
    _create_esop_grants()
    _create_runway_model(company)
    _create_unit_economics(company)
    _create_board_meetings(company)
    _create_contracts(company)
    _create_ip_tracker(company)
    _create_fema_tracker(company, investors)
    _create_investor_update(company)
    _create_compliance_score(company)

    frappe.db.commit()
    print("\n✅ StartupOS demo data loaded successfully!")
    print(f"   Company: {COMPANY_NAME}")
    print("   Login to your ERPNext and navigate to StartupOS workspace.")
    print("   To remove demo data run: bench execute startup_os.setup.demo.remove")


def remove():
    """Remove all demo data. bench execute startup_os.setup.demo.remove"""
    frappe.set_user("Administrator")
    doctypes_to_clear = [
        "Compliance Score", "Investor Update", "FEMA FDI Tracker", "IP Tracker",
        "Contract Document", "Board Minutes", "Board Meeting", "Unit Economics",
        "Runway Model", "ESOP Grant", "Equity Transaction", "Shareholder",
        "Fundraising Opportunity", "Investor Contact", "Investor", "Pitch Deck Vault",
        "Regulatory Calendar", "Compliance Alert Setting", "Compliance Score",
        "Incorporation Checklist", "DPIIT Application",
    ]
    for dt in doctypes_to_clear:
        try:
            frappe.db.delete(dt, {"company": COMPANY_NAME})
        except Exception:
            pass

    # Company
    if frappe.db.exists("Company", COMPANY_NAME):
        frappe.delete_doc("Company", COMPANY_NAME, force=True)

    frappe.db.commit()
    print("✅ Demo data removed.")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _demo_already_loaded():
    return frappe.db.exists("Company", COMPANY_NAME)


def _make(doctype, **kwargs):
    """Create and insert a document, return its name."""
    doc = frappe.new_doc(doctype)
    doc.update(kwargs)
    doc.insert(ignore_permissions=True, ignore_mandatory=True)
    return doc


# ── Company ───────────────────────────────────────────────────────────────────

def _create_company(abbr="BTL"):
    print("  📌 Creating company...")
    if frappe.db.exists("Company", COMPANY_NAME):
        return COMPANY_NAME

    company = frappe.new_doc("Company")
    company.company_name = COMPANY_NAME
    company.abbr = abbr
    company.default_currency = "INR"
    company.country = "India"
    company.insert(ignore_permissions=True)
    print(f"     Company: {COMPANY_NAME}")
    return COMPANY_NAME


# ── Module 1: Compliance ──────────────────────────────────────────────────────

def _create_dpiit_application(company):
    print("  📋 Creating DPIIT Application...")
    doc = _make("DPIIT Application",
        company=company,
        application_number="DIPP123456",
        status="Recognized",
        date_of_application=add_months(today(), -18),
        certificate_number="DIPP-2023-12345",
        recognition_date=add_months(today(), -15),
        documents=[
            {"document_name": "Incorporation Certificate", "required": 1, "uploaded": 1},
            {"document_name": "PAN Card", "required": 1, "uploaded": 1},
            {"document_name": "Audited Financial Statements", "required": 1, "uploaded": 1},
            {"document_name": "Pitch Deck / Business Plan", "required": 1, "uploaded": 1},
            {"document_name": "Self Certification", "required": 1, "uploaded": 1},
        ]
    )
    print(f"     DPIIT: {doc.name} — Status: Recognized")


def _create_incorporation_checklist(company):
    print("  📋 Creating Incorporation Checklist...")
    _make("Incorporation Checklist",
        company=company,
        status="Complete",
        inc_20a=1,
        pan=1,
        tan=1,
        gst=1,
        shops_and_establishment=1,
        other_registrations="MSME Registration, Startup India Portal"
    )
    print("     Incorporation checklist: Complete")


def _create_regulatory_calendar(company):
    print("  📅 Creating Regulatory Calendar...")
    year = datetime.date.today().year
    filings = [
        {"filing_name": "Annual Return", "form_type": "MGT-7 / MGT-7A",
         "due_date": f"{year}-11-29", "status": "Upcoming"},
        {"filing_name": "Financial Statements Filing", "form_type": "AOC-4",
         "due_date": f"{year}-10-29", "status": "Upcoming"},
        {"filing_name": "Auditor Appointment", "form_type": "ADT-1",
         "due_date": f"{year}-10-14", "status": "Upcoming"},
        {"filing_name": "GST Return - GSTR-1 (Apr)", "form_type": "GSTR-1",
         "due_date": f"{year}-05-11", "status": "Filed", "completion_date": f"{year}-05-10"},
        {"filing_name": "GST Return - GSTR-3B (Apr)", "form_type": "GSTR-3B",
         "due_date": f"{year}-05-20", "status": "Filed", "completion_date": f"{year}-05-18"},
        {"filing_name": "TDS Return Q4", "form_type": "26Q / 24Q",
         "due_date": f"{year}-05-31", "status": "Upcoming"},
        {"filing_name": "Income Tax Return", "form_type": "ITR-6",
         "due_date": f"{year}-10-31", "status": "Upcoming"},
    ]
    for f in filings:
        if not frappe.db.exists("Regulatory Calendar",
                                {"company": company, "filing_name": f["filing_name"]}):
            _make("Regulatory Calendar", company=company, **f)
    print(f"     Created {len(filings)} regulatory calendar entries")


# ── Module 2: Fundraising ─────────────────────────────────────────────────────

def _create_investors():
    print("  💰 Creating Investors...")
    investors = [
        {
            "investor_name": "Arjun Mehta (Angel)",
            "investor_type": "Angel",
            "contact_email": "arjun.mehta@example.com",
            "website": "https://arjunmehta.in"
        },
        {
            "investor_name": "Blume Ventures",
            "investor_type": "VC",
            "contact_email": "deals@blumeventures.com",
            "website": "https://blumeventures.com"
        },
        {
            "investor_name": "Sequoia Capital India",
            "investor_type": "VC",
            "contact_email": "india@sequoiacap.com",
            "website": "https://sequoiacap.com"
        }
    ]
    names = []
    for inv_data in investors:
        if not frappe.db.exists("Investor", {"investor_name": inv_data["investor_name"]}):
            doc = _make("Investor", **inv_data)
            names.append(doc.name)
            print(f"     Investor: {inv_data['investor_name']}")
        else:
            names.append(frappe.db.get_value("Investor",
                         {"investor_name": inv_data["investor_name"]}))
    return names


def _create_fundraising_opportunities(company, investors):
    print("  🎯 Creating Fundraising Pipeline...")
    opportunities = [
        {
            "investor": investors[0],
            "stage": "Closed Won",
            "amount": 5000000,
            "probability": 100,
            "close_date": add_months(today(), -12),
            "notes": "<p>Seed round closed. Arjun led the round with Rs. 50L at Rs. 3Cr pre-money.</p>"
        },
        {
            "investor": investors[1],
            "stage": "Term Sheet",
            "amount": 30000000,
            "probability": 80,
            "close_date": add_days(today(), 45),
            "notes": "<p>Pre-Series A. Blume offered Rs. 3Cr at Rs. 20Cr pre-money. Due diligence ongoing.</p>"
        },
        {
            "investor": investors[2],
            "stage": "Due Diligence",
            "amount": 50000000,
            "probability": 40,
            "close_date": add_days(today(), 90),
            "notes": "<p>Sequoia exploring entry. Very early conversations, data room shared.</p>"
        },
        {
            "investor": investors[0],
            "stage": "Meeting",
            "amount": 10000000,
            "probability": 30,
            "close_date": add_days(today(), 30),
            "notes": "<p>Follow-on from Arjun. Second meeting scheduled.</p>"
        },
        {
            "investor": investors[1],
            "stage": "Intro",
            "amount": 20000000,
            "probability": 10,
            "close_date": add_days(today(), 120),
            "notes": "<p>Intro email sent via mutual connection.</p>"
        }
    ]
    for opp in opportunities:
        _make("Fundraising Opportunity", company=company, **opp)
    print(f"     Created {len(opportunities)} pipeline deals")


# ── Module 3: Cap Table ───────────────────────────────────────────────────────

def _create_shareholders(company):
    print("  📊 Creating Shareholders...")
    shareholders_data = [
        {"shareholder_name": "Ravi Kumar (Founder)", "shareholder_type": "Founder"},
        {"shareholder_name": "Priya Singh (Co-Founder)", "shareholder_type": "Founder"},
        {"shareholder_name": "Arjun Mehta (Angel)", "shareholder_type": "Investor"},
        {"shareholder_name": "ESOP Pool", "shareholder_type": "Company"},
    ]
    names = []
    for sh_data in shareholders_data:
        if not frappe.db.exists("Shareholder",
                                {"shareholder_name": sh_data["shareholder_name"],
                                 "company": company}):
            doc = _make("Shareholder", company=company, **sh_data)
            names.append(doc.name)
        else:
            names.append(frappe.db.get_value("Shareholder",
                         {"shareholder_name": sh_data["shareholder_name"], "company": company}))
    print(f"     Created {len(shareholders_data)} shareholders")
    return names


def _create_equity_transactions(company, shareholders):
    print("  📈 Creating Equity Transactions...")
    transactions = [
        # Founder shares at incorporation (FV Rs. 10)
        {"shareholder": shareholders[0], "transaction_type": "Issuance",
         "share_type": "Equity", "quantity": 500000, "price_per_share": 10,
         "date": add_months(today(), -30)},
        {"shareholder": shareholders[1], "transaction_type": "Issuance",
         "share_type": "Equity", "quantity": 400000, "price_per_share": 10,
         "date": add_months(today(), -30)},
        # ESOP Pool
        {"shareholder": shareholders[3], "transaction_type": "Issuance",
         "share_type": "Equity", "quantity": 100000, "price_per_share": 10,
         "date": add_months(today(), -30)},
        # Angel Round — CCPS at Rs. 30
        {"shareholder": shareholders[2], "transaction_type": "Issuance",
         "share_type": "CCPS", "quantity": 166667, "price_per_share": 30,
         "date": add_months(today(), -12)},
    ]
    for tx in transactions:
        tx["total_value"] = tx["quantity"] * tx["price_per_share"]
        doc = _make("Equity Transaction", company=company, **tx)

    print("     Created 4 equity transactions")
    print("     Cap table: Ravi 43.0% | Priya 34.5% | Angel 14.4% | ESOP 8.6% (FD)")


def _create_esop_grants():
    print("  🎖  Creating ESOP Grants...")
    # Check if Employee exists, if not skip
    employees = frappe.get_all("Employee", fields=["name"], limit=2)
    if not employees:
        print("     ⚠️  No employees found — skipping ESOP grants (add employees first)")
        return

    grants = [
        {
            "employee": employees[0].name,
            "quantity": 5000,
            "grant_date": add_months(today(), -18),
            "vesting_start_date": add_months(today(), -18),
            "cliff_period_months": 12,
            "vesting_period_months": 48,
        }
    ]
    if len(employees) > 1:
        grants.append({
            "employee": employees[1].name,
            "quantity": 3000,
            "grant_date": add_months(today(), -6),
            "vesting_start_date": add_months(today(), -6),
            "cliff_period_months": 12,
            "vesting_period_months": 48,
        })

    for g in grants:
        doc = _make("ESOP Grant", **g)
        print(f"     ESOP Grant: {g['quantity']} options → {g['employee']}")


# ── Module 4: Financial ───────────────────────────────────────────────────────

def _create_runway_model(company):
    print("  💸 Creating Runway Model...")
    if frappe.db.exists("Runway Model", {"company": company}):
        return
    _make("Runway Model",
        company=company,
        cash_balance=9000000,        # Rs. 90 Lakh in bank
        base_burn=500000,            # Rs. 5 Lakh/month burn
        runway_base=18.0,            # 18 months base
        runway_optimistic=24.0,      # 24 months (25% efficiency gain)
        runway_pessimistic=13.85,    # ~14 months (30% cost overrun)
        last_updated=frappe.utils.now()
    )
    print("     Cash: ₹90L | Burn: ₹5L/mo | Runway: 18mo (base)")


def _create_unit_economics(company):
    print("  📐 Creating Unit Economics (SaaS)...")
    if frappe.db.exists("Unit Economics", {"company": company}):
        return
    _make("Unit Economics",
        company=company,
        arpu=4999,          # Rs. 4,999/month ARPU
        cac=25000,          # Rs. 25,000 CAC
        churn_rate=2.5,     # 2.5% monthly churn
        ltv=199960,         # ARPU / Churn = 4999 / 0.025
        payback_period=5.0, # CAC / ARPU = 5 months
        magic_number=1.2
    )
    print("     ARPU: ₹4,999 | CAC: ₹25K | LTV: ₹2L | Payback: 5mo | LTV:CAC = 8x")


# ── Module 5: Governance ─────────────────────────────────────────────────────

def _create_board_meetings(company):
    print("  🏛  Creating Board Meetings...")
    # Past meeting (completed)
    m1 = _make("Board Meeting",
        company=company,
        meeting_date=add_months(today(), -3),
        status="Completed",
        agenda="""<h3>Agenda — Q4 2024 Board Meeting</h3>
<ol>
<li>Approval of quarterly financials</li>
<li>Fundraising update: Pre-Series A process</li>
<li>Product roadmap H1 2025</li>
<li>ESOP pool expansion discussion</li>
<li>AOB</li>
</ol>"""
    )
    # Add minutes for completed meeting
    _make("Board Minutes",
        meeting=m1.name,
        minutes="""<h3>Minutes — Board Meeting</h3>
<p><strong>Attendees:</strong> Ravi Kumar, Priya Singh, Arjun Mehta</p>
<p>The board reviewed Q4 financials. Revenue grew 35% QoQ to Rs. 18L MRR. The fundraising process is on track with Blume at term sheet stage.</p>""",
        resolutions="""1. Q4 financials approved unanimously.
2. Management authorized to negotiate and sign term sheet with Blume Ventures.
3. ESOP pool to be expanded by 50,000 shares pending legal advice."""
    )
    # Upcoming meeting
    _make("Board Meeting",
        company=company,
        meeting_date=add_days(today(), 14),
        status="Scheduled",
        agenda="""<h3>Agenda — Q1 2025 Board Meeting</h3>
<ol>
<li>Q1 financials review</li>
<li>Blume Ventures term sheet approval</li>
<li>Key hires update</li>
<li>DPIIT renewal planning</li>
</ol>"""
    )
    print("     Created 2 board meetings (1 completed with minutes, 1 upcoming)")


def _create_contracts(company):
    print("  📄 Creating Contracts...")
    contracts = [
        {
            "contract_name": "Shareholders Agreement — Seed Round",
            "party": "Arjun Mehta",
            "expiry_date": add_months(today(), 36),
            "status": "Active"
        },
        {
            "contract_name": "Mutual NDA — Blume Ventures",
            "party": "Blume Ventures",
            "expiry_date": add_months(today(), 6),
            "status": "Active"
        },
        {
            "contract_name": "AWS Cloud Credits Agreement",
            "party": "Amazon Web Services",
            "expiry_date": add_months(today(), 8),
            "status": "Active"
        },
    ]
    for c in contracts:
        _make("Contract Document", company=company, **c)
    print(f"     Created {len(contracts)} contracts")


def _create_ip_tracker(company):
    print("  ™  Creating IP Tracker...")
    _make("IP Tracker",
        company=company,
        ip_name="BizAxl",
        ip_type="Trademark",
        status="Pending",
        application_number="4512345",
        filing_date=add_months(today(), -6),
        expiry_date=add_months(today(), 114)  # 10 years from filing
    )
    print("     Trademark: BizAxl — Status: Pending")


def _create_fema_tracker(company, investors):
    print("  🌐 Creating FEMA/FDI Tracker...")
    _make("FEMA FDI Tracker",
        company=company,
        investor=investors[0],
        round_name="Seed Round",
        status="Compliant",
        amount_inr=5000000,
        currency="INR",
        fc_gpr_status="Acknowledged",
        rbi_approval_required=0,
        rbi_approval_status="Not Required",
        fdi_notes="<p>Angel investment from Indian resident. FC-GPR filed and acknowledged by NBFC-ND-SI authorized dealer.</p>"
    )
    print("     FEMA tracker: Seed Round — Compliant")


# ── Module 6 / Reports ────────────────────────────────────────────────────────

def _create_investor_update(company):
    print("  📧 Creating Investor Update Draft...")
    period_start = add_months(today(), -1)
    _make("Investor Update",
        company=company,
        status="Draft",
        period_start=period_start,
        period_end=today(),
        update_text=f"""<h2>Monthly Investor Update — {frappe.utils.formatdate(today(), 'MMMM yyyy')}</h2>

<h3>🔑 TL;DR</h3>
<ul>
<li>MRR hit <strong>₹18.5L</strong> (+8% MoM)</li>
<li>Runway: <strong>18 months</strong> at current burn</li>
<li>Pre-Series A: Blume Ventures at <strong>Term Sheet</strong> stage</li>
</ul>

<h3>📈 Key Metrics</h3>
<table>
<tr><td>MRR</td><td>₹18.5 Lakhs</td></tr>
<tr><td>MoM Growth</td><td>8%</td></tr>
<tr><td>Active Customers</td><td>37</td></tr>
<tr><td>Churn Rate</td><td>2.5%</td></tr>
<tr><td>Burn Rate</td><td>₹5.0 Lakhs/mo</td></tr>
<tr><td>Cash in Bank</td><td>₹90 Lakhs</td></tr>
<tr><td>Runway</td><td>18 months</td></tr>
</table>

<h3>🎯 Wins</h3>
<ul>
<li>Signed 3 new enterprise customers (HDFC subsidiary, Mphasis, Wipro BPO)</li>
<li>Product: Launched bulk invoice module — top requested feature</li>
<li>Hired Head of Sales (ex-Zoho)</li>
</ul>

<h3>⚠️  Challenges</h3>
<ul>
<li>1 customer churned (budget cut) — ₹80K ARR impact</li>
<li>Server infra costs up 15% — migrating to reserved instances</li>
</ul>

<h3>🏦 Fundraising</h3>
<p>Pre-Series A process underway. Blume Ventures at term sheet stage. Targeting close in 45 days.</p>

<h3>📅 Next Month Priorities</h3>
<ol>
<li>Close Blume term sheet</li>
<li>Launch mobile app (beta)</li>
<li>Q1 Board Meeting — approval of financials</li>
</ol>"""
    )
    print("     Investor update draft created for current period")


def _create_compliance_score(company):
    print("  🏆 Creating Compliance Score...")
    if frappe.db.exists("Compliance Score", {"company": company}):
        return
    import json
    _make("Compliance Score",
        company=company,
        score=87,
        last_computed=frappe.utils.now(),
        score_breakdown=json.dumps([
            "DPIIT Recognition: ✅ (+20)",
            "Incorporation Checklist: ✅ (+20)",
            "GST Filings: ✅ Filed on time (+15)",
            "TDS Returns: ✅ Filed on time (+12)",
            "Annual Return MGT-7: ⏳ Due in 6 months (+10)",
            "AOC-4 Financial Statements: ⏳ Due in 6 months (+10)",
            "ITR Filing: ⏳ Due in 6 months (+0)",
            "Board Meetings: ⚠️  Only 2 this year (-13)",
        ])
    )
    print("     Compliance Score: 87/100")


if __name__ == "__main__":
    run()
