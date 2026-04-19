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
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --border: rgba(255,255,255,0.15);
    --accent: #ffffff;
    --text: #ffffff;
    --muted: rgba(255,255,255,0.6);
    --card: rgba(10,10,20,0.75);
}

* { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    background-image:
        linear-gradient(rgba(10,10,15,0.68), rgba(10,10,15,0.72)),
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
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.7);
    margin-bottom: 0.8rem;
}
.hero-title {
    font-family: 'Instrument Serif', serif;
    font-size: clamp(2.6rem, 6vw, 3.8rem);
    font-weight: 400;
    line-height: 1.1;
    color: #ffffff;
    margin: 0 0 0.6rem;
}
.hero-title em {
    font-style: italic;
    color: rgba(255,255,255,0.85);
}
.hero-sub {
    color: rgba(255,255,255,0.75);
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
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.28);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 0.78rem;
    color: #ffffff;
    letter-spacing: 0.02em;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.12);
    margin: 0 0 1.5rem;
}

/* ── Section label ── */
.section-label {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.9);
    margin-bottom: 0.5rem;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: rgba(10,10,20,0.7) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 1rem 1.1rem !important;
    resize: none !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(255,255,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.06) !important;
}
.stTextArea textarea::placeholder { color: rgba(255,255,255,0.35) !important; }

/* ── Hint box ── */
.hint-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    border-left: 3px solid rgba(255,255,255,0.6);
    border-radius: 10px;
    padding: 10px 15px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.8);
    margin: 0.7rem 0 1.2rem;
    line-height: 1.5;
}
.hint-box b { color: #ffffff; }

/* ── Toggle ── */
.stToggle label {
    color: #ffffff !important;
    font-size: 0.9rem !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(10,10,20,0.7) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.5rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.45) !important;
}

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.14) !important;
}

/* ── Output card ── */
.output-wrapper {
    background: rgba(10,10,20,0.82);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 2rem;
    margin-top: 1.2rem;
}
.output-wrapper h1, .output-wrapper h2, .output-wrapper h3 {
    font-family: 'Instrument Serif', serif !important;
    font-weight: 400 !important;
    color: #ffffff !important;
}
.output-wrapper h2 { color: #93c5fd !important; }
.output-wrapper hr { border-color: rgba(255,255,255,0.1) !important; margin: 1.2rem 0 !important; }
.output-wrapper strong { color: #ffffff !important; }
.output-wrapper a { color: #93c5fd !important; }
.output-wrapper p, .output-wrapper li { color: rgba(255,255,255,0.85) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
}

/* ── Info box ── */
.stAlert {
    background: rgba(37,99,235,0.15) !important;
    border: 1px solid rgba(37,99,235,0.3) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
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
st.markdown('<div class="section-label">What do you want to learn?</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-label">Experience Level</div>', unsafe_allow_html=True)

left, right = st.columns([5, 1])
with right:
    auto_detect = st.toggle(" ", value=True)
with left:
    st.markdown('<p style="color:#ffffff; font-size:0.95rem; margin-top:0.4rem;">🤖 Auto-detect from my description</p>', unsafe_allow_html=True)
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