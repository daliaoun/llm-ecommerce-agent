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
#- **TRANSLATE THE USER INPUT TO ENGLISH BEFORE STARTING**

# Define the system prompt template
QUERY_TEMPLATE = """
You are a highly intelligent assistant for an e-commerce platform.
Your task is to generate SQL queries based on the user's request to retrieve product data from the database.
Use the database schema provided below to ensure accuracy.

Context: {history}

Database Schema:
{schema}


the products table is like this :
example:
+------------+---------------+-----------------------------------------+-------------+----------+--------+----------------+--------------------------------------------------------------------------------------------------------------------------------------+--------+-------------+
| product_id | name          | description                             | category_id | brand_id | price  | stock_quantity | specifications                                                                                                                       | rating | num_reviews |
+------------+---------------+-----------------------------------------+-------------+----------+--------+----------------+--------------------------------------------------------------------------------------------------------------------------------------+--------+-------------+
|          1 | Apple Max Pro | High-performance smartphones from Apple |           1 |        1 | 491.46 |             63 | ["ram": "6 GB", "camera": "48 MP", "battery": "4000 mAh", "storage": "64 GB", "processor": "Tensor G2", "screen_size": "6.5 inches"] |   4.25 |         107 |
+------------+---------------+-----------------------------------------+-------------+----------+--------+----------------+--------------------------------------------------------------------------------------------------------------------------------------+--------+-------------+

categories are :
+--------------+
| name         |
+--------------+
| Accessories  |
| Audio        |
| Laptops      |
| Smartphones  |
| Smartwatches |
| Tablets      |



**THERE MIGHT BE TWO OR MORE FROM THE SAME PRODUCT WITH THE SAME NAME BUT NOT THE SAME SPECS, SO BE CAREFUL **
Rules:

- **If the user question is not clear or is too broad ask for clarification, and further specification** VERYYYIMPORTANT
**ALWAYS STICK TO THE SCHEMA!!!!!!!!!!!!!!!!**
- Take a deep breath
- Only generate valid SQL queries.
- **ALWAYS INFER TO THE SEMANTIC MEANING**and match it with what is available in the database.
- Use the context to relate follow-up queries to the specific products or topics mentioned earlier. For example, if the user asks for "reviews" after discussing "Smartphone X," retrieve reviews for "Smartphone X."
- **Only return the SQL query without any explanation**.
- The code you return is going to be executed directly on a MySQL database.
- Products categories are: Books, Clothing, Electronics, Home & Kitchen, Sports & Outdoors.

**Your output should be like this**: 
SELECT review FROM Reviews WHERE product_name = 'Smartphone X';

Begin processing requests.
User Request:
{user_input}

"""



FORMAT_TEMPLATE = """
You are a highly skilled conversational assistant for an e-commerce platform. Your task is to take the raw results retrieved from the database and format them into a clear, concise, and human-like response for the user.

Guidelines:
1. **Do not fabricate information.** If a product or data is not in the database results, clearly state that it's unavailable. Never invent or assume details that are not explicitly provided.
2. If a user query relates to a previously discussed product or topic, ensure the response is scoped to that context. For example, "reviews" should be tied to the most recently discussed product, such as "Smartphone X."
3. Suggest alternatives only if they are **meaningfully similar** and present in the database results. Use semantic relevance when applicable.
4. Keep your response polite, conversational, and easy to understand.
5. Use the context or history to enhance the response only when it is relevant and adds value. Always ensure the response aligns closely with the current query, even when leveraging context.
6. If the RAW DATABASE RESULTS is "The query output is empty":
   - Politely inform the user that the requested product or data isn't available.
   - Suggest similar available options based on the query's meaning (if relevant).
   - If no meaningful suggestions are found, inform the user honestly and offer assistance with other inquiries.
7. Always sound like a helpful salesperson, focusing on what is available and how it may meet the user's needs.
8. Products categories are: Books, Clothing, Electronics, Home & Kitchen, Sports & Outdoors.

Inputs:
- **User Input**: Directly reference the user's query to ensure the response is relevant.
- **Raw Database Results**: Use only the data retrieved from the database to avoid errors.
- **Context/History**: Use this to relate follow-up queries to the specific product or topic discussed in earlier user inputs.

User Input:
{user_input}

Raw Database Results:
{results}

Context to use IF NEEDED:
{history}  

Based on the above, format a friendly, helpful, and engaging response:
- Address the user query explicitly by referencing their input.
- Avoid misleading the user. If no relevant product or data is found, be honest and helpful.
- Include the product name (if available) to make the response engaging.
- Be concise, human-like, and use positive, sales-oriented language.
- Avoid overly technical terms or irrelevant details.
- Always stay on topic with the user's last query.

Friendly Response:
"""

