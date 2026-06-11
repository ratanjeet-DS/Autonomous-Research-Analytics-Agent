"""Trading Intelligence Dashboard (Streamlit).

Run:  streamlit run app.py
Theme color adapts to detected market sentiment:
  bullish → green (#16a34a), bearish → red (#dc2626), neutral → amber (#f59e0b)
"""
import streamlit as st

from config.settings import THEME_COLORS
from src.agents.crew import extract_sentiment, route

st.set_page_config(page_title="Trading Intelligence", page_icon="📈", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────────
if "report" not in st.session_state:
    st.session_state.report = ""
if "sentiment" not in st.session_state:
    st.session_state.sentiment = "neutral"
if "history" not in st.session_state:
    st.session_state.history = []

color = THEME_COLORS[st.session_state.sentiment]

# ── Dynamic theme injection ───────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
      .ti-header {{
        background: {color};
        color: white;
        padding: 1.1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
      }}
      .ti-header h1 {{ margin: 0; font-size: 1.6rem; color: white; }}
      .ti-badge {{
        display: inline-block; background: white; color: {color};
        font-weight: 700; padding: 0.2rem 0.8rem; border-radius: 999px;
        text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;
      }}
      .ti-status {{
        border-left: 5px solid {color}; padding: 0.5rem 1rem;
        background: {color}15; border-radius: 6px; margin-bottom: 0.75rem;
      }}
      div.stButton > button {{ background: {color}; color: white; border: none; }}
      div.stButton > button:hover {{ filter: brightness(0.9); color: white; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="ti-header">
          <h1>📈 Trading Intelligence Platform</h1>
          <span class="ti-badge">Sentiment: {st.session_state.sentiment}</span>
        </div>""",
    unsafe_allow_html=True,
)

# ── Sidebar: mode routing ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("Research Mode")
    mode_label = st.radio(
        "Choose an agent",
        ["TradingQnA Q&A", "Market Monitor", "Equity Research", "IPO Research"],
    )
    mode_map = {
        "TradingQnA Q&A": ("query", "Your trading question",
                           "e.g. How does physical settlement work for ITM options?"),
        "Market Monitor": ("monitor", "Topic to monitor (optional)", "e.g. F&O margin rules"),
        "Equity Research": ("equity", "Ticker / company", "e.g. TATAMOTORS"),
        "IPO Research": ("ipo", "IPO company name", "e.g. Swiggy"),
    }
    mode, label, placeholder = mode_map[mode_label]
    st.divider()
    st.caption("Powered by CrewAI + Ollama + ChromaDB. "
               "All output is research, not investment advice.")

# ── Input + run ───────────────────────────────────────────────────────────────
user_input = st.text_input(label, placeholder=placeholder)
run = st.button("Run Research", type="primary", use_container_width=True)

if run:
    if not user_input and mode != "monitor":
        st.warning("Please enter an input.")
    else:
        with st.status("Agents working — crawling, retrieving, analyzing…", expanded=False):
            try:
                report = route(mode, user_input or "Indian markets")
                st.session_state.report = report
                st.session_state.sentiment = extract_sentiment(report)
                st.session_state.history.append((mode_label, user_input, report))
            except Exception as e:
                st.session_state.report = f"**Error:** {e}"
        st.rerun()  # re-render so the theme reflects the new sentiment

# ── Output ────────────────────────────────────────────────────────────────────
if st.session_state.report:
    st.markdown(
        f'<div class="ti-status"><b>Latest report</b> — sentiment detected: '
        f'{st.session_state.sentiment.title()}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(st.session_state.report)
    st.download_button("Download report (.md)", st.session_state.report,
                       file_name="research_report.md", mime="text/markdown")

if st.session_state.history:
    with st.expander(f"Session history ({len(st.session_state.history)})"):
        for i, (m, q, _) in enumerate(reversed(st.session_state.history), 1):
            st.write(f"{i}. **{m}** — {q or '(latest feed)'}")
