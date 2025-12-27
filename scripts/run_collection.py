#!/usr/bin/env python3
"""Main orchestration script for data collection and processing."""

import asyncio
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


async def collect_single_stock_data(
    collector: GeminiCollector,
    company_name: str,
    ticker: str,
    one_year_ago: date,
) -> tuple[str, dict[str, Any] | None]:
    """Collect stock data for a single company (async wrapper).

    Args:
        collector: GeminiCollector instance
        company_name: Company name
        ticker: Stock ticker symbol
        one_year_ago: Date from exactly 1 year ago

    Returns:
        Tuple of (company_name, data) or (company_name, None) on error
    """
    try:
        print(f"  Collecting stock data for {company_name} ({ticker})...")
        # Run blocking I/O in thread pool
        data = await asyncio.to_thread(
            collector.collect_stock_data, company_name, ticker, one_year_ago
        )
        print(f"    ✓ Current: ${data['current_price']:.2f}")
        return company_name, data
    except Exception as e:
        print(f"    ✗ Error collecting {company_name}: {e}")
        return company_name, None


async def collect_all_stock_data(
    collector: GeminiCollector, one_year_ago: date
) -> dict[str, dict[str, Any]]:
    """Collect stock price data for all IT consultancies concurrently.

    Args:
        collector: GeminiCollector instance
        one_year_ago: Date from exactly 1 year ago

    Returns:
        Dictionary mapping company name to stock data
    """
    tasks = [
        collect_single_stock_data(
            collector, company_info["name"], company_info["ticker"], one_year_ago
        )
        for company_info in IT_CONSULTANCIES
    ]

    results = await asyncio.gather(*tasks)

    # Filter out failed collections (None values)
    stock_data = {name: data for name, data in results if data is not None}
    return stock_data


async def collect_single_headcount_data(
    collector: GeminiCollector, company_name: str
) -> tuple[str, dict[str, Any] | None]:
    """Collect headcount data for a single company (async wrapper).

    Args:
        collector: GeminiCollector instance
        company_name: Company name

    Returns:
        Tuple of (company_name, data) or (company_name, None) on error
    """
    try:
        print(f"  Collecting headcount for {company_name}...")
        # Run blocking I/O in thread pool
        data = await asyncio.to_thread(collector.collect_headcount, company_name)
        print(f"    ✓ Headcount: {data['current_headcount']:,}")
        return company_name, data
    except Exception as e:
        print(f"    ✗ Error collecting {company_name}: {e}")
        return company_name, None


async def collect_all_headcount_data(
    collector: GeminiCollector,
) -> dict[str, dict[str, Any]]:
    """Collect headcount data for all companies (IT consultancies + Big Tech) concurrently.

    Args:
        collector: GeminiCollector instance

    Returns:
        Dictionary mapping company name to headcount data
    """
    # Combine IT consultancies and big tech
    all_companies = [c["name"] for c in IT_CONSULTANCIES] + [
        c["name"] for c in BIG_TECH_COMPANIES
    ]

    tasks = [
        collect_single_headcount_data(collector, company_name)
        for company_name in all_companies
    ]

    results = await asyncio.gather(*tasks)

    # Filter out failed collections (None values)
    headcount_data = {name: data for name, data in results if data is not None}
    return headcount_data


async def collect_single_job_posting_data(
    collector: GeminiCollector, company_name: str, greenhouse_board: str
) -> tuple[str, dict[str, Any] | None]:
    """Collect job posting data for a single company (async wrapper).

    Args:
        collector: GeminiCollector instance
        company_name: Company name
        greenhouse_board: Greenhouse board name

    Returns:
        Tuple of (company_name, data) or (company_name, None) on error
    """
    try:
        print(f"  Collecting job postings for {company_name}...")
        # Run blocking I/O in thread pool
        data = await asyncio.to_thread(
            collector.collect_job_postings, company_name, greenhouse_board
        )
        print(f"    ✓ Technical jobs: {data['total_technical_jobs']}")
        return company_name, data
    except Exception as e:
        print(f"    ✗ Error collecting {company_name}: {e}")
        return company_name, None


