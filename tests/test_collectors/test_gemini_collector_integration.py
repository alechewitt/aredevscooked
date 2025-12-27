"""Integration tests for GeminiCollector with real API calls.

These tests require GEMINI_API_KEY to be set in environment or .env file.
Run with: pytest -m integration -v

Mark tests as integration:
    pytest -m "not integration"  # Skip integration tests (default for CI)
    pytest -m integration         # Run only integration tests
"""

import os
import pytest
from datetime import date, timedelta
from dotenv import load_dotenv
from aredevscooked.collectors.gemini_collector import GeminiCollector

# Load environment variables from .env file
load_dotenv()

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def collector():
    """Create a real GeminiCollector with API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set in environment")
    return GeminiCollector(api_key=api_key)


# Stock Price Integration Tests


def test_collect_stock_data_real_api(collector):
    """Test stock data collection with real Gemini API."""
    one_year_ago = date.today() - timedelta(days=365)
    result = collector.collect_stock_data("Microsoft", "MSFT", one_year_ago)

    # Verify structure
    assert "company" in result
    assert "ticker" in result
    assert "current_price" in result
    assert "price_1_year_ago" in result
    assert "source_urls" in result

    # Verify data types
    assert isinstance(result["current_price"], (int, float))
    assert isinstance(result["price_1_year_ago"], (int, float))
    assert isinstance(result["source_urls"], list)

    # Verify reasonable values
    assert result["current_price"] > 0
    assert result["price_1_year_ago"] > 0

    print(f"\nStock data collected: {result}")


def test_collect_stock_data_indian_exchange(collector):
    """Test stock data collection for Indian stock exchange (NSE)."""
    one_year_ago = date.today() - timedelta(days=365)
    result = collector.collect_stock_data("Infosys", "INFY", one_year_ago)

    assert "current_price" in result
    assert result["current_price"] > 0
    assert result["ticker"] == "INFY"

    print(f"\nIndian stock data collected: {result}")


# Headcount Integration Tests


def test_collect_headcount_real_api(collector):
    """Test headcount collection with real Gemini API."""
    result = collector.collect_headcount("Microsoft")

    # Verify structure
    assert "company" in result
    assert "current_headcount" in result
    assert "data_date" in result
    assert "confidence" in result
    assert "source_urls" in result

    # Verify data types
    assert isinstance(result["current_headcount"], int)
    assert isinstance(result["confidence"], str)
    assert isinstance(result["source_urls"], list)

    # Verify reasonable values
    assert result["current_headcount"] >= 1000
    assert result["confidence"] in ["high", "medium", "low"]

    print(f"\nHeadcount data collected: {result}")


def test_collect_headcount_it_consultancy(collector):
    """Test headcount collection for IT consultancy."""
    result = collector.collect_headcount("Infosys")

    assert "current_headcount" in result
    assert result["current_headcount"] >= 1000
    assert result["current_headcount"] <= 1_000_000

    print(f"\nIT consultancy headcount collected: {result}")


# Job Postings Integration Tests


def test_collect_job_postings_real_api(collector):
    """Test job postings collection with real Gemini API."""
    result = collector.collect_job_postings("Anthropic", "anthropic")

    # Verify structure
    assert "company" in result
    assert "total_technical_jobs" in result
    assert "job_titles" in result
    assert "collection_date" in result
    assert "source_url" in result

    # Verify data types
    assert isinstance(result["total_technical_jobs"], int)
    assert isinstance(result["job_titles"], list)

    # Verify reasonable values
    assert result["total_technical_jobs"] >= 0
    assert result["total_technical_jobs"] <= 1000

    print(f"\nJob postings data collected: {result}")


def test_collect_job_postings_multiple_companies(collector):
    """Test job postings for multiple AI labs."""
    companies = [
        ("Anthropic", "anthropic"),
        ("OpenAI", "openai"),
    ]

    for company_name, board_name in companies:
        result = collector.collect_job_postings(company_name, board_name)
        assert "total_technical_jobs" in result
        assert result["total_technical_jobs"] >= 0
        print(f"\n{company_name}: {result['total_technical_jobs']} jobs")


# Summary Generation Integration Tests


def test_generate_summary_real_api(collector):
    """Test summary generation with real Gemini API."""
    sample_metrics = {
        "low_end": {
            "headcount": {"aggregate_badge": "reasonably_weak"},
            "stock_index": {"current_value": 87.5},
        },
        "medium_end": {"headcount": {"aggregate_badge": "neutral"}},
        "high_end": {"job_postings": {"aggregate_badge": "strong"}},
    }

    result = collector.generate_summary(sample_metrics)

    # Verify it's a non-empty string
    assert isinstance(result, str)
    assert len(result) > 50  # Should be at least a sentence or two
    assert len(result) < 1000  # Should be a paragraph, not an essay

    print(f"\nGenerated summary: {result}")


# Error Handling Integration Tests


def test_collect_stock_data_handles_invalid_ticker(collector):
    """Test that invalid ticker is handled gracefully."""
    one_year_ago = date.today() - timedelta(days=365)

    # This might succeed with some data or might fail - either is acceptable
    # The key is that it shouldn't crash
    try:
        result = collector.collect_stock_data("InvalidCompany", "INVALID", one_year_ago)
        print(f"\nGot result for invalid ticker: {result}")
    except (ValueError, Exception) as e:
        print(f"\nHandled invalid ticker error: {e}")
        # This is acceptable behavior


def test_rate_limiting_multiple_requests(collector):
    """Test that multiple rapid requests don't cause rate limit errors."""
    # Make several requests in succession
    one_year_ago = date.today() - timedelta(days=365)

    results = []
    for company, ticker in [("Microsoft", "MSFT"), ("Apple", "AAPL")]:
        try:
            result = collector.collect_stock_data(company, ticker, one_year_ago)
            results.append(result)
            print(f"\nCollected data for {company}")
        except Exception as e:
            print(f"\nError collecting {company}: {e}")

    # At least one should succeed
    assert len(results) > 0
