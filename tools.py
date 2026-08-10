import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables (API Key)
load_dotenv()

VECTOR_DB_DIR = "vector_store"

# =========================================================================
# TOOL: DOCUMENT SEMANTIC SEARCH TOOL
# =========================================================================

@tool
def search_company_documents(query: str) -> str:
    """
    Search the company's unstructured documents (expense policies, Q2 strategic financial plan).
    
    Use this tool when you need information on:
    - Company rules and guidelines (reimbursement procedures, spending limits)
    - Who needs to approve software, travel, or office supply purchases
    - Future strategy details (such as cost-cutting plans, hosting migrations, or marketing shifts)
    
    Input should be a semantic search phrase in plain English.
    """
    try:
        # 1. Initialize the same embeddings model we used during ingestion
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # 2. Load the existing Chroma vector store from the folder
        vector_db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings
        )
        
        # 3. Perform a Similarity Search
        # k=3 means we want Chroma to retrieve the top 3 text chunks that are 
        # semantically closest to the user's query.
        docs = vector_db.similarity_search(query, k=3)
        
        if not docs:
            return "No matching document segments found."
            
        # 4. Format and join the results
        formatted_results = []
        for i, doc in enumerate(docs):
            source = os.path.basename(doc.metadata.get("source", "Unknown Source"))
            content = doc.page_content.strip()
            formatted_results.append(
                f"--- Result {i+1} (Source: {source}) ---\n{content}\n"
            )
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching documents: {str(e)}"
