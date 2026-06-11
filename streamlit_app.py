"""Streamlit UI for the Autonomous Research & Analytics Agent."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from config.settings import settings
from src.rag.store import KnowledgeBase
from src.workflow.graph import run_pipeline

st.set_page_config(page_title="Research & Analytics Agent", page_icon="📊", layout="wide")
st.title("📊 Autonomous Research & Analytics Agent")
st.caption("CrewAI · LangGraph · Ollama · Firecrawl · Crawl4AI · ChromaDB")

# ------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox("Ollama model", settings.supported_models,
                         index=settings.supported_models.index(settings.default_model)
                         if settings.default_model in settings.supported_models else 0)
    use_rag = st.toggle("Enable RAG memory (ChromaDB)", value=True)
    st.divider()
    st.markdown(f"**Ollama:** `{settings.ollama_base_url}`")
    st.markdown("**Firecrawl:** " + ("✅ key set" if settings.firecrawl_api_key else "➖ using Crawl4AI"))

tab_run, tab_chat = st.tabs(["🚀 Run Analysis", "💬 Ask the Knowledge Base"])

# ------------------------------------------------------------ run tab
with tab_run:
    col1, col2 = st.columns(2)
    with col1:
        files = st.file_uploader("Upload files (Excel / CSV / PDF / DOCX / TXT)",
                                 type=["xlsx", "xlsm", "xls", "csv", "tsv", "pdf", "docx", "txt", "md"],
                                 accept_multiple_files=True)
    with col2:
        urls_text = st.text_area("Website URLs (one per line)", placeholder="https://example.com/industry-report")
    query = st.text_input("What do you want to know?",
                          placeholder="e.g. Analyze this Excel file and compare with industry trends")

    if st.button("Run multi-agent analysis", type="primary"):
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for f in files or []:
            p = upload_dir / f.name
            p.write_bytes(f.getbuffer())
            paths.append(str(p))
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

        if not paths and not urls:
            st.warning("Upload at least one file or provide a URL.")
        else:
            with st.status("Running 9-agent pipeline…", expanded=True) as status:
                st.write("Intake → Extraction → Quality → Research → Analyst → Scientist → Viz → Insight → Report")
                result = run_pipeline(paths, urls, query, model, use_rag)
                status.update(label="Pipeline complete ✅", state="complete")
            st.session_state["result"] = result

    result = st.session_state.get("result")
    if result:
        st.metric("Confidence score", f"{result.get('confidence_score', 'n/a')} / 100")
        q = result.get("quality_report", {})
        st.metric("Data quality", f"{q.get('quality_score', 'n/a')} / 100")

        st.subheader("Executive Summary")
        st.markdown(result.get("executive_summary", "_n/a_"))

        ins = result.get("insights", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🔎 Findings")
            for f in ins.get("findings", []):
                st.markdown(f"- {f}")
        with c2:
            st.subheader("⚠️ Risks")
            for r in ins.get("risks", []):
                st.markdown(f"- {r}")
        with c3:
            st.subheader("💡 Opportunities")
            for k, items in ins.get("opportunities", {}).items():
                for o in items:
                    st.markdown(f"- **{k}**: {o}")

        st.subheader("✅ Recommendations")
        rec = ins.get("recommendations", {})
        st.markdown("**Short-term**")
        for r in rec.get("short_term", []):
            st.markdown(f"- {r}")
        st.markdown("**Long-term**")
        for r in rec.get("long_term", []):
            st.markdown(f"- {r}")

        st.subheader("📈 Charts")
        for c in result.get("charts", []):
            st.image(c["png"], caption=f"{c['title']} — {c['insight']}")

        if result.get("research_findings", {}).get("synthesis"):
            with st.expander("🌐 Web research synthesis"):
                st.markdown(result["research_findings"]["synthesis"])

        st.subheader("⬇️ Downloadable report")
        for fmt, path in (result.get("report_paths") or {}).items():
            p = Path(path)
            if p.exists():
                st.download_button(f"Download {fmt.upper()}", p.read_bytes(), file_name=p.name)

        if result.get("errors"):
            with st.expander("⚠️ Pipeline warnings"):
                for e in result["errors"]:
                    st.markdown(f"- {e}")

# ------------------------------------------------------------ chat tab
with tab_chat:
    st.markdown("Ask follow-up questions about uploaded reports and crawled web content (RAG over ChromaDB).")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for role, msg in st.session_state.chat:
        st.chat_message(role).markdown(msg)
    if q := st.chat_input("e.g. What were the main risks in the uploaded report?"):
        st.session_state.chat.append(("user", q))
        st.chat_message("user").markdown(q)
        try:
            kb = KnowledgeBase()
            res = kb.ask(q, model=model)
            answer = res["answer"] + "\n\n---\n*Sources:* " + ", ".join(
                sorted({h["source"] for h in res["sources"] if h.get("source")}) or ["none"])
        except Exception as exc:  # noqa: BLE001
            answer = f"Knowledge base unavailable: {exc}"
        st.session_state.chat.append(("assistant", answer))
        st.chat_message("assistant").markdown(answer)
