from rag import (
    load_pdf,
    split_documents,
    create_vectorstore,
    retrieve_documents,
    generate_answer
)

PDF_PATH = "test.pdf"

print("1. Loading PDF...")

documents = load_pdf(PDF_PATH)

print(f"   Pages loaded: {len(documents)}")

print("2. Splitting document...")

chunks = split_documents(documents)

print(f"   Chunks created: {len(chunks)}")

print("3. Creating vector database...")

vectorstore = create_vectorstore(chunks)

print("   Vector database created successfully!")

question = input("\nAsk a question about your PDF: ")

print("\n4. Searching the document...")

results = retrieve_documents(
    vectorstore,
    question
)

print(f"   Relevant chunks found: {len(results)}")

print("\n5. Generating answer using Gemma...")

answer = generate_answer(
    question,
    results
)

print("\n================ ANSWER ================")
print(answer)
print("=========================================")