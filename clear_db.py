import ollama
import chromadb

from langchain_community.document_loaders import PyPDFDirectoryLoader  # Importing PDF loader from Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing text splitter from Langchain
from langchain.schema import Document  # Importing Document schema from Langchain
from chromadb.config import Settings
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Directory to your pdf files:
DATA_PATH = r"papers"

client = chromadb.PersistentClient(
        path="chromadb",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

# Get all collections and delete them
collections = client.list_collections()

for collection in collections:
    client.delete_collection(name=collection.name)  # Deleting the collection by name

print("All collections have been cleared.")