async def collect_all_job_posting_data(
    collector: GeminiCollector,
) -> dict[str, dict[str, Any]]:
    """Collect job posting data for all AI labs concurrently.

    Args:
        collector: GeminiCollector instance

    Returns:
        Dictionary mapping company name to job posting data
    """
    tasks = [
        collect_single_job_posting_data(
            collector, lab_info["name"], lab_info["greenhouse_board"]
        )
        for lab_info in AI_LABS
    ]

    results = await asyncio.gather(*tasks)

    # Filter out failed collections (None values)
    job_posting_data = {name: data for name, data in results if data is not None}
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

    # Populate headcount data for IT consultancies
    low_end_headcount_companies = {}
    for name in low_end_companies:
        if name in headcount_data:
            low_end_headcount_companies[name] = {
                "current": headcount_data[name]["current_headcount"],
                "data_date": headcount_data[name].get("data_date", ""),
                # Historical changes will be populated when we have baseline data
                "changes": {},
            }

    # Populate stock index data
    stock_index_companies = {}
    for company_info in IT_CONSULTANCIES:
        name = company_info["name"]
        ticker = company_info["ticker"]
        if name in stock_data:
            stock_index_companies[name] = {
                "ticker": ticker,
                "current_price": stock_data[name]["current_price"],
                "weight": 1.0 / len(IT_CONSULTANCIES),  # Equal weights
            }

    stock_index_structure = {
        "current_value": 100.0,  # Placeholder - will calculate when we have baselines
        "baseline_date": (date.today() - timedelta(days=365)).isoformat(),
        "changes": {"1_day": 0.0, "30_day": 0.0, "1_year": 0.0},
        "companies": stock_index_companies,
    }

    low_end = {
        "headcount": {
            "companies": low_end_headcount_companies,
            "aggregate_badge": "neutral",  # Placeholder until we have historical data
        },
        "stock_index": stock_index_structure,
    }

    # Build medium-end tier (Big Tech)
    medium_end_companies = [c["name"] for c in BIG_TECH_COMPANIES]

    # Populate headcount data for Big Tech
    medium_end_headcount_companies = {}
    for name in medium_end_companies:
        if name in headcount_data:
            medium_end_headcount_companies[name] = {
                "current": headcount_data[name]["current_headcount"],
                "data_date": headcount_data[name].get("data_date", ""),
                # Historical changes will be populated when we have baseline data
                "changes": {},
            }

    medium_end = {
        "headcount": {
            "companies": medium_end_headcount_companies,
            "aggregate_badge": "neutral",  # Placeholder until we have historical data
        }
    }

    # Build high-end tier (AI labs)
    high_end_companies = [c["name"] for c in AI_LABS]

    # Populate job posting data for AI labs
    high_end_job_companies = {}
    for name in high_end_companies:
        if name in job_posting_data:
            high_end_job_companies[name] = {
                "current": job_posting_data[name]["total_technical_jobs"],
                "collection_date": job_posting_data[name].get("collection_date", ""),
                # Historical changes will be populated when we have baseline data
                "changes": {},
            }

    high_end = {
        "job_postings": {
            "companies": high_end_job_companies,
            "aggregate_badge": "neutral",  # Placeholder until we have historical data
        }
    }

    return {
        "metadata": metadata,
        "low_end": low_end,
        "medium_end": medium_end,
        "high_end": high_end,
        "ai_summary": ai_summary,
    }


async def main_async():
    """Main async entry point for data collection."""
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

    # Collect all data concurrently
    print("\n📊 Collecting stock price data...")
    stock_data = await collect_all_stock_data(collector, one_year_ago)
    print(f"  Collected {len(stock_data)}/7 companies")

    print("\n👥 Collecting headcount data...")
    headcount_data = await collect_all_headcount_data(collector)
    print(f"  Collected {len(headcount_data)}/12 companies")

    print("\n🎯 Collecting job posting data...")
    job_posting_data = await collect_all_job_posting_data(collector)
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


def main():
    """Synchronous entry point that runs async main."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    exit(main())
