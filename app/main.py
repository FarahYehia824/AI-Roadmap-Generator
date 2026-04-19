"""
app/main.py
───────────
Streamlit UI for RoadmapRAG

Run:
    streamlit run app/main.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from pipeline.generator import RoadmapPipeline

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Learning Planner",
    page_icon="🗺️",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #f7f8fc;
    --surface: #eef0f7;
    --border: #d8dce8;
    --accent: #1b3a6b;
    --accent-dim: #142d54;
    --accent-light: #e8edf7;
    --text: #0f1c35;
    --muted: #6b7694;
    --card: #ffffff;
}

* { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    background-image: 
        linear-gradient(rgba(10,10,15,0.85), rgba(10,10,15,0.95)),
        url('https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1920&q=80') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 720px !important;
    padding: 3rem 1.5rem 4rem !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2.5rem;
}
.hero-eyebrow {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Instrument Serif', serif;
    font-size: clamp(2.8rem, 6vw, 4.2rem);
    font-weight: 400;
    line-height: 1.1;
    color: var(--text);
    margin: 0 0 0.5rem;
    white-space: nowrap;
}
.hero-title em {
    font-style: italic;
    color: var(--accent);
}
.hero-sub {
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    margin-top: 0.75rem;
}

/* ── Tracks ── */
.tracks {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin: 1.5rem 0 2.5rem;
}
.track-pill {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 0.78rem;
    color: var(--muted);
    letter-spacing: 0.02em;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 0 0 2rem;
}

/* ── Input label ── */
.input-label {
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.97rem !important;
    padding: 1rem 1.1rem !important;
    resize: none !important;
    transition: border-color 0.2s !important;
    box-shadow: 0 1px 4px rgba(27,58,107,0.06) !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(27,58,107,0.10) !important;
}
.stTextArea textarea::placeholder { color: #b0b8cc !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hint box ── */
.hint-box {
    background: var(--accent-light);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.83rem;
    color: var(--muted);
    margin: 1rem 0 1.5rem;
    line-height: 1.6;
}
.hint-box b { color: var(--text); }

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.5rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(27,58,107,0.18) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-dim) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(27,58,107,0.25) !important;
}

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1rem !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Output ── */
.output-wrapper {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow: 0 2px 12px rgba(27,58,107,0.07);
}
.output-wrapper h1, .output-wrapper h2, .output-wrapper h3 {
    font-family: 'Instrument Serif', serif !important;
    font-weight: 400 !important;
    color: var(--text) !important;
}
.output-wrapper h2 { color: var(--accent) !important; }
.output-wrapper hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
.output-wrapper strong { color: var(--text) !important; }
.output-wrapper a { color: var(--accent) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}

/* ── Alert / spinner ── */
.stAlert {
    background: var(--accent-light) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.stSpinner > div { color: var(--accent) !important; }

/* ── Toggle ── */
.stToggle label { color: var(--muted) !important; font-size: 0.85rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Load pipeline ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI pipeline...")
def load_pipeline():
    return RoadmapPipeline()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ AI-Powered</div>
    <div class="hero-title">Learning<em>Planner</em></div>
    <div class="hero-sub">Tell me your learning goal — I'll build your personalized roadmap.</div>
</div>
""", unsafe_allow_html=True)

tracks = ["Data Science & ML", "Frontend", "Backend", "DevOps & Cloud", "Android", "Cybersecurity"]
pills  = " ".join(f'<span class="track-pill">{t}</span>' for t in tracks)
st.markdown(f'<div class="tracks">{pills}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-label">What do you want to learn?</div>', unsafe_allow_html=True)

query = st.text_area(
    label="goal",
    label_visibility="collapsed",
    placeholder=(
        "Tell me about yourself and what you want to learn...\n\n"
        "e.g. I've never coded before and want to become a Data Scientist\n"
        "e.g. I know Python well and want to get into Machine Learning\n"
        "e.g. I finished a bootcamp and want to learn backend development\n"
        "e.g. أريد تعلم تطوير تطبيقات الأندرويد من الصفر"
    ),
    height=180,
)

st.markdown("""
<div class="hint-box">
  <b>💡 Try:</b>
  "I want to learn web development" · "Help me get into cybersecurity" · "I want to become an Android developer"
</div>
""", unsafe_allow_html=True)


# ── Level ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-label">Experience level</div>', unsafe_allow_html=True)

auto_detect = st.toggle("🤖 Auto-detect from my description", value=True)

if not auto_detect:
    level_choice = st.selectbox(
        label="level",
        label_visibility="collapsed",
        options=["Beginner", "Intermediate", "Advanced"],
    )
else:
    level_choice = None

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Generate My Roadmap", type="primary")


# ── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    if not query.strip():
        st.warning("Please enter your learning goal first.")
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
        with st.spinner("Detecting your level..."):
            level = detect_level(query, client)
        st.info(f"🤖 Detected level: **{level}**")
    else:
        level = level_choice
        st.info(f"📌 Selected level: **{level}**")

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
            "⬇️ Download Roadmap",
            data=full_text,
            file_name="my_roadmap.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        if st.button("🔄 Generate Another", use_container_width=True):
            st.rerun()