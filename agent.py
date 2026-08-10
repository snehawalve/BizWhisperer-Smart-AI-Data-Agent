import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from tools import search_company_documents

# =========================================================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# =========================================================================
load_dotenv()

# Verify that the Gemini API Key is loaded
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "YOUR_GEMINI_API_KEY_HERE":
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

def get_agent_executor():
    """
    Assembles the LangChain Agent, connects it to the SQLite database
    via SQLDatabaseToolkit, binds the SQL tools and RAG tools,
    and returns an AgentExecutor ready to run queries.
    """
    
    # =========================================================================
    # STEP 2: INITIALIZE CHAT MODEL (LLM)
    # =========================================================================
    print("Initializing Gemini LLM Chat Model...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0.0
    )
    
    # =========================================================================
    # STEP 3: ASSEMBLE SQL DATABASE TOOLKIT
    # =========================================================================
    # Connects to the SQLite database and loads metadata
    db = SQLDatabase.from_uri("sqlite:///enterprise.db")
    
    # Initialize the toolkit which generates standard SQL tools:
    # - sql_db_list_tables (list table names)
    # - sql_db_schema (retrieve columns, constraints, and sample rows)
    # - sql_db_query (execute SELECT statement)
    # - sql_db_query_checker (validate SQL syntax)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = toolkit.get_tools()
    
    # Combine the SQL tools with our custom RAG document search tool
    tools = sql_tools + [search_company_documents]
    
    # =========================================================================
    # STEP 4: DEFINE SYSTEM INSTRUCTIONS (PROMPT)
    # =========================================================================
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are BizWhisperer, an intelligent Enterprise Data Agent.\n\n"
            "You assist business managers by answering questions using two resources:\n"
            "1. A SQL database. You can interact with it using these database tools:\n"
            "   - Use 'sql_db_list_tables' to list the tables that exist in the database.\n"
            "   - Use 'sql_db_schema' to get the schema (columns, types) and sample rows for tables.\n"
            "   - Use 'sql_db_query' to execute read-only SELECT queries. Only SELECT statements are allowed.\n"
            "   - Use 'sql_db_query_checker' to verify your query's syntax before executing it.\n"
            "   *CRITICAL: Whenever you need to query the database, you MUST first list the tables or check the schema of the tables "
            "you need, to verify that columns exist, before writing a SQL query. Never guess column names.*\n\n"
            "2. Company policy and strategy PDFs. "
            "Use the tool 'search_company_documents' to search for guidelines, "
            "budgets, and cost-reduction plans using semantic English search.\n\n"
            "How to Reason:\n"
            "- If a query requires structured transaction records, use the SQL tools to find the table, "
            "check its schema, write a query, run it, and formulate your answer.\n"
            "- If a query requires rules, limits, or strategies, use 'search_company_documents'.\n"
            "- If you search the documents for a policy rule or limit and do not find any specific mention after 2 attempts, "
            "do NOT keep calling the search tool with minor keyword changes. Instead, assume the document does not explicitly "
            "state that limit, and state this clearly in your final answer.\n"
            "- Present your final answers professionally. Round dollar amounts to 2 decimal places.\n"
            "- Never run write queries (INSERT, UPDATE, DELETE). Only run SELECT queries."
        ),
        # MessagesPlaceholder allows LangChain to inject the conversation memory array here
        MessagesPlaceholder(variable_name="chat_history"),
        # {input} is where the user's latest message goes
        ("human", "{input}"),
        # agent_scratchpad is where LangChain stores the notes of the tools it has called
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # =========================================================================
    # STEP 5: CREATE TOOL CALLING AGENT
    # =========================================================================
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # =========================================================================
    # STEP 6: WRAP IN AGENT EXECUTOR
    # =========================================================================
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,                 # Increase safety limit to allow complex multi-step queries
        handle_parsing_errors=True         # If the LLM makes a minor syntax mistake in tool format, this handles it
    )
    
    return agent_executor

if __name__ == "__main__":
    # Test script to run a sample hybrid prompt
    executor = get_agent_executor()
    
    print("\n--- Running a Test Hybrid Query ---\n")
    user_query = "What were our top 3 expenses, and who approved them? Also, does the expense policy say anything about approving those categories?"
    
    # We invoke the agent executor. We supply an empty list for chat_history.
    response = executor.invoke({
        "input": user_query,
        "chat_history": []
    })
    
    print("\n--- Final Agent Response ---")
    print(response["output"])
