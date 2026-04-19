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
    page_title="RoadmapRAG",
    page_icon="🗺️",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 800px; }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center;
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    .track-badge {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        margin: 3px;
        color: #cbd5e1;
    }
    .tip-box {
        background: #0f172a;
        border-left: 3px solid #6366f1;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #94a3b8;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Load pipeline (cached — loads once per session) ───────────────────────────
@st.cache_resource(show_spinner="Loading AI pipeline...")
def load_pipeline():
    return RoadmapPipeline()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🗺️ RoadmapRAG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Tell me your learning goal — I\'ll build your personalized roadmap.</div>',
    unsafe_allow_html=True,
)

# Tracks badges
tracks = ["Data Science & ML", "Frontend", "Backend", "DevOps & Cloud", "Android", "Cybersecurity"]
badges = " ".join(f'<span class="track-badge">{t}</span>' for t in tracks)
st.markdown(f"<div style='text-align:center;margin-bottom:2rem'>{badges}</div>", unsafe_allow_html=True)

st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
query = st.text_area(
    label="Your goal",
    placeholder=(
        "Tell me about yourself and what you want to learn...\n\n"
        "e.g. I've never coded before and want to become a Data Scientist\n"
        "e.g. I know Python well and want to get into Machine Learning\n"
        "e.g. I finished a bootcamp and want to learn backend development"
    ),
    label_visibility="collapsed",
    height=120,
)

# Level selector
st.markdown("**Your experience level:**")
col_auto, col_beg, col_int, col_adv = st.columns(4)

with col_auto:
    auto_detect = st.toggle("🤖 Auto-detect", value=True)
with col_beg:
    lvl_beg = st.button("🟢 Beginner",      use_container_width=True, disabled=auto_detect)
with col_int:
    lvl_int = st.button("🟡 Intermediate",  use_container_width=True, disabled=auto_detect)
with col_adv:
    lvl_adv = st.button("🔴 Advanced",      use_container_width=True, disabled=auto_detect)

# Store manual level in session
if lvl_beg: st.session_state["manual_level"] = "Beginner"
if lvl_int: st.session_state["manual_level"] = "Intermediate"
if lvl_adv: st.session_state["manual_level"] = "Advanced"

manual_level = st.session_state.get("manual_level", "Beginner")


# Example queries
st.markdown("""
<div class="tip-box">
💡 <b>Try:</b>
"I want to learn web development" &nbsp;·&nbsp;
"Help me get into cybersecurity" &nbsp;·&nbsp;
"I want to become an Android developer"
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

generate_btn = st.button("🚀 Generate My Roadmap", use_container_width=True, type="primary")

# ── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    if not query.strip():
        st.warning("Please enter your learning goal first.")
        st.stop()

    pipeline = load_pipeline()

    st.divider()

    # Stream output into a placeholder
    with st.spinner("Thinking..."):
        result = pipeline.retriever.retrieve(query, top_k=5)
        context = result.as_context_string()

    # Detect or use manual level
        if auto_detect:
            from pipeline.generator import detect_level
            import os
            from groq import Groq
            _client = Groq(api_key=os.getenv("OPENAI_API_KEY"))
            level = detect_level(query, _client)
            st.info(f"🤖 Detected level: **{level}**")
        else:
            level = manual_level
            st.info(f"📌 Selected level: **{level}**")

    roadmap_placeholder = st.empty()
    full_text = ""

    with st.spinner(""):
        from pipeline.generator import build_user_prompt, SYSTEM_PROMPT
        import os
        from groq import Groq

        client = Groq(api_key=os.getenv("OPENAI_API_KEY"))
        user_prompt = build_user_prompt(query, context, level)

        stream = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=int(os.getenv("MAX_TOKENS", 2000)),
            temperature=0.4,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_text += delta
            roadmap_placeholder.markdown(full_text + "▌")

        roadmap_placeholder.markdown(full_text)

    # ── Actions ───────────────────────────────────────────────────────────────
    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.download_button(
            label="⬇️ Download Roadmap",
            data=full_text,
            file_name="my_roadmap.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_b:
        if st.button("🔄 Generate Another", use_container_width=True):
            st.rerun()