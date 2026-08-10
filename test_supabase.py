from db_history import list_conversations_from_supabase

print("=== Supabase Connection & Retrieval Test ===")
try:
    chats = list_conversations_from_supabase()
    print("Connection Successful!")
    print(f"Chats found: {chats}")
except Exception as e:
    print(f"Exception raised: {e}")
