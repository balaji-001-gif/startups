import frappe
from frappe.utils import flt, add_months

@frappe.whitelist()
def get_runway(company):
	"""Get the current runway model for a company."""
	runway = frappe.get_all("Runway Model",
		filters={"company": company},
		fields=["cash_balance", "base_burn", "runway_base", "runway_optimistic", "runway_pessimistic", "last_updated"],
		limit=1
	)
	if not runway:
		return {"error": "No runway model found. Run sync first."}

	r = runway[0]
	return {
		"cash_balance": r.cash_balance,
		"monthly_burn": r.base_burn,
		"scenarios": {
			"base": {"runway_months": r.runway_base, "description": "3-month avg burn"},
			"optimistic": {"runway_months": r.runway_optimistic, "description": "25% efficiency gain (burn × 0.75)"},
			"pessimistic": {"runway_months": r.runway_pessimistic, "description": "30% cost overrun (burn × 1.30)"}
		},
		"last_updated": str(r.last_updated)
	}

@frappe.whitelist()
def sync_burn_rate(company, period=None):
	"""Manually trigger runway sync for a company."""
	from startup_os.financial.forecasting import update_runway_model
	update_runway_model(company)
	frappe.db.commit()
	return {"status": "success", "company": company, "message": "Runway model updated."}

@frappe.whitelist()
def get_burn_trend(company, months=6):
	"""Get burn rate trend over the last N months."""
	from frappe.utils import today, add_months, get_first_day, get_last_day
	import datetime

	trend = []
	for i in range(int(months), 0, -1):
		period_start = add_months(today(), -i)
		month_label = frappe.utils.formatdate(period_start, "MMM yyyy")

		# Rough burn proxy: expenses in that month
		expenses = frappe.db.sql("""
			SELECT SUM(debit - credit) as net
			FROM `tabGL Entry`
			WHERE company = %s
			  AND YEAR(posting_date) = YEAR(%s)
			  AND MONTH(posting_date) = MONTH(%s)
			  AND is_cancelled = 0
		""", (company, period_start, period_start), as_dict=True)

		trend.append({
			"month": month_label,
			"burn": flt(expenses[0].net) if expenses and expenses[0].net else 0
		})

	return trend

@frappe.whitelist()
def get_unit_economics(company):
	"""Get unit economics for a company."""
	ue = frappe.get_all("Unit Economics",
		filters={"company": company},
		fields=["arpu", "cac", "ltv", "churn_rate", "payback_period", "magic_number"],
		limit=1
	)
	if not ue:
		return {}
	u = ue[0]
	ltv_cac = round(flt(u.ltv) / flt(u.cac), 2) if u.cac else None
	return {
		"arpu": u.arpu,
		"cac": u.cac,
		"ltv": u.ltv,
		"churn_rate": u.churn_rate,
		"payback_period": u.payback_period,
		"magic_number": u.magic_number,
		"ltv_cac_ratio": ltv_cac
	}

@frappe.whitelist()
def update_unit_economics(company, arpu, cac, churn_rate):
	"""Update unit economics and trigger computed fields."""
	from startup_os.financial.forecasting import compute_unit_economics
	arpu = flt(arpu)
	cac = flt(cac)
	churn_rate = flt(churn_rate)

	ue_name = frappe.db.get_value("Unit Economics", {"company": company})
	if ue_name:
		ue = frappe.get_doc("Unit Economics", ue_name)
	else:
		ue = frappe.new_doc("Unit Economics")
		ue.company = company

	ue.arpu = arpu
	ue.cac = cac
	ue.churn_rate = churn_rate

	# Calculated fields
	if churn_rate > 0:
		ue.ltv = arpu / (churn_rate / 100.0)
	if cac and arpu:
		ue.payback_period = cac / arpu

	ue.save()
	frappe.db.commit()
	return {"status": "success", "ltv": ue.ltv, "payback_period": ue.payback_period}
