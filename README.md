<div align="center">

<!-- Animated gradient wave header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=220&section=header&text=🎓%20Final%20Assignments&fontSize=52&fontColor=ffffff&animation=fadeIn&desc=NLP%20·%20Vector%20Databases%20·%20RAG%20·%20AI%20Agents&descSize=20&descAlignY=78" width="100%" alt="header"/>

<!-- Animated typing tagline -->
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=2800&pause=700&color=36BCF7&center=true&vCenter=true&width=700&lines=🧠+From+NLP+Theory+to+Production+AI+Agents;🔎+Semantic+Search+with+Vector+Databases;📄+RAG+Chatbot+for+Word+Documents;🍣+Full+Restaurant+AI+Agent+with+n8n+Automation" alt="typing"/>

<br/><br/>

<!-- Tech stack badges -->
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain"/>
<img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
<img src="https://img.shields.io/badge/ChromaDB-Vector_Store-5B5FC7?style=for-the-badge" alt="ChromaDB"/>
<br/>
<img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
<img src="https://img.shields.io/badge/Gradio-Web_UI-FF7C00?style=for-the-badge&logo=gradio&logoColor=white" alt="Gradio"/>
<img src="https://img.shields.io/badge/n8n-Automation-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" alt="n8n"/>
<img src="https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>

<br/><br/>

**Four hands-on assignments that build on each other — starting with core NLP theory and ending with a complete, production-style AI agent.**

</div>

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%" alt="divider"/>

## 🗺️ The Learning Journey

Each assignment is one step in a progression — theory → embeddings → retrieval → autonomous agent:

```mermaid
flowchart LR
    A1["📚 Assignment 1<br/><b>NLP & AI Theory</b><br/>Tokenization, TF-IDF,<br/>Embeddings, RAG, MCP"]
    A2["🚗 Assignment 2<br/><b>Vector Database</b><br/>ChromaDB +<br/>Semantic Search"]
    A3["📄 Assignment 3<br/><b>RAG Chatbot</b><br/>Chat with your<br/>Word documents"]
    A4["🍣 Assignment 4<br/><b>Restaurant AI Agent</b><br/>Full agent + SQLite<br/>+ n8n automation"]

    A1 == "concepts" ==> A2
    A2 == "embeddings & retrieval" ==> A3
    A3 == "RAG + LLM chains" ==> A4

    style A1 fill:#1e3a5f,stroke:#36BCF7,color:#ffffff
    style A2 fill:#3b2a5f,stroke:#a78bfa,color:#ffffff
    style A3 fill:#1f4d3a,stroke:#34d399,color:#ffffff
    style A4 fill:#5f2a2a,stroke:#f97316,color:#ffffff
```

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%" alt="divider"/>

## 📂 Assignments at a Glance

| # | Project | What It Does | Core Tech | Link |
|:-:|---|---|---|:-:|
| 1️⃣ | **📚 Theory Questions** | 12 clear Q&A explanations of NLP, RAG, Docker & AI-agent fundamentals | Markdown | [Open ➜](./Assignment-1_Theory%20Questions) |
| 2️⃣ | **🚗 Vector Database** | Semantic search over car descriptions — meaning, not keywords | ChromaDB · MiniLM Embeddings | [Open ➜](./Assignment-2_Vector-Database) |
| 3️⃣ | **📄 RAG Chatbot for Word** | Upload a `.docx`, ask questions, get grounded answers with sources | LangChain · OpenAI · ChromaDB · Gradio | [Open ➜](./Assignment-3_RAG_ChatBot-Word) |
| 4️⃣ | **🍣 Restaurant AI Agent** | Full agent: menu Q&A, reservations, cancellations & email automation | LangChain · OpenAI · SQLite · n8n · Docker | [Open ➜](./Assignment-4_Restaurant-AI-Agent) |

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%" alt="divider"/>

## 🔍 Explore Each Assignment

<!-- Interactive collapsible sections — click to expand! -->

<details>
<summary><h3>1️⃣ 📚 Theory Questions — NLP, RAG, Docker & AI Agents</h3></summary>

<br/>

Clear, example-driven answers to **12 fundamental questions**, including:

| Topic Area | Questions Covered |
|---|---|
| 🔤 **NLP Basics** | Tokenization · Stemming vs. Lemmatization · TF-IDF |
| 🧠 **Embeddings** | Sentence embeddings · Cosine similarity · Why `LIKE '%pizza%'` can't do semantic search |
| 📚 **RAG** | The problem RAG solves · Main steps of a RAG pipeline |
| 🐳 **Infrastructure** | Docker image vs. container |
| 🤖 **Agents** | AI agents with tools vs. simple chatbots · MCP · Agent Skills |

