"""
StartupOS – Central Notification Engine
========================================
Handles all outbound notifications (Email, Frappe In-App, WhatsApp stub)
for every module in the StartupOS application.

Modules covered:
  - Compliance    : deadline reminders, overdue alerts, score drops
  - Cap Table     : ESOP vesting events, equity transactions
  - Fundraising   : stage changes, investor update prompts
  - Financial     : low-runway warnings, burn-rate alerts
  - Governance    : board meeting reminders
  - AI Assistant  : weekly insight digest
"""

import frappe
from frappe.utils import nowdate, add_days, getdate, date_diff
from frappe import _


# ─────────────────────────────────────────────
# HELPER UTILITIES
# ─────────────────────────────────────────────

def _get_role_emails(roles):
	"""Return a list of email addresses for users with any of the given roles."""
	if isinstance(roles, str):
		roles = [roles]
	emails = set()
	for role in roles:
		users = frappe.get_all(
			"Has Role",
			filters={"role": role, "parenttype": "User"},
			fields=["parent"],
		)
		for u in users:
			email = frappe.db.get_value("User", u.parent, "email")
			if email and not email.endswith("example.com"):
				emails.add(email)
	return list(emails)


def _get_company_alert_settings(company):
	"""Fetch alert channel preferences for a company. Returns a dict."""
	settings = frappe.get_all(
		"Compliance Alert Setting",
		filters={"company": company},
		fields=["send_email", "send_whatsapp", "reminder_days"],
		limit=1,
	)
	if settings:
		s = settings[0]
		return {
			"send_email": bool(s.send_email),
			"send_whatsapp": bool(s.send_whatsapp),
			"reminder_days": [int(d.strip()) for d in (s.reminder_days or "30,7,1").split(",")],
		}
	# Defaults when no setting record exists
	return {"send_email": True, "send_whatsapp": False, "reminder_days": [30, 7, 1]}


def _send_email(recipients, subject, template_or_message, args=None, is_html=True):
	"""Thin wrapper around frappe.sendmail with error isolation."""
	if not recipients:
		return
	try:
		if is_html and args:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=frappe.render_template(template_or_message, args),
			)
		else:
			frappe.sendmail(
				recipients=recipients,
				subject=subject,
				message=template_or_message,
			)
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"StartupOS Email Error: {subject}")


def _send_whatsapp_stub(phone, message):
	"""
	WhatsApp integration stub.
	Replace with actual Twilio / Meta Cloud API call.
	"""
	frappe.logger().info(f"[WhatsApp STUB] To: {phone} | Msg: {message[:80]}")


def _create_inapp_notification(user, subject, document_type=None, document_name=None):
	"""Create a Frappe ToDo-style in-app notification for a specific user."""
	try:
		notif = frappe.new_doc("Notification Log")
		notif.subject = subject
		notif.for_user = user
		notif.type = "Alert"
		if document_type:
			notif.document_type = document_type
		if document_name:
			notif.document_name = document_name
		notif.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "StartupOS: In-App Notification Error")


# ─────────────────────────────────────────────
# COMPLIANCE NOTIFICATIONS
# ─────────────────────────────────────────────

def notify_compliance_deadline(filing, days_left):
	"""
	Send deadline reminder for a Regulatory Calendar entry.
	Called by compliance.utils.check_upcoming_deadlines (daily scheduler).
	"""
	company = filing.get("company")
	prefs = _get_company_alert_settings(company)

	if days_left not in prefs["reminder_days"]:
		return

	urgency = "🔴 URGENT" if days_left <= 1 else ("🟡 ACTION REQUIRED" if days_left <= 7 else "🔔 REMINDER")
	subject = f"{urgency}: {filing.filing_name} due in {days_left} day(s)"
	message = f"""
	<p>Dear Team,</p>
	<p>This is an automated reminder from <strong>StartupOS Compliance Hub</strong>.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Filing</b></td><td>{filing.filing_name}</td></tr>
	  <tr><td><b>Form Type</b></td><td>{filing.get('form_type','—')}</td></tr>
	  <tr><td><b>Company</b></td><td>{company}</td></tr>
	  <tr><td><b>Due Date</b></td><td>{filing.due_date}</td></tr>
	  <tr><td><b>Days Remaining</b></td><td><b>{days_left}</b></td></tr>
	</table>
	<p>Please file on time to avoid penalties. Login to StartupOS → Compliance Hub to mark as Filed.</p>
	"""

	if prefs["send_email"]:
		recipients = _get_role_emails(["Compliance Officer", "Startup Admin"])
		_send_email(recipients, subject, message)

	if prefs["send_whatsapp"]:
		wa_msg = f"{urgency}: {filing.filing_name} for {company} is due in {days_left} day(s). File by {filing.due_date}."
		_send_whatsapp_stub("", wa_msg)  # phone lookup to be wired

	# In-app for all Compliance Officers
	for email in _get_role_emails("Compliance Officer"):
		user = frappe.db.get_value("User", {"email": email}, "name")
		if user:
			_create_inapp_notification(user, subject, "Regulatory Calendar", filing.get("name"))

	# Track reminders sent
	frappe.db.set_value("Regulatory Calendar", filing.get("name"), "reminders_sent",
		(filing.get("reminders_sent") or 0) + 1)


