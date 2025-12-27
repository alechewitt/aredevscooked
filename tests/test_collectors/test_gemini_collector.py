"""Tests for GeminiCollector class."""

import json
import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from aredevscooked.collectors.gemini_collector import GeminiCollector


# Fixtures


@pytest.fixture
def mock_gemini_response():
    """Create a mock Gemini API response."""

    def _create_response(text_content):
        mock_response = Mock()
        mock_response.text = text_content
        return mock_response

    return _create_response


@pytest.fixture
def collector():
    """Create a GeminiCollector instance with test API key."""
    return GeminiCollector(api_key="test-api-key")


# Stock Price Collection Tests


def test_collect_stock_data_returns_dict(collector, mock_gemini_response, mocker):
    """Stock data collection should return a dictionary."""
    mock_response_text = """```json
{
  "company": "HCLTech",
  "ticker": "HCL.NS",
  "current_price": 1450.50,
  "current_date": "2025-12-26",
  "price_1_year_ago": 1320.00,
  "price_1_year_ago_date": "2024-12-26",
  "source_urls": ["https://finance.yahoo.com"]
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.collect_stock_data("HCLTech", "HCL.NS", date(2024, 12, 26))

    assert isinstance(result, dict)
    assert "company" in result
    assert "current_price" in result


def test_collect_stock_data_parses_json(collector, mock_gemini_response, mocker):
    """Stock data collection should parse JSON from response."""
    mock_response_text = """```json
{
  "company": "HCLTech",
  "ticker": "HCL.NS",
  "current_price": 1450.50,
  "current_date": "2025-12-26",
  "price_1_year_ago": 1320.00,
  "price_1_year_ago_date": "2024-12-26",
  "source_urls": ["https://finance.yahoo.com"]
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.collect_stock_data("HCLTech", "HCL.NS", date(2024, 12, 26))

    assert result["company"] == "HCLTech"
    assert result["ticker"] == "HCL.NS"
    assert result["current_price"] == 1450.50
    assert result["price_1_year_ago"] == 1320.00


def test_collect_stock_data_validates_positive_price(
    collector, mock_gemini_response, mocker
):
    """Stock data collection should validate prices are positive."""
    mock_response_text = """```json
{
  "company": "HCLTech",
  "ticker": "HCL.NS",
  "current_price": -100.0,
  "current_date": "2025-12-26",
  "price_1_year_ago": 1320.00,
  "price_1_year_ago_date": "2024-12-26",
  "source_urls": ["https://finance.yahoo.com"]
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    with pytest.raises(ValueError, match="positive"):
        collector.collect_stock_data("HCLTech", "HCL.NS", date(2024, 12, 26))


# Headcount Collection Tests


def test_collect_headcount_returns_dict(collector, mock_gemini_response, mocker):
    """Headcount collection should return a dictionary."""
    mock_response_text = """```json
{
  "company": "Microsoft",
  "current_headcount": 228000,
  "data_date": "2025-09-30",
  "confidence": "high",
  "source_urls": ["https://microsoft.com"]
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.collect_headcount("Microsoft")

    assert isinstance(result, dict)
    assert "company" in result
    assert "current_headcount" in result


def test_collect_headcount_parses_json(collector, mock_gemini_response, mocker):
    """Headcount collection should parse JSON from response."""
    mock_response_text = """```json
{
  "company": "Microsoft",
  "current_headcount": 228000,
  "data_date": "2025-09-30",
  "confidence": "high",
  "source_urls": ["https://microsoft.com"]
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.collect_headcount("Microsoft")

    assert result["company"] == "Microsoft"
    assert result["current_headcount"] == 228000
    assert result["confidence"] == "high"


def test_collect_headcount_validates_range(collector, mock_gemini_response, mocker):
    """Headcount should be validated to be in plausible range."""
    mock_response_text = """```json
{
  "company": "Microsoft",
  "current_headcount": 5000000,
  "data_date": "2025-09-30",
  "confidence": "high",
  "source_urls": ["https://microsoft.com"]
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    with pytest.raises(ValueError, match="range"):
        collector.collect_headcount("Microsoft")


# Job Postings Collection Tests


def test_collect_job_postings_returns_dict(collector, mock_gemini_response, mocker):
    """Job postings collection should return a dictionary."""
    mock_response_text = """```json
{
  "company": "DeepMind",
  "total_technical_jobs": 45,
  "job_titles": ["Senior ML Engineer", "Research Scientist"],
  "collection_date": "2025-12-26",
  "source_url": "https://boards.greenhouse.io/v1/boards/deepmind/jobs"
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.collect_job_postings("DeepMind", "deepmind")

    assert isinstance(result, dict)
    assert "company" in result
    assert "total_technical_jobs" in result


def test_collect_job_postings_parses_json(collector, mock_gemini_response, mocker):
    """Job postings collection should parse JSON from response."""
    mock_response_text = """```json
{
  "company": "DeepMind",
  "total_technical_jobs": 45,
  "job_titles": ["Senior ML Engineer", "Research Scientist"],
  "collection_date": "2025-12-26",
  "source_url": "https://boards.greenhouse.io/v1/boards/deepmind/jobs"
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.collect_job_postings("DeepMind", "deepmind")

    assert result["company"] == "DeepMind"
    assert result["total_technical_jobs"] == 45
    assert isinstance(result["job_titles"], list)


def test_collect_job_postings_validates_non_negative(
    collector, mock_gemini_response, mocker
):
    """Job postings count should be non-negative."""
    mock_response_text = """```json
{
  "company": "DeepMind",
  "total_technical_jobs": -5,
  "job_titles": [],
  "collection_date": "2025-12-26",
  "source_url": "https://boards.greenhouse.io/v1/boards/deepmind/jobs"
}
```"""
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    with pytest.raises(ValueError, match="non-negative"):
        collector.collect_job_postings("DeepMind", "deepmind")


# Summary Generation Tests


def test_generate_summary_returns_string(collector, mock_gemini_response, mocker):
    """Summary generation should return a string."""
    mock_response_text = "The tech job market shows mixed signals."
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.generate_summary({"test": "data"})

    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_summary_returns_text(collector, mock_gemini_response, mocker):
    """Summary generation should return the text from response."""
    mock_response_text = "The tech job market shows mixed signals across all tiers."
    mock_model = mocker.patch.object(collector, "model")
    mock_model.generate_content.return_value = mock_gemini_response(mock_response_text)

    result = collector.generate_summary({"test": "data"})

    assert result == mock_response_text


# JSON Extraction Tests


def test_extract_json_from_markdown_code_block(collector):
    """Should extract JSON from markdown code blocks."""
    text = """```json
{
  "key": "value"
}
```"""
    result = collector._extract_json(text)
    assert result == {"key": "value"}


def test_extract_json_without_code_block(collector):
    """Should extract JSON without code blocks."""
    text = '{"key": "value"}'
    result = collector._extract_json(text)
    assert result == {"key": "value"}


def test_extract_json_handles_extra_whitespace(collector):
    """Should handle extra whitespace around JSON."""
    text = """

    {"key": "value"}

    """
    result = collector._extract_json(text)
    assert result == {"key": "value"}


def test_extract_json_raises_on_invalid_json(collector):
    """Should raise ValueError on invalid JSON."""
    text = "not valid json"
    with pytest.raises(ValueError, match="JSON"):
        collector._extract_json(text)
