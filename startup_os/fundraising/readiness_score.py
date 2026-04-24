# Funding Readiness Scoring Engine
# Scores 5 dimensions (0–20 each) = 100 total

import frappe
from frappe.utils import flt, now


@frappe.whitelist()
def compute_score(company):
    """
    Compute funding readiness score for a company.
    Scores 5 dimensions: Team, Product, Traction, Legal, Finance (20 each = 100).
    Returns a saved FundingReadinessScore doc.
    """
    scores = {}

    # ── 1. Team (20 pts) ─────────────────────────────────────────
    team_score = 0
    team_notes = []
    directors = frappe.get_all("Company Director",
                               filters={"company": company, "status": "Active"})
    if len(directors) >= 2:
        team_score += 8; team_notes.append("✅ 2+ active directors")
    elif len(directors) == 1:
        team_score += 4; team_notes.append("⚠️ Only 1 director")
    else:
        team_notes.append("❌ No directors registered")

    # DIR-8, DIR-2 consent
    consented = frappe.db.count("Company Director",
                                {"company": company, "dir_8_signed": 1, "status": "Active"})
    if len(directors) > 0 and consented == len(directors):
        team_score += 6; team_notes.append("✅ All directors have signed DIR-8 & DIR-2")
    elif consented > 0:
        team_score += 3; team_notes.append("⚠️ Some director consents pending")
    else:
        team_notes.append("❌ Director consent docs missing")

    # ESOP pool exists (signals team-building mindset)
    esop_grants = frappe.db.count("ESOP Grant")
    if esop_grants > 0:
        team_score += 6; team_notes.append(f"✅ ESOP grants in place ({esop_grants} granted)")
    else:
        team_notes.append("⚠️ No ESOP grants — consider creating an ESOP pool")

    scores["team"] = min(team_score, 20)

    # ── 2. Product (20 pts) ──────────────────────────────────────
    product_score = 0
    product_notes = []

    # IP Tracker
    ip_items = frappe.get_all("IP Tracker", filters={"company": company})
    if ip_items:
        product_score += 10; product_notes.append(f"✅ IP assets tracked ({len(ip_items)} items)")
    else:
        product_notes.append("⚠️ No IP assets registered")

    # Pitch deck vault
    decks = frappe.get_all("Pitch Deck Vault")
    if decks:
        product_score += 10; product_notes.append(f"✅ Pitch deck available ({len(decks)} version(s))")
    else:
        product_notes.append("❌ No pitch deck uploaded")

    scores["product"] = min(product_score, 20)

    # ── 3. Traction (20 pts) ─────────────────────────────────────
    traction_score = 0
    traction_notes = []

    ue = frappe.db.get_value("Unit Economics", {"company": company},
                             ["arpu", "ltv", "cac", "churn_rate", "magic_number"], as_dict=True)
    if ue:
        ltv_cac = flt(ue.ltv) / flt(ue.cac) if flt(ue.cac) else 0
        if ltv_cac >= 3:
            traction_score += 8; traction_notes.append(f"✅ LTV:CAC = {ltv_cac:.1f}x (healthy)")
        elif ltv_cac >= 1.5:
            traction_score += 4; traction_notes.append(f"⚠️ LTV:CAC = {ltv_cac:.1f}x (needs improvement)")
        else:
            traction_notes.append(f"❌ LTV:CAC = {ltv_cac:.1f}x (below threshold)")

        if flt(ue.churn_rate) <= 2:
            traction_score += 6; traction_notes.append(f"✅ Churn = {ue.churn_rate}% (low)")
        elif flt(ue.churn_rate) <= 5:
            traction_score += 3; traction_notes.append(f"⚠️ Churn = {ue.churn_rate}% (moderate)")
        else:
            traction_notes.append(f"❌ Churn = {ue.churn_rate}% (high)")

        if flt(ue.magic_number) >= 0.75:
            traction_score += 6; traction_notes.append(f"✅ Magic Number = {ue.magic_number:.2f}")
        else:
            traction_notes.append(f"⚠️ Magic Number = {ue.magic_number:.2f if ue.magic_number else 'N/A'}")
    else:
        traction_notes.append("❌ Unit economics not set up — add ARPU, CAC, LTV")

    scores["traction"] = min(traction_score, 20)

    # ── 4. Legal & Compliance (20 pts) ───────────────────────────
    legal_score = 0
    legal_notes = []

    comp = frappe.db.get_value("Compliance Score", {"company": company}, "score")
    if comp and flt(comp) >= 80:
        legal_score += 10; legal_notes.append(f"✅ Compliance Score = {comp}/100")
    elif comp and flt(comp) >= 60:
        legal_score += 6; legal_notes.append(f"⚠️ Compliance Score = {comp}/100")
    else:
        legal_notes.append(f"❌ Compliance Score = {comp or 'N/A'}/100")

    dpiit = frappe.db.get_value("DPIIT Application", {"company": company}, "status")
    if dpiit == "Recognized":
        legal_score += 6; legal_notes.append("✅ DPIIT Recognized")
    else:
        legal_notes.append(f"⚠️ DPIIT status: {dpiit or 'Not applied'}")

    sha = frappe.db.count("Contract Document",
                          {"company": company, "contract_name": ["like", "%Shareholders%"]})
    if sha > 0:
        legal_score += 4; legal_notes.append("✅ Shareholders Agreement in place")
    else:
        legal_notes.append("⚠️ No Shareholders Agreement found")

    scores["legal"] = min(legal_score, 20)

    # ── 5. Finance & Runway (20 pts) ─────────────────────────────
    finance_score = 0
    finance_notes = []

    rwy = frappe.db.get_value("Runway Model", {"company": company},
                              ["runway_base", "cash_balance", "base_burn"], as_dict=True)
    if rwy:
        if flt(rwy.runway_base) >= 18:
            finance_score += 10; finance_notes.append(f"✅ Runway = {rwy.runway_base:.1f} months (healthy)")
        elif flt(rwy.runway_base) >= 12:
            finance_score += 6; finance_notes.append(f"⚠️ Runway = {rwy.runway_base:.1f} months (raise soon)")
        else:
            finance_notes.append(f"❌ Runway = {rwy.runway_base:.1f} months (critical)")
    else:
        finance_notes.append("❌ No runway model — add cash balance and burn rate")

    budget = frappe.db.count("Budget Plan", {"company": company})
    if budget > 0:
        finance_score += 6; finance_notes.append("✅ Budget plans documented")
    else:
        finance_notes.append("⚠️ No budget plans — add budget vs actuals")

    cap_txns = frappe.db.count("Equity Transaction", {"company": company})
    if cap_txns > 0:
        finance_score += 4; finance_notes.append(f"✅ Cap table maintained ({cap_txns} transactions)")
    else:
        finance_notes.append("⚠️ No equity transactions recorded")

    scores["finance"] = min(finance_score, 20)

    # ── Overall ───────────────────────────────────────────────────
    overall = sum(scores.values())

    # Stage recommendation
    if overall >= 85:
        stage = "Series A Ready 🚀"
    elif overall >= 70:
        stage = "Pre-Series A Ready 📈"
    elif overall >= 55:
        stage = "Seed Ready 🌱"
    elif overall >= 40:
        stage = "Angel Ready 🤝"
    else:
        stage = "Foundation Building 🏗️ — Not yet investor-ready"

    # Create or update the score doc
    existing = frappe.db.get_value("Funding Readiness Score", {"company": company})
    if existing:
        doc = frappe.get_doc("Funding Readiness Score", existing)
    else:
        doc = frappe.new_doc("Funding Readiness Score")
        doc.company = company

    doc.computed_on = now()
    doc.overall_score = overall
    doc.stage_recommendation = stage
    doc.team_score = scores["team"]
    doc.team_notes = "\n".join(team_notes)
    doc.product_score = scores["product"]
    doc.product_notes = "\n".join(product_notes)
    doc.traction_score = scores["traction"]
    doc.traction_notes = "\n".join(traction_notes)
    doc.legal_score = scores["legal"]
    doc.legal_notes = "\n".join(legal_notes)
    doc.finance_score = scores["finance"]
    doc.finance_notes = "\n".join(finance_notes)
    doc.insert(ignore_permissions=True) if not existing else doc.save(ignore_permissions=True)

    frappe.db.commit()
    return {
        "score": overall,
        "stage": stage,
        "breakdown": {k: v for k, v in scores.items()},
        "doc": doc.name
    }