def notify_compliance_overdue(filing):
	"""Alert when a filing flips to Overdue status."""
	subject = f"⚠️ OVERDUE Compliance Filing: {filing.filing_name}"
	message = f"""
	<p><strong>ALERT:</strong> The regulatory filing <b>{filing.filing_name}</b> for
	<b>{filing.company}</b> is now <span style="color:red;">OVERDUE</span>.</p>
	<p>Due date was: <b>{filing.due_date}</b>. Immediate action is required to avoid penalties.</p>
	"""
	recipients = _get_role_emails(["Compliance Officer", "Startup Admin", "Legal Counsel"])
	_send_email(recipients, subject, message)


def notify_compliance_score_drop(company, old_score, new_score):
	"""Alert founders when compliance score drops significantly (>= 10 points)."""
	if (old_score - new_score) < 10:
		return
	subject = f"📉 Compliance Score Alert: {company} dropped from {old_score} → {new_score}"
	message = f"""
	<p>Your StartupOS <b>Compliance Score</b> for <b>{company}</b> has dropped.</p>
	<ul>
	  <li>Previous Score: <b>{old_score}</b></li>
	  <li>Current Score:  <b style="color:red;">{new_score}</b></li>
	</ul>
	<p>Login to Compliance Hub to review pending items and improve your score.</p>
	"""
	recipients = _get_role_emails(["Startup Admin", "Finance Executive"])
	_send_email(recipients, subject, message)


# ─────────────────────────────────────────────
# CAP TABLE / ESOP NOTIFICATIONS
# ─────────────────────────────────────────────

def notify_equity_transaction(doc):
	"""
	Notify Startup Admin + ESOP Manager when a new Equity Transaction is created.
	Hooked via doc_events → Equity Transaction → after_insert.
	"""
	subject = f"📊 New Equity Transaction: {doc.name}"
	message = f"""
	<p>A new <b>Equity Transaction</b> has been recorded in StartupOS Cap Table.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Transaction</b></td><td>{doc.name}</td></tr>
	  <tr><td><b>Shareholder</b></td><td>{doc.get('shareholder','—')}</td></tr>
	  <tr><td><b>Shares</b></td><td>{doc.get('shares','—')}</td></tr>
	  <tr><td><b>Transaction Type</b></td><td>{doc.get('transaction_type','—')}</td></tr>
	  <tr><td><b>Date</b></td><td>{doc.get('transaction_date', nowdate())}</td></tr>
	</table>
	<p>Review the Cap Table in StartupOS for the updated ownership summary.</p>
	"""
	recipients = _get_role_emails(["Startup Admin", "ESOP Manager", "Investor Relations"])
	_send_email(recipients, subject, message)


def notify_esop_grant(doc):
	"""
	Notify when a new ESOP Grant is created.
	Hooked via doc_events → ESOP Grant → after_insert.
	"""
	subject = f"🎁 New ESOP Grant: {doc.name} – {doc.get('employee','')}"
	message = f"""
	<p>A new <b>ESOP Grant</b> has been issued in StartupOS.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Grant ID</b></td><td>{doc.name}</td></tr>
	  <tr><td><b>Employee</b></td><td>{doc.get('employee','—')}</td></tr>
	  <tr><td><b>Options Granted</b></td><td>{doc.get('options_granted','—')}</td></tr>
	  <tr><td><b>Grant Date</b></td><td>{doc.get('grant_date','—')}</td></tr>
	  <tr><td><b>Cliff (months)</b></td><td>{doc.get('cliff_months','—')}</td></tr>
	  <tr><td><b>Vesting Period (months)</b></td><td>{doc.get('vesting_period_months','—')}</td></tr>
	</table>
	"""
	recipients = _get_role_emails(["ESOP Manager", "Startup Admin"])
	_send_email(recipients, subject, message)


