import frappe
from frappe.utils import flt, today, getdate

@frappe.whitelist()
def get_fully_diluted(company, as_of_date=None):
	"""
	Get the fully diluted cap table as of a given date.
	Includes: Equity shares, CCPS, Warrants, ESOP Granted (vested + unvested).
	"""
	as_of = getdate(as_of_date) if as_of_date else getdate(today())

	# 1. Equity Transactions
	transactions = frappe.get_all("Equity Transaction",
		filters={
			"company": company,
			"date": ["<=", as_of],
			"transaction_type": ["in", ["Issuance", "Transfer"]]
		},
		fields=["shareholder", "quantity", "share_type", "price_per_share", "date"]
	)

	# 2. Aggregate by Shareholder
	equity_map = {}
	for t in transactions:
		if t.shareholder not in equity_map:
			equity_map[t.shareholder] = {"equity": 0, "ccps": 0, "warrants": 0}
		st = (t.share_type or "Equity").lower()
		if st == "equity":
			equity_map[t.shareholder]["equity"] += flt(t.quantity)
		elif st == "ccps":
			equity_map[t.shareholder]["ccps"] += flt(t.quantity)
		elif st == "warrants":
			equity_map[t.shareholder]["warrants"] += flt(t.quantity)

	# Buybacks and Cancellations
	reductions = frappe.get_all("Equity Transaction",
		filters={
			"company": company,
			"date": ["<=", as_of],
			"transaction_type": ["in", ["Buyback", "Cancellation"]]
		},
		fields=["shareholder", "quantity", "share_type"]
	)
	for r in reductions:
		if r.shareholder in equity_map:
			st = (r.share_type or "Equity").lower()
			if st == "equity":
				equity_map[r.shareholder]["equity"] -= flt(r.quantity)

	# 3. ESOP Grants (fully diluted includes all granted, vested or not)
	esop_grants = frappe.get_all("ESOP Grant",
		filters={"grant_date": ["<=", as_of]},
		fields=["employee", "quantity"]
	)
	esop_map = {}
	for g in esop_grants:
		esop_map[g.employee] = esop_map.get(g.employee, 0) + flt(g.quantity)

	# 4. Compute totals
	total_equity = sum(v["equity"] for v in equity_map.values())
	total_ccps = sum(v["ccps"] for v in equity_map.values())
	total_warrants = sum(v["warrants"] for v in equity_map.values())
	total_esop = sum(esop_map.values())
	total_fully_diluted = total_equity + total_ccps + total_warrants + total_esop

	# 5. Build rows
	rows = []
	for sh, holdings in equity_map.items():
		sh_total = holdings["equity"] + holdings["ccps"] + holdings["warrants"]
		rows.append({
			"type": "Shareholder",
			"name": sh,
			"equity": holdings["equity"],
			"ccps": holdings["ccps"],
			"warrants": holdings["warrants"],
			"esop": 0,
			"total": sh_total,
			"ownership_pct": round(sh_total / total_fully_diluted * 100, 4) if total_fully_diluted else 0
		})

	for emp, qty in esop_map.items():
		rows.append({
			"type": "ESOP",
			"name": emp,
			"equity": 0,
			"ccps": 0,
			"warrants": 0,
			"esop": qty,
			"total": qty,
			"ownership_pct": round(qty / total_fully_diluted * 100, 4) if total_fully_diluted else 0
		})

	return {
		"as_of_date": str(as_of),
		"total_shares": total_equity,
		"total_ccps": total_ccps,
		"total_warrants": total_warrants,
		"total_esop_pool": total_esop,
		"total_fully_diluted": total_fully_diluted,
		"rows": rows
	}

@frappe.whitelist()
def run_dilution_scenario(company, new_amount, pre_money):
	"""
	Simulate dilution from a new funding round.
	new_amount: INR amount being raised
	pre_money: pre-money valuation in INR
	"""
	new_amount = flt(new_amount)
	pre_money = flt(pre_money)
	post_money = pre_money + new_amount

	new_investor_pct = round(new_amount / post_money * 100, 4)
	existing_pct = round(100 - new_investor_pct, 4)

	# Get current fully diluted cap table
	current = get_fully_diluted(company)
	total_fd = flt(current.get("total_fully_diluted", 0))

	# Calculate new share price if we know total shares
	price_per_share = pre_money / total_fd if total_fd else 0
	new_shares = new_amount / price_per_share if price_per_share else 0
	new_total = total_fd + new_shares

	diluted_rows = []
	for row in current.get("rows", []):
		diluted_rows.append({
			"name": row["name"],
			"type": row["type"],
			"current_pct": row["ownership_pct"],
			"post_dilution_pct": round(row["total"] / new_total * 100, 4) if new_total else 0,
			"dilution_impact": round(row["ownership_pct"] - row["total"] / new_total * 100, 4) if new_total else 0
		})

	return {
		"pre_money": pre_money,
		"new_amount_raised": new_amount,
		"post_money": post_money,
		"new_investor_ownership_pct": new_investor_pct,
		"existing_owner_diluted_to_pct": existing_pct,
		"price_per_share": round(price_per_share, 2),
		"new_shares_issued": round(new_shares),
		"new_total_shares": round(new_total),
		"diluted_cap_table": diluted_rows
	}

@frappe.whitelist()
def record_equity_transaction(company, shareholder, transaction_type, share_type, quantity, price_per_share, date=None):
	"""Create an equity transaction record."""
	from frappe.utils import today as t
	doc = frappe.new_doc("Equity Transaction")
	doc.company = company
	doc.shareholder = shareholder
	doc.transaction_type = transaction_type
	doc.share_type = share_type
	doc.quantity = flt(quantity)
	doc.price_per_share = flt(price_per_share)
	doc.total_value = flt(quantity) * flt(price_per_share)
	doc.date = date or t()
	doc.insert()
	frappe.db.commit()
	return {"status": "success", "name": doc.name}
