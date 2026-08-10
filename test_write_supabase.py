from db_history import save_conversation_to_supabase, list_conversations_from_supabase

print("=== Supabase Write and List Test ===")
messages = [
    {"role": "user", "content": "Hello world query"},
    {"role": "assistant", "content": "Hello, this is a response", "thoughts": [["thought", "Capturing thought test"], ["tool", "SQL output test"]]}
]

try:
    print("\nAttempting to save conversation 'test_session_999'...")
    save_conversation_to_supabase("test_session_999", "Test Title 999", messages)
    print("Save call finished.")
    
    print("\nAttempting to retrieve conversations...")
    chats = list_conversations_from_supabase()
    print(f"Retrieved chats: {chats}")
except Exception as e:
    print(f"Exception: {e}")
