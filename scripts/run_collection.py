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
from aredevscooked.generators.badge_generator import BadgeGenerator
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


def load_baselines() -> dict[str, Any] | None:
    """Load baseline data from baselines.json.

    Returns:
        Baseline data dict or None if file doesn't exist
    """
    baselines_file = Path("data/processed/baselines.json")
    if not baselines_file.exists():
        print("  ⚠️  No baselines.json found, skipping change calculations")
        return None

    with open(baselines_file, "r") as f:
        return json.load(f)


def calculate_headcount_changes(
    current: int,
    company_name: str,
    baselines_data: dict[str, Any],
    headcount_processor: HeadcountProcessor,
) -> dict[str, dict[str, Any]]:
    """Calculate headcount changes against all baselines.

    Args:
        current: Current headcount
        company_name: Company name
        baselines_data: Baseline data structure
        headcount_processor: HeadcountProcessor instance

    Returns:
        Dictionary of changes for each baseline period
    """
    changes = {}

    for baseline_name in ["1_day_ago", "30_days_ago", "1_year_ago", "q1_2023"]:
        baseline = baselines_data["baselines"].get(baseline_name, {})
        headcounts = baseline.get("headcounts", {})

        if company_name in headcounts:
            baseline_value = headcounts[company_name]["headcount"]
            pct_change = headcount_processor.calculate_percentage_change(
                current, baseline_value
            )
            abs_change = headcount_processor.calculate_absolute_change(
                current, baseline_value
            )
            badge = headcount_processor.classify_change(pct_change)

            changes[baseline_name] = {
                "value": abs_change,
                "pct": round(pct_change, 2),
                "badge": badge,
            }

    return changes


def load_history_snapshot(days_ago: int) -> dict[str, Any] | None:
    """Load a snapshot from metrics_history.json.

    Args:
        days_ago: Number of days ago (1, 30, etc.)

    Returns:
        Snapshot data or None if not found
    """
    history_file = Path("data/processed/metrics_history.json")
    if not history_file.exists():
        return None

    target_date = (date.today() - timedelta(days=days_ago)).isoformat()

    with open(history_file, "r") as f:
        history = json.load(f)

    return history.get("snapshots", {}).get(target_date)


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
    badge_generator = BadgeGenerator()

    # Load baselines for change calculations
    baselines_data = load_baselines()
    has_baselines = baselines_data is not None

    # Build metadata
    metadata = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "collection_status": "success",
    }

    # Build low-end tier (IT consultancies)
    low_end_companies = [c["name"] for c in IT_CONSULTANCIES]

    # Populate headcount data for IT consultancies
    low_end_headcount_companies = {}
    low_end_badges = []

    for name in low_end_companies:
        if name in headcount_data:
            current_headcount = headcount_data[name]["current_headcount"]

            # Calculate changes if we have baselines
            if has_baselines:
                changes = calculate_headcount_changes(
                    current_headcount, name, baselines_data, headcount_processor
                )
                # Collect badges for aggregate calculation
                for change_data in changes.values():
                    low_end_badges.append(change_data["badge"])
            else:
                changes = {}

            low_end_headcount_companies[name] = {
                "current": current_headcount,
                "data_date": headcount_data[name].get("data_date", ""),
                "changes": changes,
            }

    # Calculate aggregate badge (worst wins)
    if low_end_badges:
        low_end_aggregate_badge = badge_generator.get_aggregate_badge(low_end_badges)
    else:
        low_end_aggregate_badge = "neutral"

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
            "aggregate_badge": low_end_aggregate_badge,
        },
        "stock_index": stock_index_structure,
    }

    # Build medium-end tier (Big Tech)
    medium_end_companies = [c["name"] for c in BIG_TECH_COMPANIES]

    # Populate headcount data for Big Tech
    medium_end_headcount_companies = {}
    medium_end_badges = []

    for name in medium_end_companies:
        if name in headcount_data:
            current_headcount = headcount_data[name]["current_headcount"]

            # Calculate changes if we have baselines
            if has_baselines:
                changes = calculate_headcount_changes(
                    current_headcount, name, baselines_data, headcount_processor
                )
                # Collect badges for aggregate calculation
                for change_data in changes.values():
                    medium_end_badges.append(change_data["badge"])
            else:
                changes = {}

            medium_end_headcount_companies[name] = {
                "current": current_headcount,
                "data_date": headcount_data[name].get("data_date", ""),
                "changes": changes,
            }

    # Calculate aggregate badge
    if medium_end_badges:
        medium_end_aggregate_badge = badge_generator.get_aggregate_badge(
            medium_end_badges
        )
    else:
        medium_end_aggregate_badge = "neutral"

    medium_end = {
        "headcount": {
            "companies": medium_end_headcount_companies,
            "aggregate_badge": medium_end_aggregate_badge,
        }
    }

    # Build high-end tier (AI labs)
    high_end_companies = [c["name"] for c in AI_LABS]

    # Populate job posting data for AI labs
    # Note: We use history snapshots for job postings since Greenhouse doesn't provide historical data
    high_end_job_companies = {}
    high_end_badges = []

    for name in high_end_companies:
        if name in job_posting_data:
            current_jobs = job_posting_data[name]["total_technical_jobs"]
            changes = {}

            # Try to get historical snapshots from metrics_history.json
            for days_ago, key in [(1, "1_day_ago"), (30, "30_days_ago")]:
                snapshot = load_history_snapshot(days_ago)
                if snapshot and name in snapshot.get("job_postings", {}):
                    historical_jobs = snapshot["job_postings"][name][
                        "total_technical_jobs"
                    ]
                    job_change = current_jobs - historical_jobs
                    badge = jobs_processor.classify_change(job_change)
                    changes[key] = {"value": job_change, "badge": badge}
                    high_end_badges.append(badge)

            high_end_job_companies[name] = {
                "current": current_jobs,
                "collection_date": job_posting_data[name].get("collection_date", ""),
                "changes": changes,
            }

    # Calculate aggregate badge
    if high_end_badges:
        high_end_aggregate_badge = badge_generator.get_aggregate_badge(high_end_badges)
    else:
        high_end_aggregate_badge = "neutral"

    high_end = {
        "job_postings": {
            "companies": high_end_job_companies,
            "aggregate_badge": high_end_aggregate_badge,
        }
    }

    return {
        "metadata": metadata,
        "low_end": low_end,
        "medium_end": medium_end,
        "high_end": high_end,
        "ai_summary": ai_summary,
    }