def notify_esop_vesting_event(grant_name, employee, options_vested, vested_date):
	"""
	Notify employee + ESOP Manager when options vest.
	Called by cap_table.calculator.recompute_vesting_schedules (daily scheduler).
	"""
	subject = f"🎉 ESOP Vesting Event: {options_vested} options vested – {employee}"
	employee_email = frappe.db.get_value("Employee", {"employee_name": employee}, "company_email") or \
	                 frappe.db.get_value("Employee", {"name": employee}, "company_email")

	message = f"""
	<p>Dear {employee},</p>
	<p>Your ESOP options have vested as per your grant schedule.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Grant</b></td><td>{grant_name}</td></tr>
	  <tr><td><b>Options Vested</b></td><td><b>{options_vested}</b></td></tr>
	  <tr><td><b>Vesting Date</b></td><td>{vested_date}</td></tr>
	</table>
	<p>Login to the Employee Self-Service portal to view your vesting schedule.</p>
	"""
	recipients = [r for r in [employee_email] + _get_role_emails("ESOP Manager") if r]
	_send_email(recipients, subject, message)


# ─────────────────────────────────────────────
# FUNDRAISING NOTIFICATIONS
# ─────────────────────────────────────────────

STAGE_EMOJI = {
	"Lead": "🌱",
	"Intro Call": "📞",
	"Due Diligence": "🔍",
	"Term Sheet": "📄",
	"Closed": "✅",
	"Rejected": "❌",
}

def notify_fundraising_stage_change(doc, prev_stage):
	"""
	Notify IR + Startup Admin when a Fundraising Opportunity stage changes.
	Hooked via doc_events → Fundraising Opportunity → on_update.
	"""
	if doc.status == prev_stage:
		return
	emoji = STAGE_EMOJI.get(doc.status, "📊")
	subject = f"{emoji} Deal Stage Update: {doc.get('investor_name','—')} → {doc.status}"
	message = f"""
	<p>A fundraising opportunity has moved to a new stage in <b>StartupOS Fundraising OS</b>.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Investor</b></td><td>{doc.get('investor_name','—')}</td></tr>
	  <tr><td><b>Previous Stage</b></td><td>{prev_stage}</td></tr>
	  <tr><td><b>New Stage</b></td><td><b>{doc.status}</b></td></tr>
	  <tr><td><b>Expected Close</b></td><td>{doc.get('expected_close_date','—')}</td></tr>
	  <tr><td><b>Ticket Size</b></td><td>₹ {doc.get('ticket_size','—')}</td></tr>
	</table>
	"""
	recipients = _get_role_emails(["Investor Relations", "Startup Admin"])
	_send_email(recipients, subject, message)


def notify_investor_update_due(opportunity):
	"""
	Monthly prompt to send an investor update.
	Called by fundraising.report_generator.prompt_investor_update (monthly scheduler).
	"""
	subject = f"📬 Monthly Investor Update Due – {opportunity.get('investor_name','')}"
	message = f"""
	<p>It's time to send your monthly investor update to <b>{opportunity.get('investor_name','')}</b>.</p>
	<p>Login to StartupOS → Fundraising OS to generate and send the update.</p>
	"""
	recipients = _get_role_emails(["Investor Relations", "Startup Admin"])
	_send_email(recipients, subject, message)


# ─────────────────────────────────────────────
# FINANCIAL NOTIFICATIONS
# ─────────────────────────────────────────────

def notify_low_runway(company, runway_months, burn_rate):
	"""
	Alert founders when runway drops below threshold.
	Called by financial.forecasting.update_all_runway_models (daily scheduler).
	"""
	if runway_months > 6:
		return
	urgency = "🔴 CRITICAL" if runway_months <= 2 else "🟡 WARNING"
	subject = f"{urgency}: {company} has only {runway_months:.1f} months of runway left"
	message = f"""
	<p><strong>StartupOS Financial Alert</strong></p>
	<p>Your company <b>{company}</b> has a critically low runway.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Runway Remaining</b></td><td><b>{runway_months:.1f} months</b></td></tr>
	  <tr><td><b>Monthly Burn Rate</b></td><td>₹ {burn_rate:,.0f}</td></tr>
	</table>
	<p>Login to StartupOS → Financial OS to review your forecasts and take action.</p>
	"""
	recipients = _get_role_emails(["Startup Admin", "Finance Executive"])
	_send_email(recipients, subject, message)


