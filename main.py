"""CLI entry point.

Examples:
    python main.py --files data/uploads/sales.xlsx --query "Analyze performance"
    python main.py --urls https://example.com --files report.pdf --model llama3
    python main.py --ask "What were the key risks?"          # RAG follow-up
"""
from __future__ import annotations

import argparse
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def cli() -> None:
    p = argparse.ArgumentParser(description="Autonomous Research & Analytics Agent")
    p.add_argument("--files", nargs="*", default=[], help="Paths to xlsx/csv/pdf/docx/txt files")
    p.add_argument("--urls", nargs="*", default=[], help="URLs to research")
    p.add_argument("--query", default="", help="Business question / objective")
    p.add_argument("--model", default=None, help="Ollama model (llama3|qwen3|mistral|deepseek-r1)")
    p.add_argument("--no-rag", action="store_true", help="Disable ChromaDB memory")
    p.add_argument("--ask", default=None, help="Ask a RAG follow-up question and exit")
    args = p.parse_args()

    if args.ask:
        from src.rag.store import KnowledgeBase

        res = KnowledgeBase().ask(args.ask, model=args.model)
        print(res["answer"])
        return

    if not args.files and not args.urls:
        p.error("Provide --files and/or --urls (or --ask for a follow-up question).")

    from src.workflow.graph import run_pipeline

    result = run_pipeline(args.files, args.urls, args.query, args.model, not args.no_rag)
    print("\n=== EXECUTIVE SUMMARY ===\n", result.get("executive_summary", ""))
    print("\n=== CONFIDENCE ===", result.get("confidence_score"))
    print("\n=== REPORTS ===")
    print(json.dumps(result.get("report_paths", {}), indent=2))
    if result.get("errors"):
        print("\n=== WARNINGS ===")
        for e in result["errors"]:
            print(" -", e)


if __name__ == "__main__":
    cli()
