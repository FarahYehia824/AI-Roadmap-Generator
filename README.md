# 🗺️ RoadmapRAG — AI-Powered Learning Path Generator

> Give it a goal. Get a personalized, structured roadmap.

RoadmapRAG is a **Retrieval-Augmented Generation (RAG)** system that takes a user's learning goal and generates a detailed, step-by-step roadmap with curated resources — powered by semantic search and an LLM.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Goal-to-Roadmap** | Input any learning goal → get a structured roadmap |
| 🔍 **Semantic Search** | Finds the most relevant skills using vector similarity |
| 📚 **Resource Recommendations** | Curated courses for every step |
| ⚡ **Personalized Plans** | Adapts to Beginner / Intermediate / Advanced |
| 🗓️ **Time Estimates** | Weekly schedule for each step |
| 💬 **Streamlit UI** | Clean chat-based interface |

---

## 🏗️ Project Structure


roadmap-rag/
│
├── data/                        # 📦 Knowledge base (JSON files)
│   ├── skills.json              #   33 skills across 6 tracks
│   ├── roadmaps.json            #   6 learning tracks with ordered steps
│   └── resources.json           #   72 curated courses & resources
│
├── pipeline/                    # 🧠 RAG pipeline
│   ├── ingest.py                #   Load data → embed → store in ChromaDB
│   ├── retriever.py             #   Semantic search over vector store
│   └── generator.py             #   Build prompt → call LLM → return roadmap
│
├── app/
│   └── main.py                  # 🖥️ Streamlit UI
│
├── tests/
│   └── test_pipeline.py         # ✅ Unit tests
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── 02_embeddings_demo.ipynb
│
├── validate_data.py             # 🔍 Data integrity checker
├── .env.example                 # Environment variables template
├── requirements.txt
└── README.md


---

## ⚙️ How It Works


User Input
    │
    ▼
[ Embedding Model ]     →   converts goal to vector
    │
    ▼
[ ChromaDB Search ]     →   finds top-K relevant skills & steps
    │
    ▼
[ Context Builder ]     →   assembles retrieved data into context
    │
    ▼
[ LLM (GPT-4o-mini) ]  →   generates structured roadmap
    │
    ▼
Personalized Roadmap ✅


---

## 🚀 Quickstart

\`\`\`bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/roadmap-rag.git
cd roadmap-rag

# 2. Virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# add your OPENAI_API_KEY to .env

# 5. Ingest data (builds the vector store)
python -m pipeline.ingest

# 6. Run
streamlit run app/main.py
\`\`\`

---

## 🗃️ Data Overview

| File | Records | Description |
|------|---------|-------------|
| `skills.json` | 33 | Skills with prerequisites & time estimates |
| `roadmaps.json` | 6 tracks | Ordered steps with why & milestones |
| `resources.json` | 72 courses | Curated resources per skill |

**Tracks:** Data Science & ML · Frontend · Backend · DevOps & Cloud · Android · Cybersecurity

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Vector DB | `ChromaDB` |
| LLM | `OpenAI GPT-4o-mini` |
| Orchestration | `LangChain` |
| UI | `Streamlit` |

---

## 🗺️ Project Roadmap

- [x] Design data schema
- [x] Build knowledge base (skills + roadmaps + resources)
- [x] Data validation script
- [ ] `ingest.py` — embed and store in ChromaDB
- [ ] `retriever.py` — semantic search
- [ ] `generator.py` — prompt builder + LLM call
- [ ] `app/main.py` — Streamlit UI

---

## 📄 License

MIT License
