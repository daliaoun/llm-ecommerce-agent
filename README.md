# E-commerce Chatbot Assistant

This project is an e-commerce conversational assistant built with Python, LangChain, OpenAI models, MySQL, Chroma vector storage, and Streamlit.

This project is inspired by my work at UmanLink Digital services, rebuilt independently with improvements.

It helps users through natural language conversations for common shopping and support scenarios.

## Project Overview

The chatbot is designed to support four main user flows:

1. Product discovery and recommendations
- Understands user intent and preferences.
- Generates SQL queries against the product catalog.
- Returns user-friendly responses from real database results.

2. FAQ support with retrieval-augmented generation
- Uses embeddings and vector search over indexed documentation.
- Retrieves relevant context and produces concise answers.

3. Order management
- Supports order status lookup.
- Supports cancellation eligibility and cancellation actions.
- Uses request context and conversation memory to handle follow-ups.

4. Scope control and support redirection
- Keeps answers focused on e-commerce functionality.
- Redirects out-of-scope requests to support channels.

## Tech Stack

- Python
- LangChain and LangChain OpenAI
- OpenAI API
- MySQL
- Chroma vector database
- Streamlit

## Key Files

- features/streamlit_app.py: Streamlit user interface.
- features/agent.py: Main tool-calling agent orchestration.
- features/tools.py: Tool registration for FAQ, product suggestion, and order management.
- features/suggestion.py: Product search and response formatting pipeline.
- features/order_managment.py: Order status and cancellation workflow.
- features/faq.py: FAQ retrieval pipeline (vector search + LLM answer generation).
- features/config.py: Centralized environment variable loading and settings.

## Small Local Run Guide

Use these steps to run the project on your PC.

### 1. Prerequisites

- Python 3.10 or newer
- Access to a MySQL database with the required schema
- An OpenAI API key

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a .env file in the project root (same folder as README.md) and set:

```env
OPENAI_API_KEY=your_openai_api_key
DB_HOST=your_db_host
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

### 4. Run the app

```bash
streamlit run features/streamlit_app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Troubleshooting

- If database connection fails, verify DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME.
- If OpenAI calls fail, verify OPENAI_API_KEY.
- If you get import errors, confirm dependencies were installed from requirements.txt in the active environment.

## Notes

- Keep .env private and do not commit secrets.
- Use .env.example as a template only.