# Create ConversationSummaryBufferMemory
memory = ConversationSummaryBufferMemory(
    llm=chat,
    max_token_limit=300,  # Adjust token limit as needed
    return_messages=True,
    memory_key="history"
)

# Create Prompt Template with memory
prompt_template = PromptTemplate.from_template(template=QUERY_TEMPLATE)


# Establish Database Connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**settings.db_config)
        print("Database connected successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None
    

# Example usage with multiple interactions
def generate_sql_query(user_input):
    # Get the current history
    history = memory.load_memory_variables({})['history']
    
    # Format the prompt with current context and memory summary
    formatted_prompt = prompt_template.format(
        schema=schema,
        history=history,
        user_input=user_input
    )
    
    
    # Generate response
    response = chat.invoke(formatted_prompt)
    print(response.content)
    return response.content

# Sanitize and Execute SQL Query
def execute_sql_query(sql_query):
    connection = get_db_connection()
    if not connection:
        return "Error: Could not connect to the database."
    
    # Check if the query is a SELECT query
    if not sql_query.strip().lower().startswith("select"):
        return sql_query  # Return the query itself without execution
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        print('thisis the result=',results)
        return results
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return f"Error executing query: {err}"
# User-friendly response generation
# User-friendly response generation with context
def format_results_for_chat(results, history,user_input):

    formatted_prompt = FORMAT_TEMPLATE.format(results=results, history=history,user_input=user_input)
   # Stream the response
    response_stream = chat.invoke(formatted_prompt)
    final_response = response_stream.content

    print(f"this is |||||||||||||||||:{final_response}")
    return final_response



def sanitize_sql_query(llm_output):
    """
    Sanitize and format the LLM's SQL query output for execution.
    """
    if not llm_output.strip():
        sanitized_query=" The query output is empty."
    # Remove SQL code block markers and strip whitespace
    sanitized_query = llm_output.strip().replace("```sql", "").replace("```", "").strip()
    
    # Additional validation or cleaning can go here if needed
    if not sanitized_query.lower().startswith("select"):
        return sanitized_query
    
    return sanitized_query


def chatbot_response(user_input):
    # Generate SQL query using LLM
    llm_output = generate_sql_query(user_input)
    
    try:
        # Sanitize and validate SQL query
        sql_query = sanitize_sql_query(llm_output)
        
        # Execute the SQL query on the database
        db_results = execute_sql_query(sql_query)
        
        # Retrieve conversation history
        history = memory.load_memory_variables({})['history']
        
        # Format the results into a chatbot response
        friendly_response = format_results_for_chat(db_results, history, user_input)

        # Save the formatted response to memory
        memory.save_context(
            {"input": user_input},
            {"output": friendly_response}
        )


        return friendly_response
    
    except ValueError as ve:
        # Conversational error handling
        return str(ve)
    except mysql.connector.Error as db_err:
        error_responses = [
            f"I'm having trouble accessing our product database right now. The error says: {db_err}. Would you like to try your query again?",
            f"Oops! There seems to be a small hiccup with our database. Here's what went wrong: {db_err}. Could you rephrase your request?",
            f"I apologize, but I'm experiencing some technical difficulties. The database returned an error: {db_err}. Can I help you with something else?"
        ]
        error_response = random.choice(error_responses)
        
        # Save the error response to memory
        memory.save_context(
            {"input": user_input},
            {"output": error_response}
        )
        return error_response
    
    except Exception as e:
        generic_errors = [
            f"I'm sorry, but something unexpected happened. Could you please try your request again?",
            "Hmm, it looks like we've encountered a small issue. Would you mind rephrasing your request?",
            "Apologies, but I'm having trouble processing your request at the moment. Can you help me understand what you're looking for?"
        ]
        generic_error = random.choice(generic_errors)
        
        # Save the generic error to memory
        memory.save_context(
            {"input": user_input},
            {"output": generic_error}
        )
        
        return generic_error





