import os
import sqlite3
import json
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler

# Import our backend agent and ingestion functions
from agent import get_agent_executor
from ingest_pdfs import ingest_documents
from db_history import (
    save_conversation_to_supabase,
    load_conversation_from_supabase,
    list_conversations_from_supabase,
    get_supabase_client,
    sign_in_user,
    sign_up_user
)

# Load environment variables
load_dotenv()

# =========================================================================
# STEP 1: CONFIGURE STREAMLIT PAGE
# =========================================================================
# st.set_page_config must be the very first Streamlit command called.
# It configures the browser tab title, favicon, and sidebar layout.
st.set_page_config(
    page_title="BizWhisperer - AI Data Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling to make the interface look premium and modern (Glassmorphism + harmonious colors)
st.markdown("""
<style>
    /* Styling the main title */
    .main-header {
        font-family: 'Outfit', sans-serif;
        color: #1E3A8A;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    /* Styling for sidebar sections */
    .sidebar-title {
        font-weight: 600;
        font-size: 1.2rem;
        color: #1E3A8A;
        margin-bottom: 10px;
    }
    /* Reasoning step boxes */
    .thought-box {
        background-color: #F3F4F6;
        border-left: 4px solid #3B82F6;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .tool-output-box {
        background-color: #ECECF1;
        border-left: 4px solid #10B981;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# STEP 2: AGENT THOUGHT CALLBACK HANDLER
# =========================================================================
# This custom class intercepts LangChain's internal execution steps.
# When the agent decides to execute a tool or completes one, this class captures 
# the event so we can display the agent's "inner thoughts" in the UI.
class StreamlitAgentCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.steps = []

    def on_agent_action(self, action, **kwargs):
        # Triggers when the agent decides to run a tool
        tool_name = action.tool
        tool_input = action.tool_input
        log_text = action.log
        
        step_info = f"💡 **Thought**: {log_text.split('Action:')[0].strip() if 'Action:' in log_text else log_text.strip()}"
        step_info += f"\n⚙️ **Action**: Calling tool `{tool_name}` with input `{tool_input}`"
        self.steps.append(("thought", step_info))
        
    def on_tool_end(self, output, **kwargs):
        # Triggers when a tool finishes running and returns data
        self.steps.append(("tool_output", f"📥 **Tool Result**:\n{output}"))

    def on_agent_finish(self, finish, **kwargs):
        # Triggers when the agent reaches its final answer
        self.steps.append(("finish", "✅ **Completed Reasoning Loop**"))

# =========================================================================
# STEP 3: SESSION STATE INITIALIZATION & CHAT HISTORY STORAGE
# =========================================================================
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# Initialize session-specific Supabase client
if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = get_supabase_client()

# Intercept unauthenticated users
if "user" not in st.session_state:
    st.markdown('<div class="main-header" style="text-align:center;">BizWhisperer Security 🔒</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header" style="text-align:center;">Enter your enterprise credentials to access the data agent.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio("Select Action:", ["Log In", "Register New Account"], horizontal=True)
        email = st.text_input("Corporate Email:")
        password = st.text_input("Password:", type="password")
        
        if auth_mode == "Log In":
            if st.button("🚪 Access Dashboard", use_container_width=True):
                try:
                    user = sign_in_user(st.session_state.supabase_client, email, password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Logged in as {email}!")
                        st.rerun()
                except Exception as e:
                    st.error(f"{e}")
        else:
            st.info("New accounts will be registered securely in your cloud database.")
            if st.button("➕ Register & Sign Up", use_container_width=True):
                try:
                    user = sign_up_user(st.session_state.supabase_client, email, password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Registered successfully as {email}!")
                        st.rerun()
                except Exception as e:
                    st.error(f"{e}")
    st.stop() # Halt execution so the dashboard remains locked

# Generate a session ID and clear/load messages
if "session_id" not in st.session_state:
    st.session_state.session_id = str(int(time.time()))
if "messages" not in st.session_state:
    st.session_state.messages = []

def save_chat():
    """
    Saves the current st.session_state.messages list to Supabase.
    The first user message is used as the title.
    """
    if not st.session_state.messages:
        return
        
    # Get a title from the first user prompt
    title = "New Conversation"
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            title = msg["content"]
            if len(title) > 28:
                title = title[:25] + "..."
            break
            
    save_conversation_to_supabase(
        st.session_state.supabase_client, 
        st.session_state.session_id, 
        title, 
        st.session_state.messages, 
        st.session_state.user["id"]
    )

# =========================================================================
# STEP 4: SIDEBAR DASHBOARD CONTENT
# =========================================================================
with st.sidebar:
    # 1. CHAT HISTORY MANAGEMENT SECTION
    st.markdown('<div class="sidebar-title">💬 Conversations</div>', unsafe_allow_html=True)
    
    # "New Chat" button resets the active session ID and clears the screen
    if st.button("➕ New Chat", use_container_width=True):
        if st.session_state.messages:
            save_chat()
        st.session_state.session_id = str(int(time.time()))
        st.session_state.messages = []
        st.rerun()
        
    # Read saved conversations from Supabase (filtered by user_id)
    try:
        past_chats = list_conversations_from_supabase(st.session_state.supabase_client, st.session_state.user["id"])
    except Exception:
        past_chats = []
    
    if past_chats:
        st.markdown("##### 📜 Past Chats")
        for chat in past_chats:
            chat_id = chat.get("id")
            chat_title = chat.get("title", "Saved Conversation")
            
            # Highlight the currently active chat
            button_style = f"📝 {chat_title}"
            if chat_id == st.session_state.session_id:
                button_style = f"💬 {chat_title} (Active)"
                
            # If user clicks, load that chat history from Supabase and reload streamlit
            if st.button(button_style, key=f"hist_{chat_id}", use_container_width=True):
                if st.session_state.messages:
                    save_chat()
                # Load messages from Supabase
                loaded_messages = load_conversation_from_supabase(st.session_state.supabase_client, chat_id)
                st.session_state.session_id = chat_id
                st.session_state.messages = loaded_messages
                st.rerun()
    else:
        st.info("No past conversations found. Ask a question to start a session!")
                
    st.divider()
    
    st.markdown('<div class="sidebar-title">⚙️ Enterprise Data Panel</div>', unsafe_allow_html=True)
    st.write("Browse structured SQL tables and manage RAG documents in real time.")
    
    st.divider()
    
    # 1. DATABASE PREVIEWER
    # We load our SQLite tables using pandas so the user can easily see the data.
    st.markdown("### 📊 SQLite Database Explorer")
    table_to_inspect = st.selectbox(
        "Select table to preview:",
        ["expenses", "sales", "employees"]
    )
    
    try:
        conn = sqlite3.connect("enterprise.db")
        df = pd.read_sql_query(f"SELECT * FROM {table_to_inspect} LIMIT 10", conn)
        conn.close()
        # Displays the data table in the sidebar
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error loading table: {e}")
        
    st.divider()
    
    # 2. PDF DOCUMENT UPLOADER
    # Users can upload new PDFs to the RAG vector store directly from their browser!
    st.markdown("### 📁 Upload New PDF Report")
    uploaded_file = st.file_uploader("Upload policy or financial report (PDF):", type="pdf")
    
    if uploaded_file is not None:
        # Save the uploaded file to our documents folder
        save_path = os.path.join("documents", uploaded_file.name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Saved: {uploaded_file.name}")
            
            # Trigger ingestion (Phase 3) for the newly uploaded file!
            with st.spinner("Ingesting PDF into ChromaDB vector store..."):
                try:
                    ingest_documents()
                    st.toast("Document indexed successfully! Vector DB updated.", icon="🚀")
                except Exception as ex:
                    st.error(f"Error indexing document: {ex}")
        else:
            st.info("'{uploaded_file.name}' is already uploaded and indexed.")

    st.divider()
    # Display secure profile details and Logout button
    st.markdown(f"👤 **User**: `{st.session_state.user['email']}`")
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.pop("user", None)
        st.session_state.pop("messages", None)
        st.session_state.pop("session_id", None)
        st.rerun()

    st.divider()
    st.caption("BizWhisperer v1.0 • Powered by LangChain & Gemini 3.1 Flash Lite")

# =========================================================================
# STEP 5: MAIN CHAT INTERFACE RENDERING
# =========================================================================
st.markdown('<div class="main-header">BizWhisperer 🧠</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Agentic SQL & RAG Assistant. Ask me anything about employee records, business transactions, or policy manual guidelines.</div>', unsafe_allow_html=True)

# Render past message bubbles from the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # If there are captured thinking steps from a previous query, render them in an expander
        if "thoughts" in message and message["thoughts"]:
            with st.expander("Show Reasoning Steps 🔍"):
                for step_type, step_content in message["thoughts"]:
                    if step_type == "thought":
                        st.markdown(f'<div class="thought-box">{step_content}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="tool-output-box">{step_content}</div>', unsafe_allow_html=True)

# =========================================================================
# STEP 6: USER INPUT AND AGENT INVOCATION
# =========================================================================
if user_prompt := st.chat_input("Ask a question (e.g. 'What was AWS expense in Q2 and what is our reduction target?')"):
    
    # 1. Display user's question in chat
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)
        
    # 2. Call the agent to get a response
    with st.chat_message("assistant"):
        st.write("Thinking...")
        
        # Create placeholders for progressive updates
        thought_placeholder = st.empty()
        answer_placeholder = st.empty()
        
        # Instantiate the custom callback handler to capture the thoughts
        cb_handler = StreamlitAgentCallbackHandler()
        
        try:
            # Connect to our backend agent executor
            agent_executor = get_agent_executor()
            
            # Format chat history for LangChain
            # LangChain expects structured histories. For a simple demo, we can supply history as a list of strings
            # or keep it empty. We will feed it empty here or format messages.
            # To keep it robust, we construct the input dictionary
            agent_inputs = {
                "input": user_prompt,
                "chat_history": [] # For a single-turn agent prompt, can expand to convert st.session_state messages
            }
            
            # Run the agent
            response = agent_executor.invoke(agent_inputs, {"callbacks": [cb_handler]})
            
            # Extract final response text
            final_answer = response.get("output", "I could not formulate an answer.")
            
            # Clean up the output formatting if wrapped in LangChain block formats
            # The agent can return a list containing a mix of dictionaries and strings.
            # This function iterates through all parts and joins them into a single string.
            def clean_output(val):
                if isinstance(val, list):
                    parts = []
                    for item in val:
                        if isinstance(item, dict) and "text" in item:
                            text = item["text"]
                        elif isinstance(item, str):
                            text = item
                        else:
                            continue
                        if text:
                            parts.append(text)
                    
                    # Merge parts while ensuring words aren't stuck together
                    joined_text = ""
                    for part in parts:
                        if not joined_text:
                            joined_text = part
                        else:
                            needs_space = (
                                not joined_text[-1].isspace() and 
                                not part[0].isspace() and 
                                part[0] not in [".", ",", "!", "?", ";", ":", ")", "]", "}"]
                            )
                            if needs_space:
                                joined_text += " " + part
                            else:
                                joined_text += part
                    return joined_text
                elif isinstance(val, str) and val.strip().startswith("["):
                    try:
                        import ast
                        parsed_val = ast.literal_eval(val)
                        if isinstance(parsed_val, list):
                            return clean_output(parsed_val)
                    except:
                        pass
                return str(val)

            final_answer = clean_output(final_answer)
            
            # 3. Render the reasoning steps inside an expander
            if cb_handler.steps:
                with st.expander("Show Reasoning Steps 🔍", expanded=True):
                    for step_type, step_content in cb_handler.steps:
                        if step_type == "thought":
                            st.markdown(f'<div class="thought-box">{step_content}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="tool-output-box">{step_content}</div>', unsafe_allow_html=True)
            
            # Clear "Thinking..." and render the final answer
            answer_placeholder.write(final_answer)
            
            # 4. Save the assistant response and thoughts to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer,
                "thoughts": cb_handler.steps
            })
            save_chat()
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            # Remove "Thinking..." message
            answer_placeholder.empty()
