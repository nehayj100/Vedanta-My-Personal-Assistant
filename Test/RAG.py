import ollama
import chromadb

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Directory to your pdf files:
DATA_PATH = r"papers"

# Define tenant and database settings
DEFAULT_TENANT = "my_unique_tenant"  # Set your tenant name
DEFAULT_DATABASE = "my_database"  # Set your database name

# Create a ChromaDB client
client = chromadb.Client(settings=Settings())

# Attempt to create the tenant
try:
    client.create_tenant(name=DEFAULT_TENANT)
    print(f"Tenant '{DEFAULT_TENANT}' created successfully.")
except chromadb.errors.TenantAlreadyExists:
    print(f"Tenant '{DEFAULT_TENANT}' already exists.")
except Exception as e:
    print(f"Error creating tenant '{DEFAULT_TENANT}': {e}")

# Now initialize the PersistentClient with the created tenant
persistent_client = chromadb.PersistentClient(
    path="chromadb",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)
