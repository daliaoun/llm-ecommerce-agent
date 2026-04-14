import time
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser 
from config import settings

# Define the embedding and vector store globally if they don't change across function calls
embedding = OpenAIEmbeddings(model='text-embedding-ada-002')

vectorstore_from_directory = Chroma(
    persist_directory="data/database_v",
    embedding_function=embedding
)

# Define the retriever globally as well
retriever = vectorstore_from_directory.as_retriever(
    search_type='mmr',
    search_kwargs={'k': 3, 'lambda_mult': 0.8}
)

# Define the template globally
TEMPLATE = '''
You are a highly skilled conversational assistant for an e-commerce platform.
Your task is to answer the user's question in a clear and concise manner using only the context provided below.

Question:
{question}

Context:
{context}

Make sure your response directly addresses the user's question. If the information is unavailable in the context, reply with: "I'm sorry, I couldn't find the information you're looking for."

At the end of your response, list the relevant section(s) of the e-commerce document **if available** used in the format:
Sources: *Section Name(s)*
where *Section Name(s)* should be replaced with the specific "Main Section" and "Section" titles from the context.
Feel free to make the response friendly and engaging!
'''

prompt_template = PromptTemplate.from_template(TEMPLATE)

# Chat model setup
chat = ChatOpenAI(
    model_name='gpt-4o',
    seed=365,
    temperature=0,
    max_tokens=250,
    api_key=settings.openai_api_key or None,
)

def execute_chain(question: str) -> str:
    """
    Executes the LangChain pipeline with the given question.

    Args:
        question (str): The user's question.

    Returns:
        str: The final response from the pipeline.
    """
    # Define the chain
    chain = ({
        'context': retriever,
        'question': RunnablePassthrough()
    } | prompt_template | chat | StrOutputParser())
    
    # Process the question and return the streamed response
    final_response = ""
    for partial_response in chain.stream(question):
        final_response += partial_response


    return final_response
