import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    print("Initializing GenAI Client...")
    # The default Client() reads GEMINI_API_KEY from environment variables
    client = genai.Client()
    
    print("Listing models...")
    for model in client.models.list():
        print(f"Model: {model.name} | Actions: {model.supported_actions}")
except Exception as e:
    print(f"Error listing models: {e}")
