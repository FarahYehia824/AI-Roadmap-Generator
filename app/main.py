import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Learning Planner",
    page_icon="✦",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;1,400&family=Outfit:wght@300;400;500;600&display=swap');

:root {
    --bg: #0d1117;
    --surface: #131a2e;
    --border: rgba(96,165,250,0.2);
    --accent: #3b82f6;
    --text: #f0f4ff;
    --muted: rgba(220,230,255,0.65);
    --card: rgba(15,23,42,0.7);
}

* { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    background-image:
        linear-gradient(135deg, rgba(13,17,23,0.92), rgba(19,26,46,0.95)),
        url('https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 700px !important;
    padding: 2rem 1.5rem 4rem !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.4);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #93c5fd;
    margin-bottom: 1.1rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.6rem, 6vw, 3.8rem);
    font-weight: 500;
    line-height: 1.1;
    color: #f0f4ff;
    margin: 0 0 0.6rem;
}
.hero-title em {
    font-style: italic;
    color: #93c5fd;
}
.hero-sub {
    color: rgba(220,230,255,0.65);
    font-size: 1rem;
    font-weight: 300;
    margin-top: 0.5rem;
}

/* ── Tracks ── */
.tracks {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin: 1.2rem 0 1.8rem;
}
.track-pill {
    background: rgba(96,165,250,0.1);
    border: 1px solid rgba(96,165,250,0.3);
    border-radius: 100px;
    padding: 6px 15px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #bfdbfe;
    letter-spacing: 0.02em;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid rgba(96,165,250,0.1);
    margin: 0 0 1.5rem;
}

