#!/usr/bin/env python3
"""Quick test script to verify Gemini API integration."""

from aredevscooked.collectors.gemini_collector import GeminiCollector
from datetime import date, timedelta
import json


def main():
    """Test Gemini API with real queries."""
    print("🧪 Testing Gemini API Integration\n")
    print("=" * 60)

    try:
        collector = GeminiCollector()
        print("✓ GeminiCollector initialized successfully\n")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Make sure GEMINI_API_KEY is set in .env file")
        return 1

    # Test 1: Headcount collection
    print("\n📊 Test 1: Collecting headcount for Microsoft...")
    print("-" * 60)
    try:
        result = collector.collect_headcount("Microsoft")
        print(f"✓ Success!")
        print(f"  Company: {result['company']}")
        print(f"  Headcount: {result['current_headcount']:,}")
        print(f"  Date: {result['data_date']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Sources: {result['source_urls']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1

    # Test 2: Stock price collection
    print("\n💰 Test 2: Collecting stock prices for MSFT...")
    print("-" * 60)
    try:
        one_year_ago = date.today() - timedelta(days=365)
        result = collector.collect_stock_data("Microsoft", "MSFT", one_year_ago)
        print(f"✓ Success!")
        print(f"  Company: {result['company']}")
        print(f"  Current Price: ${result['current_price']:.2f}")
        print(f"  Price 1Y Ago: ${result['price_1_year_ago']:.2f}")
        change_pct = (
            (result["current_price"] - result["price_1_year_ago"])
            / result["price_1_year_ago"]
            * 100
        )
        print(f"  1Y Change: {change_pct:+.1f}%")
        print(f"  Sources: {result['source_urls']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1

    # Test 3: Job postings
    print("\n🎯 Test 3: Collecting job postings for Anthropic...")
    print("-" * 60)
    try:
        result = collector.collect_job_postings("Anthropic", "anthropic")
        print(f"✓ Success!")
        print(f"  Company: {result['company']}")
        print(f"  Technical Jobs: {result['total_technical_jobs']}")
        print(f"  Sample Titles: {result['job_titles'][:3]}")
        print(f"  Collection Date: {result['collection_date']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1

    # Test 4: AI Summary
    print("\n📝 Test 4: Generating AI summary...")
    print("-" * 60)
    try:
        sample_metrics = {
            "low_end": {
                "headcount": {"aggregate_badge": "reasonably_weak"},
                "stock_index": {"current_value": 87.5},
            },
            "medium_end": {"headcount": {"aggregate_badge": "neutral"}},
            "high_end": {"job_postings": {"aggregate_badge": "strong"}},
        }
        summary = collector.generate_summary(sample_metrics)
        print(f"✓ Success!")
        print(f"  Summary: {summary}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1

    print("\n" + "=" * 60)
    print("✅ All Gemini API tests passed successfully!")
    print("\nNote: Check the output above to verify the data quality.")
    print("If quota exceeded, wait 24 hours or use a different API key.")
    return 0


if __name__ == "__main__":
    exit(main())
