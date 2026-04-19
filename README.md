# 🗺️ Learning Planner — AI-Powered Learning Path Generator

> Give it a goal. Get a personalized, structured roadmap.

**Learning Planner** is a Retrieval-Augmented Generation (RAG) system that takes your learning goal in natural language — in Arabic or English — and generates a detailed, step-by-step roadmap with curated resources, powered by semantic search and an LLM.

🔗 **Live App:** [learning-planner.streamlit.app](https://learning-planner.streamlit.app/)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Goal-to-Roadmap** | Input any learning goal → get a structured roadmap |
| 🔍 **Semantic Search** | Finds the most relevant skills using FAISS vector similarity |
| 📚 **Resource Recommendations** | 72 curated courses for every step |
| 🤖 **Auto-detect Level** | Detects your experience level from how you describe yourself |
| ⚡ **Multilingual** | Works in Arabic and English |
| 🗓️ **Time Estimates** | Weekly schedule and milestones for each step |
| ⬇️ **Download Roadmap** | Export your roadmap as a Markdown file |

---

## 🏗️ Project Structure

```
roadmap-rag/
│
├── data/                        # 📦 Knowledge base (JSON files)
│   ├── skills.json              #   33 skills across 6 tracks
│   ├── roadmaps.json            #   6 learning tracks with ordered steps
│   └── resources.json           #   72 curated courses & resources
│
├── pipeline/                    # 🧠 RAG pipeline
│   ├── ingest.py                #   Load data → embed → store in FAISS
│   ├── retriever.py             #   Semantic search over FAISS vector store
│   └── generator.py             #   Build prompt → call LLM → return roadmap
│
├── app/
│   └── main.py                  # 🖥️ Streamlit UI
│
├── validate_data.py             # 🔍 Data integrity checker
├── .env.example                 # Environment variables template
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

```
User Input (Arabic or English)
        │
        ▼
[ Sentence Transformers ]   →   converts goal to vector
        │
        ▼
[ FAISS Search ]            →   finds top-K relevant skills & steps
        │
        ▼
[ Context Builder ]         →   assembles retrieved chunks into context
        │
        ▼
[ Groq — Llama 3.3 70B ]   →   generates structured roadmap
        │
        ▼
Personalized Roadmap ✅
```

---

## 🚀 Quickstart

```bash
# 1. Clone
git clone https://github.com/FarahYehia824/AI-Roadmap-Generator.git
cd AI-Roadmap-Generator

# 2. Virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 5. Ingest data (builds the FAISS vector store)
python -m pipeline.ingest

# 6. Run
streamlit run app/main.py
```

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
| Vector Store | `FAISS` |
| LLM | `Groq — Llama 3.3 70B` |
| UI | `Streamlit` |
| Language | `Python 3.11+` |

---

## 🗺️ Project Roadmap

- [x] Design data schema (skills + roadmaps + resources)
- [x] Build knowledge base — 33 skills, 45 steps, 72 resources
- [x] Data validation script
- [x] `ingest.py` — chunking + embedding + FAISS store
- [x] `retriever.py` — semantic search
- [x] `generator.py` — smart prompt builder + LLM call
- [x] Auto-detect user level from natural language
- [x] Arabic + English support
- [x] `app/main.py` — Streamlit UI with dark library theme
- [x] Deploy on Streamlit Cloud

---

## 📄 License

MIT License
