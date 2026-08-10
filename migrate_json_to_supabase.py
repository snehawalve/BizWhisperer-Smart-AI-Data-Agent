import os
import json
from db_history import save_conversation_to_supabase

HISTORY_DIR = "chat_history"

def migrate_chats():
    """
    Reads all local JSON conversation history files and uploads them to the
    new Supabase PostgreSQL database so you don't lose your past chats!
    """
    print("=== Starting JSON to Supabase Migration ===")
    
    if not os.path.exists(HISTORY_DIR):
        print(f"No local history directory '{HISTORY_DIR}' found. Nothing to migrate.")
        return
        
    json_files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    
    if not json_files:
        print("No local JSON history files found to migrate.")
        return
        
    print(f"Found {len(json_files)} local chat(s) to migrate.")
    
    success_count = 0
    for file_name in json_files:
        file_path = os.path.join(HISTORY_DIR, file_name)
        print(f"\nReading file: {file_name}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
                
            session_id = chat_data.get("session_id")
            title = chat_data.get("title", "Imported Conversation")
            messages = chat_data.get("messages", [])
            
            if not session_id or not messages:
                print(f"Skipping {file_name}: Missing session_id or messages.")
                continue
                
            # Call our database save utility to upsert the conversations and messages into Supabase
            save_conversation_to_supabase(session_id, title, messages)
            success_count += 1
            
        except Exception as e:
            print(f"Failed to migrate {file_name}: {e}")
            
    print("\n==========================================")
    print(f"Migration completed! Successfully migrated {success_count}/{len(json_files)} chats to Supabase.")
    print("==========================================")

if __name__ == "__main__":
    migrate_chats()
