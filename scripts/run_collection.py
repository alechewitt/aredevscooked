#!/usr/bin/env python3
"""Main orchestration script for data collection and processing."""

import json
from datetime import date, datetime, timedelta, timezone
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

from aredevscooked.collectors.gemini_collector import GeminiCollector
from aredevscooked.processors.stock_processor import StockProcessor
from aredevscooked.processors.headcount_processor import HeadcountProcessor
from aredevscooked.processors.jobs_processor import JobsProcessor
from aredevscooked.utils.config import IT_CONSULTANCIES, BIG_TECH_COMPANIES, AI_LABS


def collect_all_stock_data(
    collector: GeminiCollector, one_year_ago: date
) -> dict[str, dict[str, Any]]:
    """Collect stock price data for all IT consultancies.

    Args:
        collector: GeminiCollector instance
        one_year_ago: Date from exactly 1 year ago

    Returns:
        Dictionary mapping company name to stock data
    """
    stock_data = {}

    for company_info in IT_CONSULTANCIES:
        company_name = company_info["name"]
        ticker = company_info["ticker"]

        try:
            print(f"  Collecting stock data for {company_name} ({ticker})...")
            data = collector.collect_stock_data(company_name, ticker, one_year_ago)
            stock_data[company_name] = data
            print(f"    ✓ Current: ${data['current_price']:.2f}")
        except Exception as e:
            print(f"    ✗ Error collecting {company_name}: {e}")
            continue

    return stock_data


def collect_all_headcount_data(
    collector: GeminiCollector,
) -> dict[str, dict[str, Any]]:
    """Collect headcount data for all companies (IT consultancies + Big Tech).

    Args:
        collector: GeminiCollector instance

    Returns:
        Dictionary mapping company name to headcount data
    """
    headcount_data = {}

    # Combine IT consultancies and big tech
    all_companies = [c["name"] for c in IT_CONSULTANCIES] + [
        c["name"] for c in BIG_TECH_COMPANIES
    ]

    for company_name in all_companies:
        try:
            print(f"  Collecting headcount for {company_name}...")
            data = collector.collect_headcount(company_name)
            headcount_data[company_name] = data
            print(f"    ✓ Headcount: {data['current_headcount']:,}")
        except Exception as e:
            print(f"    ✗ Error collecting {company_name}: {e}")
            continue

    return headcount_data


def collect_all_job_posting_data(
    collector: GeminiCollector,
) -> dict[str, dict[str, Any]]:
    """Collect job posting data for all AI labs.

    Args:
        collector: GeminiCollector instance

    Returns:
        Dictionary mapping company name to job posting data
    """
    job_posting_data = {}

    for lab_info in AI_LABS:
        company_name = lab_info["name"]
        greenhouse_board = lab_info["greenhouse_board"]

        try:
            print(f"  Collecting job postings for {company_name}...")
            data = collector.collect_job_postings(company_name, greenhouse_board)
            job_posting_data[company_name] = data
            print(f"    ✓ Technical jobs: {data['total_technical_jobs']}")
        except Exception as e:
            print(f"    ✗ Error collecting {company_name}: {e}")
            continue

    return job_posting_data


def build_metrics_structure(
    stock_data: dict[str, dict[str, Any]],
    headcount_data: dict[str, dict[str, Any]],
    job_posting_data: dict[str, dict[str, Any]],
    ai_summary: str,
) -> dict[str, Any]:
    """Build the complete metrics_latest.json structure.

    Args:
        stock_data: Stock price data for IT consultancies
        headcount_data: Headcount data for all companies
        job_posting_data: Job posting data for AI labs
        ai_summary: AI-generated market summary

    Returns:
        Complete metrics structure ready for JSON serialization
    """
    # Initialize processors
    stock_processor = StockProcessor()
    headcount_processor = HeadcountProcessor()
    jobs_processor = JobsProcessor()

    # Build metadata
    metadata = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "collection_status": "success",
    }

    # Build low-end tier (IT consultancies)
    low_end_companies = [c["name"] for c in IT_CONSULTANCIES]
    low_end_headcount_data = {
        name: headcount_data[name]
        for name in low_end_companies
        if name in headcount_data
    }

    # Calculate stock index (placeholder - will need baseline data)
    # For now, just structure the data
    stock_index_structure = {
        "current_value": 100.0,  # Placeholder
        "baseline_date": (date.today() - timedelta(days=365)).isoformat(),
        "changes": {"1_day": 0.0, "30_day": 0.0, "1_year": 0.0},
        "companies": {},
    }

    low_end = {
        "headcount": {
            "companies": {},
            "aggregate_badge": "neutral",  # Placeholder
        },
        "stock_index": stock_index_structure,
    }

    # Build medium-end tier (Big Tech)
    medium_end_companies = [c["name"] for c in BIG_TECH_COMPANIES]
    medium_end_headcount_data = {
        name: headcount_data[name]
        for name in medium_end_companies
        if name in headcount_data
    }

    medium_end = {
        "headcount": {
            "companies": {},
            "aggregate_badge": "neutral",  # Placeholder
        }
    }

    # Build high-end tier (AI labs)
    high_end_companies = [c["name"] for c in AI_LABS]
    high_end_job_data = {
        name: job_posting_data[name]
        for name in high_end_companies
        if name in job_posting_data
    }

    high_end = {
        "job_postings": {
            "companies": {},
            "aggregate_badge": "neutral",  # Placeholder
        }
    }

    return {
        "metadata": metadata,
        "low_end": low_end,
        "medium_end": medium_end,
        "high_end": high_end,
        "ai_summary": ai_summary,
    }


def main():
    """Main entry point for data collection."""
    # Load environment variables
    load_dotenv()

    print("🚀 Starting aredevscooked data collection...")
    print("=" * 60)

    # Initialize collector
    try:
        collector = GeminiCollector()
        print("✓ GeminiCollector initialized\n")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Make sure GEMINI_API_KEY is set in .env file")
        return 1

    # Calculate dates
    one_year_ago = date.today() - timedelta(days=365)

    # Collect all data
    print("\n📊 Collecting stock price data...")
    stock_data = collect_all_stock_data(collector, one_year_ago)
    print(f"  Collected {len(stock_data)}/7 companies")

    print("\n👥 Collecting headcount data...")
    headcount_data = collect_all_headcount_data(collector)
    print(f"  Collected {len(headcount_data)}/12 companies")

    print("\n🎯 Collecting job posting data...")
    job_posting_data = collect_all_job_posting_data(collector)
    print(f"  Collected {len(job_posting_data)}/3 companies")

    print("\n📝 Generating AI summary...")
    # For now, use placeholder summary (will implement after we have data)
    ai_summary = "Market data collection in progress..."

    # Build metrics structure
    print("\n🏗️  Building metrics structure...")
    metrics = build_metrics_structure(
        stock_data, headcount_data, job_posting_data, ai_summary
    )

    # Write to file
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "metrics_latest.json"

    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✅ Metrics written to {output_file}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
