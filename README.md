# BizWhisperer: AI Data Agent

BizWhisperer is an advanced AI Data Agent combining Relational SQL (structured data) and Retrieval-Augmented Generation (RAG, unstructured PDF data) with an LLM Agentic workflow.

## Project Structure
- `data/`: Relational SQLite database and sample files.
- `documents/`: Enterprise PDF documents.
- `vector_store/`: Persistent vector database (ChromaDB).
- `app/`: Source code for backend agent, tools, and UI.
- `requirements.txt`: Python package requirements.
- `.env`: Environment variables (API keys).
- `init_db.py`: Script to initialize the SQLite database.
- `ingest_pdfs.py`: Script to load and vectorise PDF documents.
- `agent.py`: Agentic router and tool definition.
- `app.py`: Streamlit frontend application.

## Prerequisites
1. Python 3.8+
2. Google Gemini API Key (or OpenAI API Key)
