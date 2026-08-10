import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# =========================================================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# =========================================================================
# load_dotenv() reads key-value pairs from a .env file and sets them as 
# environment variables. This lets LangChain automatically find our GEMINI_API_KEY.
load_dotenv()

# Check that the API key is present before trying to use it.
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "YOUR_GEMINI_API_KEY_HERE":
    raise ValueError(
        "Please set your GEMINI_API_KEY in the .env file before running this script."
    )

def ingest_documents():
    """
    Reads PDFs from the 'documents' directory, splits them into small chunks,
    generates embeddings using Google Gemini's embedding model, and saves them
    to a local Chroma vector database.
    """
    
    # =========================================================================
    # STEP 2: LOCATE AND LOAD PDF FILES
    # =========================================================================
    # We will locate the PDF files we generated in the 'documents' folder.
    pdf_dir = "documents"
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found in the 'documents' directory.")
        return
        
    all_pages = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"Loading document: {pdf_path}")
        
        # PyPDFLoader parses the PDF and extracts text page-by-page.
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        all_pages.extend(pages)
        
    print(f"Successfully loaded {len(all_pages)} total pages from PDFs.")
    
    # =========================================================================
    # STEP 3: TEXT CHUNKING (SPLITTING THE TEXT)
    # =========================================================================
    # LLMs have context windows, and we also want our search to return specific 
    # paragraphs rather than a whole 10-page document.
    # RecursiveCharacterTextSplitter splits text by looking at a list of characters 
    # (like double newlines, single newlines, spaces, and characters) in order.
    # - chunk_size=500: Each chunk of text will be roughly 500 characters long.
    # - chunk_overlap=50: To ensure we don't lose context between two halves of a 
    #   split sentence, the last 50 characters of chunk 1 will be duplicated at the
    #   start of chunk 2.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(all_pages)
    print(f"Split {len(all_pages)} pages into {len(chunks)} smaller text chunks.")
    
    # Print a preview of the first chunk to see what it looks like
    if chunks:
        print("\n--- Example Chunk Preview ---")
        print(f"Source: {chunks[0].metadata['source']}")
        print(f"Content: {chunks[0].page_content}")
        print("-----------------------------\n")
        
    # =========================================================================
    # STEP 4: EMBEDDINGS MODEL
    # =========================================================================
    # An embedding model takes a string of text and returns a list of numbers 
    # representing its semantic meaning.
    # We use Google's 'text-embedding-004', which is highly performant and fast.
    print("Initializing Google Gemini Embeddings model...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # =========================================================================
    # STEP 5: STORE IN VECTOR DB (CHROMADB)
    # =========================================================================
    # We will initialize Chroma, a popular, lightweight open-source vector store.
    # We tell it:
    # - Where to get the documents and their texts (chunks).
    # - Which embedding model to use (embeddings).
    # - Where to save the database files locally (persist_directory).
    persist_dir = "vector_store"
    print(f"Creating vector database in directory: '{persist_dir}'...")
    
    # Chroma.from_documents will automatically:
    # 1. Call the embedding model to convert each text chunk into a vector.
    # 2. Store the original text, the metadata (like filename/page number), and the vector.
    # 3. Write these database files to the 'vector_store' directory.
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    # In older versions of Chroma, we had to call vector_db.persist(). 
    # In newer versions, it persists automatically, but it's safe to know it's saved.
    print("Vector database built and saved successfully.")

if __name__ == "__main__":
    ingest_documents()
