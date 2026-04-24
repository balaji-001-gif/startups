import os
import frappe

class VectorStore:
	"""
	Abstraction layer over vector store backends (Chroma or Pinecone).
	"""

	def __init__(self):
		self.store_type = frappe.conf.get("vector_store") or "chroma"
		self.collection_name = "startup_os_knowledge"
		self._store = None

	def _init_chroma(self):
		try:
			import chromadb
			persist_dir = os.path.join(frappe.get_site_path(), "private", "chroma_db")
			os.makedirs(persist_dir, exist_ok=True)
			client = chromadb.PersistentClient(path=persist_dir)
			self._store = client.get_or_create_collection(self.collection_name)
		except ImportError:
			frappe.log_error("chromadb not installed. Run: pip install chromadb", "VectorStore Init")
			self._store = None

	def _init_pinecone(self):
		try:
			import pinecone
			api_key = frappe.conf.get("pinecone_api_key")
			if not api_key:
				frappe.throw("pinecone_api_key not set in site_config.json")
			pinecone.init(api_key=api_key)
			if self.collection_name not in pinecone.list_indexes():
				pinecone.create_index(self.collection_name, dimension=1536)  # OpenAI embedding dim
			self._store = pinecone.Index(self.collection_name)
		except ImportError:
			frappe.log_error("pinecone-client not installed. Run: pip install pinecone-client", "VectorStore Init")
			self._store = None

	def get_store(self):
		if self._store:
			return self._store
		if self.store_type == "chroma":
			self._init_chroma()
		elif self.store_type == "pinecone":
			self._init_pinecone()
		return self._store

	def add_documents(self, documents, ids, metadatas=None):
		"""Add documents to the vector store."""
		store = self.get_store()
		if not store:
			return False

		if self.store_type == "chroma":
			store.upsert(documents=documents, ids=ids, metadatas=metadatas or [{}] * len(documents))
		elif self.store_type == "pinecone":
			# Pinecone requires embeddings
			embeddings = self._get_embeddings(documents)
			vectors = [(ids[i], embeddings[i], {"text": documents[i]}) for i in range(len(documents))]
			store.upsert(vectors=vectors)

		return True

	def similarity_search(self, query, n_results=5):
		"""Search for similar documents."""
		store = self.get_store()
		if not store:
			return []

		if self.store_type == "chroma":
			results = store.query(query_texts=[query], n_results=n_results)
			docs = results.get("documents", [[]])[0]
			return docs
		elif self.store_type == "pinecone":
			embedding = self._get_embeddings([query])[0]
			results = store.query(vector=embedding, top_k=n_results, include_metadata=True)
			return [m.get("metadata", {}).get("text", "") for m in results.get("matches", [])]

		return []

	def _get_embeddings(self, texts):
		"""Get embeddings using OpenAI."""
		try:
			import openai
			openai.api_key = frappe.conf.get("openai_api_key")
			response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
			return [item["embedding"] for item in response["data"]]
		except Exception as e:
			frappe.log_error(str(e), "VectorStore Embedding Error")
			return [[0.0] * 1536] * len(texts)  # Zero-fallback
