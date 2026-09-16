from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma


# -----------------------------
# Local Ollama models
# -----------------------------

EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "gemma2:2b"


# -----------------------------
# Embedding model
# -----------------------------

embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL
)


# -----------------------------
# Chat model
# -----------------------------

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0
)


# -----------------------------
# Load PDF
# -----------------------------

def load_pdf(file_path):

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    return documents


# -----------------------------
# Split document
# -----------------------------

def split_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


# -----------------------------
# Create vector database
# -----------------------------

def create_vectorstore(chunks):

    # Create empty Chroma collection
    vectorstore = Chroma(
        collection_name="rag_documents",
        embedding_function=embeddings
    )

    # Process embeddings in small batches
    batch_size = 20

    total_chunks = len(chunks)

    for i in range(0, total_chunks, batch_size):

        batch = chunks[i:i + batch_size]

        start = i + 1
        end = min(i + batch_size, total_chunks)

        print(
            f"Embedding chunks {start}-{end} "
            f"of {total_chunks}"
        )

        vectorstore.add_documents(batch)

    print("All chunks embedded successfully.")

    return vectorstore


# -----------------------------
# Retrieve relevant chunks
# -----------------------------

def retrieve_documents(vectorstore, question):

    results = vectorstore.similarity_search(
        question,
        k=4
    )

    return results


# -----------------------------
# Generate answer
# -----------------------------

def generate_answer(question, documents):

    # Combine retrieved chunks
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information
provided in the document context.

If the answer cannot be found in the document, say:

"I could not find the answer in the uploaded document."

Do not make up information.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = llm.invoke(prompt)

    return response.content