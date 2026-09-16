import streamlit as st
import tempfile
import os

from rag import (
    load_pdf,
    split_documents,
    create_vectorstore,
    retrieve_documents,
    generate_answer
)


# --------------------------------
# Page configuration
# --------------------------------

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="📚",
    layout="centered"
)


# --------------------------------
# Title
# --------------------------------

st.title("📚 RAG Document Chatbot")

st.write(
    "Upload a PDF and ask questions about its content."
)


# --------------------------------
# Initialize session state
# --------------------------------

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------
# File uploader
# --------------------------------

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)


# --------------------------------
# Process a NEW PDF
# --------------------------------

if uploaded_file is not None:

    # Only process if this is a new file
    if uploaded_file.name != st.session_state.document_name:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(
                uploaded_file.getvalue()
            )

            temp_file_path = temp_file.name


        try:

            with st.spinner(
                "📖 Reading and processing your PDF..."
            ):

                # Load PDF
                documents = load_pdf(
                    temp_file_path
                )

                # Split into chunks
                chunks = split_documents(
                    documents
                )

                st.info(
                    f"📄 Pages: {len(documents)} | "
                    f"Chunks: {len(chunks)}"
                )

                # Create vector database
                vectorstore = create_vectorstore(
                    chunks
                )


            # Save vector database
            st.session_state.vectorstore = vectorstore

            st.session_state.document_name = (
                uploaded_file.name
            )

            # Clear previous conversation
            st.session_state.messages = []

            st.success(
                f"✅ {uploaded_file.name} processed successfully!"
            )

        finally:

            if os.path.exists(temp_file_path):

                os.remove(temp_file_path)


# --------------------------------
# Display previous messages
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# --------------------------------
# Chat
# --------------------------------

if st.session_state.vectorstore is not None:

    question = st.chat_input(
        "Ask something about your PDF..."
    )


    if question:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        with st.chat_message("user"):

            st.write(question)


        # Retrieve relevant chunks
        with st.spinner(
            "🔎 Searching the document..."
        ):

            results = retrieve_documents(
                st.session_state.vectorstore,
                question
            )


        # Generate answer
        with st.spinner(
            "🤖 Generating answer..."
        ):

            answer = generate_answer(
                question,
                results
            )


        # Save assistant message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        with st.chat_message("assistant"):

            st.write(answer)


else:

    st.info(
        "👆 Upload a PDF above to start chatting."
    )