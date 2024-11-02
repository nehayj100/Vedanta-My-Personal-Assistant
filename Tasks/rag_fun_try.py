import ollama
import chromadb

from langchain_community.document_loaders import PyPDFDirectoryLoader  # Importing PDF loader from Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing text splitter from Langchain
from langchain.schema import Document  # Importing Document schema from Langchain
from chromadb.config import Settings
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Directory to your pdf files:
DATA_PATH = r"../papers"


def perform_RAG(prompt):
    # client = chromadb.PersistentClient(
    #     path="chromadb",
    #     settings=Settings(),
    #     tenant=DEFAULT_TENANT,
    #     database=DEFAULT_DATABASE,
    # )

    # # Get all collections and delete them
    # collections = client.list_collections()

    # for collection in collections:
    #     client.delete_collection(name=collection.name)  # Deleting the collection by name

    # print("All collections have been cleared.")
########################################################################################################################

    rag_client = chromadb.PersistentClient(
        path="chromadb",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

    # client = chromadb.Client(settings={"chromadb.storage": "sqlite", "chromadb.storage.path": "chromadb.db"})
    # Collection name
    collection_name = "docs"

    # Try to load the collection; if it doesn't exist, create it
    try:
        # Attempt to get the collection by name
        collection = rag_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' loaded successfully.")
    except Exception as e:
        # If collection doesn't exist, create it
        print(f"Collection '{collection_name}' not found. Creating a new one.")
        collection = rag_client.create_collection(name=collection_name)

        documents = load_documents()  # Load documents from a source
        chunks = split_text(documents)  # Split documents into manageable chunks

        # store each document in a vector embedding database
        for i, chunk in enumerate(chunks):
            d = chunk.page_content
            # print(f"Chunk {i}: {d}")
            response = ollama.embeddings(model="llama3.1", prompt=d)
            embedding = response["embedding"]
            # print(f"embedding: {embedding}")
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d]
            )

    # # an example prompt
    # prompt = "How does chain of thought prompting work?"

    # prompt = "What's the score of llama 3 8B on MATH (0-shot, CoT)?"

    # generate an embedding for the prompt and retrieve the most relevant doc
    embedding = ollama.embeddings(
    prompt=prompt,
    model="llama3.1"
    )["embedding"]
    # print(f"embedding: length {len(embedding)})\n{embedding}")

    results = collection.query(
    query_embeddings=[embedding],
    n_results=5
    )

    # print(f"results:\n{results}")

    # data = results['documents'][0][0]
    # Extract the documents from the results
    data1 = results['documents'][0][0]
    data2 = results['documents'][0][1]
    data3 = results['documents'][0][2]
    data4 = results['documents'][0][3]
    data5 = results['documents'][0][4]

    # Combine the data into a single string
    combined_data = f"{data1}\n\n{data2}\n\n{data3}\n\n{data4}\n\n{data5}"

    prompt = f"Using this data: {combined_data}. Respond to this prompt: {prompt}"

    # print(f"prompt: {prompt}")

    # generate a response combining the prompt and data we retrieved in step 2
    output = ollama.generate(
    model="llama3.1",
    prompt=prompt
    )

    print(f"response:\n{output['response']}")


def main():
    # search_google("Texas A&M University")
    perform_RAG("what is chain of thought?")

main()