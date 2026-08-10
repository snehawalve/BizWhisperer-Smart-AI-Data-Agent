from tools import query_sql_db, search_company_documents

print("=== Testing Tool 1: SQL Database query ===")
# We invoke the tool directly using the .invoke() method
# This simulates what LangChain does when the Agent requests to run this tool.
sql_result = query_sql_db.invoke("SELECT category, SUM(amount) FROM expenses GROUP BY category;")
print(sql_result)

print("\n=== Testing Tool 2: Document Semantic Search ===")
# We search for something related to the AWS cost cutting strategy
doc_result = search_company_documents.invoke("AWS migration cost reduction")
print(doc_result)
