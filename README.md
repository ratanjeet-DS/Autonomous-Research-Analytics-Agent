# Trading Intelligence Multi-Agent Platform

A professional multi-agent trading research system. CrewAI agents crawl TradingQnA and public financial sources, store everything in a local vector database, and generate dashboard-ready research reports — using only free, open-source components.

## Stack

| Layer | Tool | Notes |
|---|---|---|
| Orchestration | CrewAI | 4 specialist agents + supervisor |
| LLM | Ollama (Llama 3.1 / Qwen / Mistral / DeepSeek…) | runs locally, no API key |
| Crawling | Discourse JSON API + requests/BS4 | TradingQnA runs on Discourse, so its public `/search.json`, `/latest.json`, `/t/{id}.json` endpoints are used directly — free and structured. Optional self-hosted Firecrawl supported for other pages. |
| Vector DB | ChromaDB (persistent) + sentence-transformers | local embeddings |
| Frontend | Streamlit | theme color changes with detected sentiment |

## Agents

1. **TradingQnA Query Resolution Specialist** — answers trading questions from community/expert/Zerodha-staff discussions, with thread URLs.
2. **TradingQnA Market Monitor** — trending topics, F&O/platform/regulatory updates, community sentiment (Bullish/Neutral/Bearish).
3. **Equity Research Analyst** — fundamentals, margins, cash flow, debt, valuation table, recommendation.
4. **IPO Research Specialist** — business model, unit economics, use of proceeds, TAM, risks, verdict.
5. **Supervisor (Manager Agent)** — routes requests, deduplicates, ranks by relevance, enforces citations and final markdown structure.

## Setup

```bash
# 1. Install Ollama and pull a model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1          # or qwen2.5 / mistral / deepseek-r1

# 2. Python environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env          # defaults work out of the box

# 4. Run
streamlit run app.py
```

## How it works (RAG workflow)

1. Tools crawl TradingQnA (Discourse JSON) and public pages (filings, IPO docs, news).
2. Documents are cleaned, chunked (~1000 chars, 150 overlap), and **upserted into ChromaDB** with content-hash IDs (idempotent re-crawls).
3. Agents always query the **Knowledge Base tool first** to retrieve historical context, then crawl fresh data.
4. Specialist output passes through the **supervisor** for deduplication, ranking, and citation enforcement.
5. Streamlit parses the report's sentiment (`Bullish/Bearish/Neutral`) and re-themes the dashboard: green `#16a34a` / red `#dc2626` / amber `#f59e0b`.

## Project layout

```
trading-intel/
├── app.py                       # Streamlit dashboard (dynamic theming)
├── requirements.txt
├── .env.example
├── config/settings.py           # all knobs in one place
└── src/
    ├── crawler.py               # TradingQnA Discourse client + generic fetcher
    ├── vectorstore.py           # ChromaDB ingest/retrieve
    ├── tools/research_tools.py  # CrewAI tools (crawl + auto-ingest + KB search)
    └── agents/
        ├── prompts.py           # report templates from the spec
        └── crew.py              # agents, tasks, routing, sentiment extraction
```

## Using it programmatically

```python
from src.agents.crew import run_query, run_equity, run_ipo, run_monitor

print(run_query("How does physical settlement work for ITM options?"))
print(run_equity("TATAMOTORS"))
print(run_ipo("Swiggy"))
print(run_monitor("F&O margin rules"))
```

## Notes & responsible use

- Crawl politely: limits are configurable in `.env` (`MAX_THREADS_PER_QUERY`, `MAX_POSTS_PER_THREAD`); respect TradingQnA's terms of service.
- Open-source LLMs can still make numerical mistakes — prompts force `"Data Not Available"` for unverified figures, but **verify financial numbers against primary sources** before acting.
- All output is research/education, **not investment advice**.

## Common tweaks

- **Different model:** set `LLM_MODEL=ollama/qwen2.5` in `.env`.
- **Better embeddings:** `EMBEDDING_MODEL=BAAI/bge-small-en-v1.5`.
- **Self-hosted Firecrawl:** run the [open-source Firecrawl](https://github.com/mendableai/firecrawl) locally and set `FIRECRAWL_API_URL=http://localhost:3002`.
- **Faster runs:** lower `max_iter` in `src/agents/crew.py` or use a smaller model (`ollama/llama3.2:3b`).
