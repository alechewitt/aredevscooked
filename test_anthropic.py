#!/usr/bin/env python3
"""Quick test to collect Anthropic job postings."""

from dotenv import load_dotenv
from aredevscooked.collectors.gemini_collector import GeminiCollector

load_dotenv()

collector = GeminiCollector()

print("Collecting Anthropic job postings...")
try:
    data = collector.collect_job_postings("Anthropic", "anthropic")
    print(f"Success! Total technical jobs: {data['total_technical_jobs']}")
    print(f"Job titles: {data['job_titles'][:5]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