Every answer includes concrete examples — like how `better` → `good` in lemmatization but stays `better` in stemming.

**➜ [Read the full Q&A](./Assignment-1_Theory%20Questions)**

</details>

<details>
<summary><h3>2️⃣ 🚗 Vector Database — Semantic Search with ChromaDB</h3></summary>

<br/>

A lightweight project proving that **search by meaning beats search by keywords**:

```text
Text Data → Embeddings → Vector Database → Semantic Query → Relevant Results
```

- 🚙 Embeds **15 vehicle descriptions** with local `all-MiniLM-L6-v2` embeddings — **no API key needed**
- 🏷️ Attaches structured metadata (brand, type, year)
- 🔎 Runs natural-language queries like *"zero emissions high tech transport"* → correctly finds the electric car
- 📏 Ranks results by vector distance scores

**➜ [Explore the project](./Assignment-2_Vector-Database)**

</details>

<details>
<summary><h3>3️⃣ 📄 RAG Chatbot — Chat with Your Word Documents</h3></summary>

<br/>

**Upload a Word document → index it → ask questions → get grounded answers with sources.**

```mermaid
flowchart LR
    A[📄 Upload .docx] --> B[✂️ Split into Chunks]
    B --> C[🧠 OpenAI Embeddings]
    C --> D[(🗄️ ChromaDB)]
    E[💬 Question] --> F[🔎 Retrieve Chunks]
    D --> F
    F --> G[🤖 GPT Answer + Source]
```

- 📤 Upload `.docx` files directly in the browser (Gradio UI)
- 🧩 Automatic chunking for better retrieval
- 💬 Conversational Q&A with memory for follow-up questions
- 📚 Every answer cites its source document

**➜ [Explore the project](./Assignment-3_RAG_ChatBot-Word)**

</details>

<details>
<summary><h3>4️⃣ 🍣 Restaurant AI Agent — The Grand Finale</h3></summary>

<br/>

A complete AI agent for **Sakura Asian Kitchen** — the most advanced project in the repo:

```mermaid
flowchart LR
    UI["💻 CLI / 🌐 Gradio / ✨ HTML Chat"] --> BOT["🤖 LangChain Agent"]
    BOT <--> DB[("🗄️ SQLite<br/>40 menu items")]
    BOT <--> LLM["🧠 GPT-4o-mini"]
    BOT -- "webhook" --> N8N["⚙️ n8n"] --> MAIL["📧 Email"]
```

- 🍜 **Menu Q&A** — dietary filters, allergies, full-course recommendations, tip calculations
- 📅 **Smart reservations** — multi-turn detail collection, validations (party ≤ 15, operating hours), duplicate prevention
- ❌ **Cancellations** — by booking ID or customer name
- 📧 **n8n email automation** — Dockerized workflow sends confirmation emails
- ✅ **Smoke tests** — full regression suite that costs zero API credits
- 💻 **3 interfaces** sharing one backend: CLI, Gradio, and a custom HTML chat page

**➜ [Explore the project](./Assignment-4_Restaurant-AI-Agent)**

</details>

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%" alt="divider"/>

## 🛠️ Skills Demonstrated

```mermaid
mindmap
  root((🎓 Skills))
    🔤 NLP Foundations
      Tokenization
      TF-IDF
      Embeddings
    🔎 Retrieval
      ChromaDB
      Semantic Search
      RAG Pipelines
    🤖 AI Engineering
      LangChain Chains
      Prompt Engineering
      Question Routing
    ⚙️ Production
      SQLite
      Docker
      n8n Automation
      Testing
```

| Category | Skills |
|---|---|
| 🧠 **AI / LLM** | Prompt engineering, LLM routing, structured JSON extraction, conversation memory, grounded answering |
| 🔎 **Retrieval** | Embeddings, vector databases, semantic search, chunking, RAG pipelines |
| 🏗️ **Engineering** | Python, SQLite schema design, REST webhooks, multi-interface architecture, error handling |
| 🚀 **DevOps & QA** | Docker Compose, n8n workflow automation, smoke & regression testing, environment configuration |

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%" alt="divider"/>

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/AmitZalman/Final_Assignments.git
cd Final_Assignments

# Each assignment is self-contained — pick one and dive in:
cd Assignment-4_Restaurant-AI-Agent
pip install -r requirements.txt
python restaurant_chatbot_app.py
```

> 💡 Each assignment folder contains its own detailed README with full setup steps, architecture charts, and usage examples.

---

<div align="center">

### 👨‍💻 Built by Amit Zalman

*From theory to a working AI agent — one assignment at a time.*

<br/>

<!-- Animated wave footer -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=130&section=footer" width="100%" alt="footer"/>

</div>