def save_daily_snapshot(
    stock_data: dict[str, dict[str, Any]],
    headcount_data: dict[str, dict[str, Any]],
    job_posting_data: dict[str, dict[str, Any]],
) -> None:
    """Save today's raw data as a snapshot in metrics_history.json.

    This creates a historical record for future change calculations.

    Args:
        stock_data: Stock price data for IT consultancies
        headcount_data: Headcount data for all companies
        job_posting_data: Job posting data for AI labs
    """
    history_file = Path("data/processed/metrics_history.json")
    today = date.today().isoformat()

    # Load existing history or create new
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = {
            "metadata": {
                "description": "Daily snapshots of market data",
                "first_snapshot": today,
            },
            "snapshots": {},
        }

    # Create today's snapshot
    snapshot = {
        "date": today,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stock_prices": {},
        "headcounts": {},
        "job_postings": {},
    }

    # Save stock prices
    for company_name, data in stock_data.items():
        snapshot["stock_prices"][company_name] = {
            "price": data["current_price"],
            "ticker": data["ticker"],
        }

    # Save headcounts
    for company_name, data in headcount_data.items():
        snapshot["headcounts"][company_name] = {
            "headcount": data["current_headcount"],
            "data_date": data.get("data_date", ""),
        }

    # Save job postings
    for company_name, data in job_posting_data.items():
        snapshot["job_postings"][company_name] = {
            "total_technical_jobs": data["total_technical_jobs"],
            "collection_date": data.get("collection_date", ""),
        }

    # Add to history
    history["snapshots"][today] = snapshot
    history["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Write back
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    print(f"  💾 Daily snapshot saved to {history_file}")


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

    # Save daily snapshot to history
    print("\n💾 Saving daily snapshot...")
    save_daily_snapshot(stock_data, headcount_data, job_posting_data)

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

    # Also copy to website/ directory for GitHub Pages deployment
    website_dir = Path("website")
    website_metrics_file = website_dir / "metrics_latest.json"

    with open(website_metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Metrics copied to {website_metrics_file} (for GitHub Pages)")
    print("=" * 60)

    return 0


def main():
    """Synchronous entry point that runs async main."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    exit(main())
