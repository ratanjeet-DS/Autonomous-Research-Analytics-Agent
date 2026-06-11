# Autonomous Research & Analytics Agent

A production-ready, multi-agent research and business-intelligence platform that ingests Excel, CSV, PDF, DOCX, TXT files and websites, then automatically extracts, cleans, analyzes, researches, visualizes and reports — orchestrated by **LangGraph**, reasoned over by **CrewAI** agents, powered by **local Ollama LLMs**.

## Architecture

LangGraph workflow with conditional routing across nine CrewAI-backed agents. Deterministic work (parsing, statistics, ML, charting) runs in plain Python for reliability; LLM agents reason over the computed results.

    User Input
        ↓
    1. Intake Agent          — type detection, validation, routing plan
        ↓
    2. Data Extraction Agent — Excel (sheets/formulas), PDF/DOCX (text/tables), URLs (Firecrawl → Crawl4AI → httpx fallback)
        ↓
    3. Data Quality Agent    — missing values, duplicates, IQR anomalies, format checks, quality score
        ↓  (conditional: URL/mixed input → research; tabular/document-only → skip ahead)
    4. Research Agent        — industry context, benchmarks, competitors, trends; feeds ChromaDB
        ↓
    5. Business Analyst      — KPIs (growth/decline/variance), trends, seasonality, root-cause drivers
        ↓
    6. Data Scientist        — correlation, hypothesis tests (t-test/ANOVA), OLS regression, AutoML
                               (RandomForest/XGBoost/LogReg · LinReg/RF/XGB regressors · KMeans/DBSCAN · ARIMA/Prophet)
        ↓
    7. Visualization Agent   — auto bar/line/pie/scatter/heatmap/distribution/forecast charts → PNG, SVG, HTML
        ↓
    8. Insight Agent         — findings, hidden patterns, risks, revenue/cost/efficiency opportunities,
                               short- & long-term recommendations, confidence score
        ↓
    9. Report Generator      — Jinja2 → Markdown, HTML, PDF (ReportLab), DOCX
        ↓
    Final Output (Streamlit dashboard + downloadable reports)

## Quick start (local)

Requirements: Python 3.12 and a running [Ollama](https://ollama.com) instance.

    # 1. Install
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    crawl4ai-setup                      # installs the headless browser for Crawl4AI

    # 2. Configure
    cp .env.example .env                # set FIRECRAWL_API_KEY if you have one (optional)

    # 3. Pull models
    ollama pull qwen3 && ollama pull llama3   # plus mistral / deepseek-r1 if desired

    # 4. Run the UI
    streamlit run app/streamlit_app.py

    # …or the CLI
    python main.py --files data/uploads/sales.xlsx --query "Analyze business performance"
    python main.py --urls https://example.com/market-report --files report.pdf --model llama3
    python main.py --ask "What were the key risks in the uploaded report?"   # RAG follow-up

## Quick start (Docker)

    docker compose up -d --build
    ./scripts/pull_models.sh            # pull Ollama models into the container
    open http://localhost:8501

## Supported user queries

- "Analyze this Excel file."
- "Compare uploaded report with industry trends."  (upload + URLs → mixed routing)
- "Generate executive summary." / "Identify business risks."
- "Forecast next quarter performance."  (auto ARIMA/Prophet)
- "Create presentation-ready charts." / "Compare competitors."
- "Recommend strategic actions." / "Explain findings in simple language."  (RAG chat tab)

## Output of every run

Executive summary · key metrics · charts (PNG/SVG/HTML) · research findings · statistical findings · ML insights · risks · opportunities · recommendations · confidence score · downloadable report (MD/HTML/PDF/DOCX).

## Configuration

All settings live in `.env` (see `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local LLM endpoint |
| `DEFAULT_MODEL` | `qwen3` | Any of llama3 / qwen3 / mistral / deepseek-r1 (switchable in the UI) |
| `FIRECRAWL_API_KEY` | _empty_ | Enables hosted Firecrawl; otherwise Crawl4AI/httpx are used |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | RAG vector store |
| `UPLOAD_DIR` / `OUTPUT_DIR` | `./data/...` | File locations |

## Project layout

    config/settings.py        # pydantic-settings configuration
    src/llm/ollama_client.py  # model factory + fallback
    src/agents/               # CrewAI agents (intake/research/analyst/scientist/insight/report)
    src/workflow/             # LangGraph state + graph with conditional routing
    src/ingestion/            # file loaders + Firecrawl/Crawl4AI web scraping
    src/quality/              # data-quality scoring + auto-cleaning
    src/analytics/            # KPIs, statistics, AutoML, forecasting
    src/viz/                  # auto-chart engine (matplotlib/seaborn/plotly)
    src/rag/                  # ChromaDB chunking, semantic search, RAG Q&A
    src/insights/             # insight + confidence-score generation
    src/reporting/            # Jinja2 → MD/HTML/PDF/DOCX
    app/streamlit_app.py      # dashboard UI with RAG chat
    main.py                   # CLI
    tests/                    # pytest smoke tests (no LLM needed)

## Testing

    pip install pytest
    pytest tests/ -v          # deterministic components run without Ollama

## Notes & graceful degradation

- If Ollama is unreachable, deterministic analytics, charts and reports still complete; LLM-written sections are marked unavailable.
- Web scraping cascades: Firecrawl (if keyed) → Crawl4AI → plain httpx+BeautifulSoup.
- PDF export uses ReportLab (pure Python); swap in WeasyPrint if you prefer CSS-driven PDFs and have its system deps.