def notify_burn_rate_spike(company, previous_burn, current_burn, pct_change):
	"""Alert when month-over-month burn rate spikes more than 20%."""
	if pct_change < 20:
		return
	subject = f"🔥 Burn Rate Spike: {company} +{pct_change:.0f}% MoM"
	message = f"""
	<p><strong>Burn Rate Alert</strong> for <b>{company}</b></p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Previous Burn</b></td><td>₹ {previous_burn:,.0f}/mo</td></tr>
	  <tr><td><b>Current Burn</b></td><td>₹ {current_burn:,.0f}/mo</td></tr>
	  <tr><td><b>Change</b></td><td><b style="color:red;">+{pct_change:.1f}%</b></td></tr>
	</table>
	<p>Review your expense breakdown in StartupOS → Financial OS.</p>
	"""
	recipients = _get_role_emails(["Startup Admin", "Finance Executive"])
	_send_email(recipients, subject, message)


# ─────────────────────────────────────────────
# GOVERNANCE NOTIFICATIONS
# ─────────────────────────────────────────────

def notify_board_meeting_reminder(meeting_doc, days_left):
	"""
	Remind Board Members of an upcoming board meeting.
	"""
	subject = f"📅 Board Meeting Reminder: {meeting_doc.get('title','Board Meeting')} in {days_left} day(s)"
	message = f"""
	<p>This is a reminder for an upcoming <b>Board Meeting</b>.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Meeting</b></td><td>{meeting_doc.get('title','—')}</td></tr>
	  <tr><td><b>Date</b></td><td>{meeting_doc.get('meeting_date','—')}</td></tr>
	  <tr><td><b>Agenda</b></td><td>{meeting_doc.get('agenda_summary','—')}</td></tr>
	</table>
	<p>Login to StartupOS → Governance to review agenda items and documents.</p>
	"""
	recipients = _get_role_emails(["Board Member", "Startup Admin"])
	_send_email(recipients, subject, message)


def notify_resolution_pending_signature(resolution_doc):
	"""Alert when a Board Resolution needs signatures."""
	subject = f"✍️ Action Required: Sign Board Resolution – {resolution_doc.get('title','')}"
	message = f"""
	<p>A Board Resolution requires your signature in <b>StartupOS Governance</b>.</p>
	<p><b>Resolution:</b> {resolution_doc.get('title','—')}<br/>
	   <b>Deadline:</b> {resolution_doc.get('signature_deadline','—')}</p>
	<p>Login to StartupOS → Governance → Board Resolutions to sign.</p>
	"""
	recipients = _get_role_emails(["Board Member", "Legal Counsel"])
	_send_email(recipients, subject, message)


# ─────────────────────────────────────────────
# DPIIT / REGISTRATION NOTIFICATIONS
# ─────────────────────────────────────────────

def notify_dpiit_status_change(doc, prev_status):
	"""Notify when DPIIT Application status changes."""
	if doc.status == prev_status:
		return
	subject = f"🏆 DPIIT Application Update: {doc.name} → {doc.status}"
	message = f"""
	<p>Your <b>DPIIT Startup Recognition</b> application status has changed.</p>
	<table border="1" cellpadding="6" style="border-collapse:collapse;">
	  <tr><td><b>Application</b></td><td>{doc.name}</td></tr>
	  <tr><td><b>Previous Status</b></td><td>{prev_status}</td></tr>
	  <tr><td><b>New Status</b></td><td><b>{doc.status}</b></td></tr>
	</table>
	<p>Login to StartupOS → Compliance Hub → DPIIT Application for more details.</p>
	"""
	recipients = _get_role_emails(["Startup Admin", "Compliance Officer", "Legal Counsel"])
	_send_email(recipients, subject, message)


# ─────────────────────────────────────────────
# AI ASSISTANT NOTIFICATIONS
# ─────────────────────────────────────────────

def notify_ai_weekly_digest(company, insights):
	"""
	Send a weekly AI-generated insights digest to founders.
	Called by ai_assistant.rag_engine.refresh_knowledge_base (weekly scheduler).
	"""
	subject = f"🤖 Your Weekly StartupOS AI Digest – {company}"
	bullets = "".join(f"<li>{insight}</li>" for insight in (insights or ["No new insights this week."]))
	message = f"""
	<p>Here is your weekly AI-generated insights summary for <b>{company}</b>.</p>
	<ul>{bullets}</ul>
	<p>Ask the AI Assistant in StartupOS for deeper analysis on any topic.</p>
	"""
	recipients = _get_role_emails(["Startup Admin"])
	_send_email(recipients, subject, message)
