# ─────────────────────────────────────────────────────────────────────────────
# rag_word.py  —  Chat with any Word Document (.docx) using OpenAI + LangChain
#
# WHAT THIS APP DOES:
#   1. You upload a Word file (.docx) through a Gradio web UI
#   2. The document is split into small chunks and embedded (converted to numbers)
#   3. Those embeddings are stored in ChromaDB (an in-memory vector database)
#   4. When you ask a question, ChromaDB finds the most relevant chunks
#   5. Those chunks + your question are sent to GPT-4o-mini to generate an answer
# ─────────────────────────────────────────────────────────────────────────────

import os  # reads environment variables (the API key)
import gradio as gr  # builds the web UI — no HTML needed

# LangChain components — each does one specific job in the pipeline:
from langchain_community.document_loaders import Docx2txtLoader
# ↑ reads a Word file (.docx) and extracts the text

from langchain_text_splitters import RecursiveCharacterTextSplitter
# ↑ splits long texts into smaller chunks that fit in the LLM context window

from langchain_chroma import Chroma
# ↑ ChromaDB integration — stores and searches embedding vectors

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# ↑ OpenAIEmbeddings: converts text → 1536-dimension float vectors via OpenAI API
#   ChatOpenAI: the GPT model client (here we use gpt-4o-mini)

from langchain_classic.chains import ConversationalRetrievalChain
# ↑ a pre-built LangChain chain that:
#   - reformulates the question using chat history
#   - retrieves relevant documents
#   - passes everything to the LLM

from langchain_classic.memory import ConversationBufferMemory
# ↑ stores the full conversation (all Q&A turns) and injects it into each prompt

from dotenv import load_dotenv

# ↑ reads the .env file and sets environment variables

load_dotenv()  # must be called early — before any OpenAI clients are created


# ── FUNCTION: load_and_index ──────────────────────────────────────────────────
# Takes a Word file path, runs the full indexing pipeline, returns a retriever.
# This is called once when the user uploads a Word document.
def load_and_index(file_path: str):
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set. Add it to .env")

    # STEP 1 — Load Word Document
    loader = Docx2txtLoader(file_path)
    pages = loader.load()
    print(f"Loaded document text")

    # STEP 2 — Chunk the text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")

    # STEP 3 — Embed and store in ChromaDB
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(chunks, embedding=embeddings)

    # STEP 4 — Return a retriever
    # k=4 means: return the 4 chunks most similar to the question.
    return vectorstore.as_retriever(search_kwargs={"k": 4})


# ── FUNCTION: build_chain ─────────────────────────────────────────────────────
# Wraps the retriever in a LangChain conversational RAG chain.
def build_chain(retriever):
    # The LLM that generates the final answer.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # ConversationBufferMemory stores every (question, answer) pair.
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # ConversationalRetrievalChain combines Memory, Retriever, and the LLM.
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    return chain


# Global variable — stores the chain between Gradio events.
# None means no document has been uploaded yet.
chain = None


# ── FUNCTION: upload_word ─────────────────────────────────────────────────────
# Triggered when the user uploads a Word file in the Gradio UI.
def upload_word(word_file):
    global chain  # we modify the global chain variable
    if word_file is None:
        return "No file uploaded.", []

    file_path = word_file if isinstance(word_file, str) else word_file.name
    retriever = load_and_index(file_path)  # index the Word document
    chain = build_chain(retriever)  # build the RAG chain

    return "✅ Word document indexed! Ask me anything about it.", []


# ── FUNCTION: ask_question ────────────────────────────────────────────────────
# Triggered when the user types a question and presses Enter.
def ask_question(question, history):
    global chain
    history = history or []

    if chain is None:  # Document not uploaded yet
        return history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": "Please upload a Word document first."},
        ]

    # chain.invoke() runs the full pipeline
    result = chain.invoke({"question": question})
    answer = result["answer"]

    # Append source metadata to the UI answer
    sources = result.get("source_documents", [])
    if sources:
        # Word docs usually don't have 'page' metadata, so we show the source file name instead
        source_names = set(os.path.basename(str(doc.metadata.get("source", "Word Document"))) for doc in sources)
        answer += f"\n\n_Sources: {', '.join(source_names)}_"


    print(f"\n{'-' * 50}")
    print(f"❓ QUESTION: {question}")

    print(f"💡 LLM ANSWER: {result['answer']}\n")
    print("📚 RETRIEVED CONTEXT CHUNKS:")
    for i, doc in enumerate(sources, start=1):
        print(f"\n--- Chunk {i} ---")
        print(doc.page_content)
    print(f"{'-' * 50}\n")
    # ----------------------------------

    return history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]


# ── GRADIO UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(title="Chat with Your Word Document") as demo:
    gr.Markdown("## 📄 Chat with Your Word Document\nUpload a `.docx` file, then ask questions.")

    with gr.Row():
        word_input = gr.File(label="Upload Word Document", file_types=[".docx"])
        status = gr.Textbox(label="Status", interactive=False)

    chatbot = gr.Chatbot(label="Conversation", height=400)
    question_input = gr.Textbox(placeholder="Ask about your document...")

    # .change() fires when the file input changes (Word doc is uploaded)
    word_input.change(fn=upload_word, inputs=word_input, outputs=[status, chatbot])

    # .submit() fires when user presses Enter in the textbox
    question_input.submit(
        fn=ask_question,
        inputs=[question_input, chatbot],
        outputs=chatbot
    )

    gr.Examples(
        examples=[
            ["What specific evidence, data, or examples are used to support the main claims?"],
            ["Can you identify any major challenges, limitations, or risks discussed in the text?"],
            ["Based on the document, what are the future implications or final recommendations?"],
            ["How do the different sections of this document connect to form the overall conclusion?"],
            ["Extract 3 obscure but interesting facts mentioned deep in the document."]],
        inputs=question_input
    )

if __name__ == "__main__":
    demo.launch()  # opens http://localhost:7860 in your browser