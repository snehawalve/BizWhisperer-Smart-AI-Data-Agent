import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# We will try different model names to see which ones are accepted by the current LangChain + Gemini integration
models_to_try = [
    "models/gemini-embedding-001",
    "models/gemini-embedding-2"
]

for model_name in models_to_try:
    try:
        print(f"Testing model: '{model_name}'...")
        embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
        # Try embedding a single word
        vec = embeddings.embed_query("hello")
        print(f"-> SUCCESS! Vector dimension: {len(vec)}")
        break # Exit loop on first success
    except Exception as e:
        print(f"-> FAILED with error: {e}\n")
