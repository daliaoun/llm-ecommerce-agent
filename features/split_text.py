from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()

loader_docx = Docx2txtLoader("/home/umanlinkgroup/Desktop/chatbot-site-e-commerce-backend/data/e-commerce.docx")
pages = loader_docx.load()

md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on = [("#", "Main Section"), 
                           ("##", "Subsection")]
)

pages_md_split = md_splitter.split_text(pages[0].page_content)

for i in pages_md_split:
    print(i)
    
embedding = OpenAIEmbeddings(model='text-embedding-ada-002')

vectorstore = Chroma.from_documents(documents = pages_md_split, 
                                    embedding = embedding, 
                                    persist_directory = "/home/umanlinkgroup/Desktop/chatbot-site-e-commerce-backend/data/database_v")

