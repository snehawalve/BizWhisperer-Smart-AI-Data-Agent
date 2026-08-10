import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key is missing from the .env file.")

def get_supabase_client() -> Client:
    """
    Creates and returns a fresh client instance. In Streamlit, this will be called
    per-user-session and saved in st.session_state to prevent cross-session token leaking.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================================
# AUTHENTICATION HELPERS
# =========================================================================

def sign_in_user(supabase_client: Client, email: str, password: str) -> dict:
    """
    Authenticates an existing user using email/password.
    """
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email
            }
        return None
    except Exception as e:
        raise Exception(f"Sign-in failed: {e}")


def sign_up_user(supabase_client: Client, email: str, password: str) -> dict:
    """
    Registers a new user in Supabase Auth.
    """
    try:
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email
            }
        return None
    except Exception as e:
        raise Exception(f"Registration failed: {e}")

# =========================================================================
# DATABASE OPERATIONS (CRUD)
# =========================================================================

def save_conversation_to_supabase(supabase_client: Client, session_id: str, title: str, messages: list, user_id: str):
    """
    Saves the entire list of chat messages to the remote Supabase database.
    Associates the conversation with the logged-in user_id.
    """
    if not messages or not user_id:
        return
        
    try:
        # 1. UPSERT THE CONVERSATION RECORD
        supabase_client.table("conversations").upsert({
            "id": session_id,
            "title": title,
            "user_id": user_id
        }).execute()
        
        # 2. DELETE OLD MESSAGES FOR THIS SESSION
        supabase_client.table("messages").delete().eq("conversation_id", session_id).execute()
        
        # 3. BULK INSERT NEW MESSAGES
        insert_rows = []
        for msg in messages:
            insert_rows.append({
                "conversation_id": session_id,
                "role": msg["role"],
                "content": msg["content"],
                "thoughts": msg.get("thoughts", [])
            })
            
        if insert_rows:
            supabase_client.table("messages").insert(insert_rows).execute()
            
        print(f"Successfully saved conversation '{title}' (ID: {session_id}) for user {user_id} to Supabase.")
        
    except Exception as e:
        print(f"Error saving chat to Supabase: {e}")


def load_conversation_from_supabase(supabase_client: Client, session_id: str) -> list:
    """
    Retrieves the list of messages for a given session ID from Supabase.
    """
    try:
        response = supabase_client.table("messages") \
            .select("role, content, thoughts") \
            .eq("conversation_id", session_id) \
            .order("created_at", desc=False) \
            .execute()
            
        loaded_messages = []
        for row in response.data:
            loaded_messages.append({
                "role": row["role"],
                "content": row["content"],
                "thoughts": row["thoughts"] if row["thoughts"] is not None else []
            })
            
        return loaded_messages
        
    except Exception as e:
        print(f"Error loading chat from Supabase: {e}")
        return []


def list_conversations_from_supabase(supabase_client: Client, user_id: str) -> list:
    """
    Fetches the titles and IDs of saved conversations for a specific user, sorted by newest first.
    """
    if not user_id:
        return []
        
    try:
        response = supabase_client.table("conversations") \
            .select("id, title") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
            
        return response.data
        
    except Exception as e:
        print(f"Error listing chats from Supabase: {e}")
        return []
