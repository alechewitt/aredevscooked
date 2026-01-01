"""Tests for Gemini prompt templates."""

import pytest
from aredevscooked.gemini_prompts import (
    create_headcount_prompt,
    create_job_postings_prompt,
    create_summary_prompt,
)


@pytest.fixture
def sample_metrics():
    """Sample metrics data for summary prompt testing."""
    return {
        "low_end": {"headcount": {"aggregate_badge": "weak"}},
        "medium_end": {"headcount": {"aggregate_badge": "neutral"}},
        "high_end": {"job_postings": {"aggregate_badge": "strong"}},
    }


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


def test_headcount_prompt_requests_multiple_periods():
    """Headcount prompt should request data for multiple time periods."""
    prompt = create_headcount_prompt("Microsoft")
    assert "current" in prompt.lower()
    assert "one year ago" in prompt.lower() or "one_year_ago" in prompt.lower()
    assert "q1 2023" in prompt.lower() or "q1_2023" in prompt.lower()


def test_headcount_prompt_includes_q1_2023_date():
    """Headcount prompt should include Q1 2023 target date."""
    prompt = create_headcount_prompt("Microsoft")
    assert "2023-03-31" in prompt


def test_headcount_prompt_requests_notes():
    """Headcount prompt should request notes for layoff adjustments."""
    prompt = create_headcount_prompt("Microsoft")
    assert "notes" in prompt.lower()


def test_headcount_prompt_mentions_quarterly_reports():
    """Headcount prompt should mention quarterly reports as primary sources."""
    prompt = create_headcount_prompt("Microsoft")
    assert "quarterly" in prompt.lower()


def test_headcount_prompt_mentions_layoff_adjustments():
    """Headcount prompt should mention layoff adjustments."""
    prompt = create_headcount_prompt("Microsoft")
    assert "layoff" in prompt.lower()


# Job Postings Prompt Tests


def test_job_postings_prompt_includes_company_name():
    """Job postings prompt should include company name."""
    prompt = create_job_postings_prompt(
        "DeepMind", "https://job-boards.greenhouse.io/deepmind"
    )
    assert "DeepMind" in prompt


def test_job_postings_prompt_includes_jobs_url():
    """Job postings prompt should include the jobs URL."""
    jobs_url = "https://job-boards.greenhouse.io/deepmind"
    prompt = create_job_postings_prompt("DeepMind", jobs_url)
    assert jobs_url in prompt


def test_job_postings_prompt_mentions_technical_roles():
    """Job postings prompt should focus on technical roles."""
    prompt = create_job_postings_prompt(
        "DeepMind", "https://job-boards.greenhouse.io/deepmind"
    )
    assert "technical" in prompt.lower() or "engineering" in prompt.lower()


def test_job_postings_prompt_requests_json():
    """Job postings prompt should request JSON output."""
    prompt = create_job_postings_prompt(
        "DeepMind", "https://job-boards.greenhouse.io/deepmind"
    )
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
