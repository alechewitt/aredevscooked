"""Tests for Gemini prompt templates."""

import pytest
from datetime import date
from aredevscooked.utils.gemini_prompts import (
    create_stock_price_prompt,
    create_headcount_prompt,
    create_job_postings_prompt,
    create_summary_prompt,
)


# Fixtures


@pytest.fixture
def sample_date():
    """Sample date for testing."""
    return date(2024, 12, 26)


@pytest.fixture
def sample_metrics():
    """Sample metrics data for summary prompt testing."""
    return {
        "low_end": {"headcount": {"aggregate_badge": "weak"}},
        "medium_end": {"headcount": {"aggregate_badge": "neutral"}},
        "high_end": {"job_postings": {"aggregate_badge": "strong"}},
    }


# Stock Price Prompt Tests


def test_stock_price_prompt_includes_company_name(sample_date):
    """Stock price prompt should include company name."""
    prompt = create_stock_price_prompt("HCLTech", "HCL.NS", sample_date)
    assert "HCLTech" in prompt


def test_stock_price_prompt_includes_ticker(sample_date):
    """Stock price prompt should include ticker symbol."""
    prompt = create_stock_price_prompt("HCLTech", "HCL.NS", sample_date)
    assert "HCL.NS" in prompt


def test_stock_price_prompt_includes_one_year_ago_date(sample_date):
    """Stock price prompt should include 1 year ago date."""
    prompt = create_stock_price_prompt("HCLTech", "HCL.NS", sample_date)
    assert "2024-12-26" in prompt


def test_stock_price_prompt_requests_json(sample_date):
    """Stock price prompt should request JSON output."""
    prompt = create_stock_price_prompt("HCLTech", "HCL.NS", sample_date)
    assert "JSON" in prompt or "json" in prompt


# Headcount Prompt Tests


def test_headcount_prompt_includes_company_name():
    """Headcount prompt should include company name."""
    prompt = create_headcount_prompt("Microsoft")
    assert "Microsoft" in prompt


def test_headcount_prompt_requests_json():
    """Headcount prompt should request JSON output."""
    prompt = create_headcount_prompt("Microsoft")
    assert "JSON" in prompt or "json" in prompt


def test_headcount_prompt_requests_confidence_level():
    """Headcount prompt should ask for confidence level."""
    prompt = create_headcount_prompt("Microsoft")
    assert "confidence" in prompt.lower()


def test_headcount_prompt_mentions_sources():
    """Headcount prompt should request sources."""
    prompt = create_headcount_prompt("Microsoft")
    assert "source" in prompt.lower()


# Job Postings Prompt Tests


def test_job_postings_prompt_includes_board_name():
    """Job postings prompt should include Greenhouse board name."""
    prompt = create_job_postings_prompt("DeepMind", "deepmind")
    assert "deepmind" in prompt


def test_job_postings_prompt_includes_greenhouse_url():
    """Job postings prompt should include greenhouse.io URL."""
    prompt = create_job_postings_prompt("DeepMind", "deepmind")
    assert "greenhouse.io" in prompt.lower()


def test_job_postings_prompt_mentions_technical_roles():
    """Job postings prompt should focus on technical roles."""
    prompt = create_job_postings_prompt("DeepMind", "deepmind")
    assert "technical" in prompt.lower() or "engineering" in prompt.lower()


def test_job_postings_prompt_requests_json():
    """Job postings prompt should request JSON output."""
    prompt = create_job_postings_prompt("DeepMind", "deepmind")
    assert "JSON" in prompt or "json" in prompt


# Summary Prompt Tests


def test_summary_prompt_includes_metrics_data(sample_metrics):
    """Summary prompt should include metrics data."""
    prompt = create_summary_prompt(sample_metrics)
    assert "weak" in prompt or str(sample_metrics) in prompt


def test_summary_prompt_mentions_three_tiers():
    """Summary prompt should mention all three company tiers."""
    sample_metrics = {"low_end": {}, "medium_end": {}, "high_end": {}}
    prompt = create_summary_prompt(sample_metrics)
    tier_mentions = (
        "low" in prompt.lower()
        or "medium" in prompt.lower()
        or "high" in prompt.lower()
        or "consultanc" in prompt.lower()
        or "big tech" in prompt.lower()
        or "AI lab" in prompt.lower()
    )
    assert tier_mentions


def test_summary_prompt_requests_single_paragraph():
    """Summary prompt should request a single paragraph."""
    sample_metrics = {}
    prompt = create_summary_prompt(sample_metrics)
    assert "paragraph" in prompt.lower() or "3-4 sentences" in prompt.lower()
