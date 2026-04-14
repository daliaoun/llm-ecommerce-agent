import random
import time
import mysql.connector
import json
import openai
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables import chain
from operator import itemgetter
from langchain_core.runnables import RunnableConfig
from config import settings

def load_schema(file_name="schema.json"):
    """Load database schema from a file."""
    try:
        with open(file_name, "r") as file:
            schema = json.load(file)
        print("Schema loaded successfully!")
        return schema
    except FileNotFoundError:
        print(f"Error: File {file_name} not found. Make sure the file exists.")
        return None
    except json.JSONDecodeError as err:
        print(f"Error decoding JSON: {err}")
        return None

# Load schema
schema = load_schema("one_of_one.json")
# Initialize ChatOpenAI
chat = ChatOpenAI(
    model_name='gpt-4o',
    seed=365,
    temperature=0,
    max_tokens=250,
    streaming=True,
    api_key=settings.openai_api_key or None,
)

# SQL Generation Template
# SQL Generation Template
SQL_GENERATION_TEMPLATE = """
Core Objective

Generate precise SQL queries for order management operations based on user input.

**User Input**:
{user_input}

**context**:
{history}
Scenario Selection Hierarchy (Strict Priority)
    Status Check
        Triggered by "status" keywords
    Cancellation Process
        First mention: Check Cancellation Eligibility
        Subsequent mention: Proceed with Cancellation
    Fallback: Default to Status Check

Request Types
    1. Order Status Check
    Requirements:
        order_id
        customer_name
        Validate user ownership
        Retrieve order details
    2. Order Cancellation Eligibility
    Requirements:
        order_id
        customer_name
        Verify order status
        Prevent cancellation for shipped/completed orders
    3. Order Cancellation
    Prerequisites:
        Mandatory prior eligibility check
        order_id
        customer_name
        Update order status to "Cancelled"
        
**Database Schema**:
{schema}
Key Processing Instructions
    Input Parsing
        Detect intent via keywords:
            "cancel"
            "cancellation"
            "stop order"
        Extract order_id and customer_name semantically
        Leave fields empty if not found
    SQL Query Guidelines
        Strictly adhere to provided database schema
        Verify user ownership
        Check cancellation eligibility before cancellation
        Always end queries with semicolon (;)


Output Format
Return **only** a JSON object with the following structure:
    "sql_query": "Generated SQL query",   
    "request_type": "Status Check | Order Cancellation Eligibility | Order Cancellation" 
    
Critical Constraints
     MANDATORY RULES:
        Never generate queries without context
        Always respect database schema
        Prioritize user authentication
        Maintain data integrity

Fundamental Approach
    Deliver precise, context-aware SQL queries for seamless order management.
"""

# Response Formatter Template
FORMAT_TEMPLATE = """
You are a highly skilled conversational assistant for an e-commerce platform.

Your task is to generate responses that are:

    Human-like: Use natural, conversational language.
    Empathetic: Acknowledge the user's concerns.
    Scenario-specific: Tailor the response to the user's specific query and the system's findings.
    Professional: Keep the tone friendly, polite, and clear.

Scenario Interpretation

CONTEXT:
{history}

Request Details:

    Request Type: {request_type}
    User Input: {user_input}
    SQL Query Executed: {sql_query}
    Execution Results: {results}

Interpretation Rules
1. Missing Information

    If order_id or customer_name is missing in the user input:
        Respond conversationally by asking for the missing information.

2. Order Status Check Scenarios

    Order Found & Ownership Verified:
        Respond clearly with the order status.

    Ownership Mismatch:
        Politely deny access.

    Order Not Found:
        Acknowledge the inconvenience and suggest next steps.

3. Order Cancellation Scenarios

    Eligible for Cancellation:
        Offer to proceed with cancellation.

    **only if Execution Results is  "Shipped" or "Completed"**:
        Explain why cancellation isn't possible and offer alternative suggestions.

    Order Not Found:
        Handle it with empathy and a suggestion to double-check details.

4. Fallback

    If the results or input are unclear:
        Respond empathetically and suggest next steps.

        
Your response should:

    Use the specific scenario as a basis.
    Avoid mentioning backend or technical details.
    Sound empathetic and helpful.

Friendly Response:


"""

# Create memory
memory = ConversationSummaryBufferMemory(
    llm=chat,
    max_token_limit=300,
    return_messages=True,
    memory_key="history"
)

def get_db_connection():
    """Establish a database connection."""
    try:
        connection = mysql.connector.connect(**settings.db_config)
        print("Database connected successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def generate_sql_query(user_input):
    """Generate SQL query from user input."""
    history = memory.load_memory_variables({}).get('history', '')
    formatted_prompt = SQL_GENERATION_TEMPLATE.format(
        history=history,
        schema=schema,
        user_input=user_input
    )
    response = chat.invoke(formatted_prompt)
    sanitized_query = response.content.strip().replace("```json", "").replace("```", "").strip()
    sql_response = json.loads(sanitized_query)
    print(sql_response)
    return sql_response

def execute_sql_query(sql_query):
    """Execute the SQL query."""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed"}

    try:
        connection.autocommit = True  # Explicitly set autocommit
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(sql_query)
            affected_rows = cursor.rowcount
            print("Affected rows:", affected_rows)
            results = cursor.fetchall()
        connection.close()
        print(results)
        return results
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        connection.rollback()  # Rollback in case of error
        return {"error": str(err)}

def execute_and_format_query(sql_response):
    """Execute the query and format results."""
    sql_query = sql_response.get("sql_query")
    request_type = sql_response.get("request_type")

    if not sql_query:
        return {"error": "No SQL query to execute"}

    results = execute_sql_query(sql_query)
    return {
        "sql_query": sql_query,
        "request_type": request_type,
        "results": results
    }

def generate_user_response(formatted_results, user_input):
    """Generate a user-friendly response."""
    try:
        history = memory.load_memory_variables({}).get('history', '')
        results = formatted_results["results"]
        
        
        formatted_prompt = FORMAT_TEMPLATE.format(
            history=history,
            request_type=formatted_results["request_type"],
            user_input=user_input,
            sql_query=formatted_results["sql_query"],
            results=results
        )
        response = chat.invoke(formatted_prompt)
        return response.content
    except Exception as e:
        print(f"Error generating user response: {e}")
        return "There was an error processing your request."

def chatbot_response_managment(user_input):
    """Main chatbot response handler."""
    sql_response = generate_sql_query(user_input)
    formatted_results = execute_and_format_query(sql_response)
    final_response = generate_user_response(formatted_results, user_input)
    memory.save_context({"input": user_input}, {"output": final_response})
    return final_response