/* ── Section label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: rgba(220,230,255,0.9);
    margin-bottom: 0.55rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: rgba(15,23,42,0.7) !important;
    border: 1px solid rgba(96,165,250,0.22) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.93rem !important;
    font-weight: 300 !important;
    padding: 1rem 1.1rem !important;
    resize: none !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(96,165,250,0.5) !important;
    box-shadow: 0 0 0 3px rgba(96,165,250,0.08) !important;
}
.stTextArea textarea::placeholder { color: rgba(148,163,184,0.5) !important; font-size: 0.88rem !important; }

/* ── Hint box ── */
.hint-box {
    background: rgba(96,165,250,0.07);
    border: 1px solid rgba(96,165,250,0.18);
    border-left: 3px solid #60a5fa;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.81rem;
    color: rgba(186,210,255,0.82);
    margin: 0.65rem 0 1.3rem;
    line-height: 1.5;
}
.hint-box b { color: #93c5fd; }

/* ── Level card ── */
.level-card {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(15,23,42,0.5);
    border: 1px solid rgba(96,165,250,0.15);
    border-radius: 12px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
}
.level-card-icon {
    width: 34px; height: 34px;
    border-radius: 8px;
    background: rgba(96,165,250,0.12);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
}
.level-card-text p { font-size: 0.88rem; font-weight: 500; color: #e2e8f0; margin: 0 0 2px; }
.level-card-sub { font-size: 0.74rem; color: rgba(148,163,184,0.7); }

/* ── Toggle ── */
.stToggle label {
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(15,23,42,0.7) !important;
    border: 1px solid rgba(96,165,250,0.22) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Primary button — واضح من الأول ── */
.stButton > button[kind="primary"] {
    background: #3b82f6 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.97rem !important;
    padding: 0.85rem 1.5rem !important;
    width: 100% !important;
    box-shadow: 0 0 0 1px #2563eb, 0 4px 20px rgba(59,130,246,0.5) !important;
    letter-spacing: 0.02em !important;
    transition: transform 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3b82f6 !important;
    box-shadow: 0 0 0 1px #2563eb, 0 4px 20px rgba(59,130,246,0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.07) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.12) !important;
}

/* ── Output card ── */
.output-wrapper {
    background: rgba(10,14,25,0.92);
    border: 1px solid rgba(96,165,250,0.25);
    border-radius: 14px;
    padding: 2rem;
    margin-top: 1.2rem;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.output-wrapper h1, .output-wrapper h2, .output-wrapper h3 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 500 !important;
    color: #f0f4ff !important;
}
.output-wrapper h2 { color: #93c5fd !important; }
.output-wrapper hr { border-color: rgba(96,165,250,0.1) !important; margin: 1.2rem 0 !important; }
.output-wrapper strong { color: #f0f4ff !important; }
.output-wrapper a { color: #93c5fd !important; }
.output-wrapper p, .output-wrapper li { color: rgba(220,230,255,0.85) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
}

/* ── Info box ── */
.stAlert {
    background: rgba(59,130,246,0.12) !important;
    border: 1px solid rgba(59,130,246,0.28) !important;
    border-radius: 10px !important;
    color: #bfdbfe !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(96,165,250,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Pipeline loader ───────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Setting up your planner...")
def load_pipeline():
    import shutil
    from pathlib import Path
    if Path("chroma_db").exists():
        shutil.rmtree("chroma_db")
    from pipeline.ingest import main as ingest
    ingest()
    from pipeline.generator import RoadmapPipeline
    return RoadmapPipeline()


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ AI-Powered</div>
    <div class="hero-title">Learning <em>Planner</em></div>
    <div class="hero-sub">Tell me your learning goal — I'll build your personalized roadmap.</div>
</div>
""", unsafe_allow_html=True)

tracks = ["Data Science & ML", "Frontend", "Backend", "DevOps & Cloud", "Android", "Cybersecurity"]
pills  = " ".join(f'<span class="track-pill">{t}</span>' for t in tracks)
st.markdown(f'<div class="tracks">{pills}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📝 What do you want to learn?</div>', unsafe_allow_html=True)

query = st.text_area(
    label="goal",
    label_visibility="collapsed",
    placeholder=(
        "Tell me your goal in your own words...\n\n"
        "e.g. I've never coded before and want to become a Data Scientist\n"
        "e.g. I know Python and want to break into Machine Learning\n"
        "e.g. أريد تعلم تطوير تطبيقات الأندرويد من الصفر"
    ),
    height=150,
)

st.markdown("""
<div class="hint-box">
  <b>💡 Try:</b> "How do I start coding?" · "Roadmap for AI engineer" · "Learn backend from scratch"
</div>
""", unsafe_allow_html=True)

# ── Level ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">🎯 Experience Level</div>', unsafe_allow_html=True)

col_text, col_toggle = st.columns([5, 1])
with col_text:
    st.markdown("""
    <div class="level-card">
        <div class="level-card-icon">🤖</div>
        <div class="level-card-text">
            <p>Auto-detect from my description</p>
            <span class="level-card-sub">Claude will figure out your level automatically</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_toggle:
    auto_detect = st.toggle(" ", value=True, label_visibility="collapsed")

if not auto_detect:
    level_choice = st.selectbox(
        label="level",
        label_visibility="collapsed",
        options=["Beginner", "Intermediate", "Advanced"],
    )
else:
    level_choice = None

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("✦ Build My Roadmap", type="primary")

# ── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    if not query.strip():
        st.warning("Please describe your learning goal first.")
        st.stop()

    pipeline = load_pipeline()

    with st.spinner("Searching knowledge base..."):
        result  = pipeline.retriever.retrieve(query, top_k=5)
        context = result.as_context_string()

    import os
    from groq import Groq
    from pipeline.generator import build_user_prompt, SYSTEM_PROMPT, detect_level

    client = Groq(api_key=os.getenv("OPENAI_API_KEY"))

    if auto_detect:
        with st.spinner("Understanding your level..."):
            level = detect_level(query, client)
        st.info(f"🤖 Detected level: **{level}**")
    else:
        level = level_choice
        st.info(f"📌 Level: **{level}**")

    st.markdown('<div class="output-wrapper">', unsafe_allow_html=True)
    placeholder = st.empty()
    full_text   = ""

    stream = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_user_prompt(query, context, level)},
        ],
        max_tokens=int(os.getenv("MAX_TOKENS", 2000)),
        temperature=0.4,
        stream=True,
    )

    for chunk in stream:
        delta     = chunk.choices[0].delta.content or ""
        full_text += delta
        placeholder.markdown(full_text + "▌")

    placeholder.markdown(full_text)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇ Download Roadmap",
            data=full_text,
            file_name="learning_plan.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        if st.button("↺ Start Over", use_container_width=True):
            st.rerun()