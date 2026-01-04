# 🤖 Multi-Modal RAG Chatbot

A **Retrieval-Augmented Generation (RAG) chatbot** that can answer questions from documents using **text, tables, and images**. Built with **React frontend** and **FastAPI backend**, powered by **OpenAI LLMs** and embeddings.

---

## Features

- ✅ Upload documents (PDF, images, etc.) for ingestion.
- ✅ Automatically extract **text, tables, and images**.
- ✅ Generate searchable summaries and embeddings for fast retrieval.
- ✅ Ask questions interactively via a chat interface.
- ✅ Multi-modal understanding: handles **text, tables, and visual content**.
- ✅ Stores data securely using a vector database.
- ✅ Supports chat history for context-aware answers.

---

## Tech Stack

- **Frontend:** React, Tailwind CSS
- **Backend:** FastAPI, Python
- **LLMs & Embeddings:** OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)
- **Vector DB:** Chroma / any supported LangChain vector store
- **Environment Management:** `venv`, `.env` for API keys
- **Document Parsing:** `unstructured`, `tesseract-ocr`, `poppler-utils`

---
