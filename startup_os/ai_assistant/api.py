import frappe

@frappe.whitelist()
def chat(message, session_id=None):
	"""
	Main AI chat endpoint.
	Retrieves live context from the company and passes to RAG engine.
	"""
	if not message:
		frappe.throw("Message cannot be empty.")

	user = frappe.session.user

	# Identify user's company
	company = frappe.db.get_value("User Permission",
		{"user": user, "allow": "Company"},
		"for_value"
	)

	from startup_os.ai_assistant.rag_engine import RAGEngine
	engine = RAGEngine(company=company)
	response = engine.query(message)

	# Log to session
	new_session_id = session_id or frappe.generate_hash(length=12)
	_log_chat(user, company, message, response, new_session_id)

	return {
		"message": response,
		"session_id": new_session_id,
		"company": company
	}

def _log_chat(user, company, question, answer, session_id):
	"""Persist chat history in an AI Chat Session doc."""
	try:
		session_name = frappe.db.get_value("AI Chat Session", {"session_id": session_id})
		if session_name:
			session_doc = frappe.get_doc("AI Chat Session", session_name)
		else:
			session_doc = frappe.new_doc("AI Chat Session")
			session_doc.user = user
			session_doc.company = company
			session_doc.session_id = session_id

		session_doc.append("messages", {
			"role": "user",
			"content": question,
			"timestamp": frappe.utils.now()
		})
		session_doc.append("messages", {
			"role": "assistant",
			"content": answer,
			"timestamp": frappe.utils.now()
		})
		session_doc.save(ignore_permissions=True)
	except Exception:
		pass  # Don't let logging failures block the response

@frappe.whitelist()
def get_chat_history(session_id):
	"""Retrieve chat history for a session."""
	session_name = frappe.db.get_value("AI Chat Session", {"session_id": session_id})
	if not session_name:
		return {"messages": []}

	doc = frappe.get_doc("AI Chat Session", session_name)
	return {
		"session_id": session_id,
		"messages": [
			{"role": m.role, "content": m.content, "timestamp": str(m.timestamp)}
			for m in doc.messages
		]
	}

@frappe.whitelist()
def refresh_knowledge_base():
	"""Manually trigger knowledge base refresh (admin only)."""
	if frappe.session.user != "Administrator":
		frappe.throw("Only Administrator can refresh the knowledge base.")

	from startup_os.ai_assistant import rag_engine
	rag_engine.refresh_knowledge_base()
	return {"status": "success", "message": "Knowledge base refresh triggered."}
