import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# We will try other advanced model names to find one with active quota
models_to_try = [
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash"
]

for model_name in models_to_try:
    try:
        print(f"Testing model: '{model_name}'...")
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.0)
        res = llm.invoke("Say 'Hello' in one word.")
        print(f"-> SUCCESS! Response: {res.content.strip()}\n")
        break
    except Exception as e:
        print(f"-> FAILED with error: {e}\n")
