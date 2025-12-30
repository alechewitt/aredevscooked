"""Tests for orchestration script."""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
from scripts.run_collection import (
    collect_all_stock_data,
    collect_all_headcount_data,
    collect_all_job_posting_data,
    build_metrics_structure,
)


# Stock Data Collection Tests


@pytest.mark.asyncio
async def test_collect_all_stock_data_returns_dict(mocker):
    """Should collect stock data for all IT consultancies."""
    mock_collector = mocker.Mock()
    mock_collector.collect_stock_data.return_value = {
        "company": "HCLTech",
        "ticker": "HCL.NS",
        "current_price": 1450.50,
        "price_1_year_ago": 1320.00,
    }

    result = await collect_all_stock_data(mock_collector, date(2024, 12, 26))

    assert isinstance(result, dict)
    assert len(result) == 7  # 7 IT consultancies
    assert "HCLTech" in result
    assert mock_collector.collect_stock_data.call_count == 7


@pytest.mark.asyncio
async def test_collect_all_stock_data_calls_collector_for_each_company(mocker):
    """Should call collector for each IT consultancy."""
    mock_collector = mocker.Mock()
    mock_collector.collect_stock_data.return_value = {
        "company": "HCLTech",
        "ticker": "HCL.NS",
        "current_price": 1450.50,
        "price_1_year_ago": 1320.00,
    }

    one_year_ago = date(2024, 12, 26)
    await collect_all_stock_data(mock_collector, one_year_ago)

    # Verify called with correct company and ticker
    calls = mock_collector.collect_stock_data.call_args_list
    assert len(calls) == 7
    # Check first call
    assert calls[0][0][0] == "HCLTech"  # company_name
    assert calls[0][0][1] == "HCL.NS"  # ticker
    assert calls[0][0][2] == one_year_ago  # date


@pytest.mark.asyncio
async def test_collect_all_stock_data_handles_errors(mocker, caplog):
    """Should handle errors gracefully and continue collecting."""
    mock_collector = mocker.Mock()
    # First call fails, rest succeed
    mock_collector.collect_stock_data.side_effect = [
        ValueError("API error"),
        {"company": "LTIMindtree", "current_price": 5600.0, "price_1_year_ago": 5200.0},
        {"company": "Cognizant", "current_price": 78.0, "price_1_year_ago": 75.0},
        {"company": "Infosys", "current_price": 1500.0, "price_1_year_ago": 1450.0},
        {"company": "TCS", "current_price": 3700.0, "price_1_year_ago": 3600.0},
        {
            "company": "Tech Mahindra",
            "current_price": 1150.0,
            "price_1_year_ago": 1200.0,
        },
        {"company": "Wipro", "current_price": 400.0, "price_1_year_ago": 420.0},
    ]

    result = await collect_all_stock_data(mock_collector, date(2024, 12, 26))

    # Should have 6 successful results (1 failed)
    assert len(result) == 6
    assert "HCLTech" not in result
    assert "LTIMindtree" in result


# Headcount Data Collection Tests


@pytest.mark.asyncio
async def test_collect_all_headcount_data_returns_dict(mocker):
    """Should collect headcount for all companies (IT + Big Tech)."""
    mock_collector = mocker.Mock()
    mock_collector.collect_headcount.return_value = {
        "company": "HCLTech",
        "current_headcount": 226640,
        "data_date": "2025-09-30",
    }

    result = await collect_all_headcount_data(mock_collector)

    assert isinstance(result, dict)
    assert len(result) == 12  # 7 IT consultancies + 5 big tech
    assert "HCLTech" in result
    assert "Microsoft" in result
    assert mock_collector.collect_headcount.call_count == 12


@pytest.mark.asyncio
async def test_collect_all_headcount_data_calls_collector_for_each_company(mocker):
    """Should call collector for each company."""
    mock_collector = mocker.Mock()
    mock_collector.collect_headcount.return_value = {
        "company": "Microsoft",
        "current_headcount": 228000,
    }

    await collect_all_headcount_data(mock_collector)

    # Verify called with correct companies
    calls = mock_collector.collect_headcount.call_args_list
    assert len(calls) == 12
    company_names = [call[0][0] for call in calls]
    assert "HCLTech" in company_names
    assert "Microsoft" in company_names


# Job Posting Data Collection Tests


@pytest.mark.asyncio
async def test_collect_all_job_posting_data_returns_dict(mocker):
    """Should collect job postings for all AI labs."""
    mock_collector = mocker.Mock()
    mock_collector.collect_job_postings.return_value = {
        "company": "DeepMind",
        "total_technical_jobs": 45,
    }

    result = await collect_all_job_posting_data(mock_collector)

    assert isinstance(result, dict)
    assert len(result) == 3  # 3 AI labs
    assert "DeepMind" in result
    assert mock_collector.collect_job_postings.call_count == 3


@pytest.mark.asyncio
async def test_collect_all_job_posting_data_calls_collector_for_each_lab(mocker):
    """Should call collector for each AI lab with board name."""
    mock_collector = mocker.Mock()
    mock_collector.collect_job_postings.return_value = {
        "company": "Anthropic",
        "total_technical_jobs": 35,
    }

    await collect_all_job_posting_data(mock_collector)

    # Verify called with correct company and board
    calls = mock_collector.collect_job_postings.call_args_list
    assert len(calls) == 3
    # Check that board names are passed
    assert calls[0][0][1] in ["deepmind", "anthropic", "openai"]


# Metrics Structure Building Tests


def test_build_metrics_structure_returns_complete_structure(mocker):
    """Should build complete metrics_latest.json structure."""
    mock_stock_data = {
        "HCLTech": {"current_price": 1450.50, "price_1_year_ago": 1320.00}
    }
    mock_headcount_data = {"HCLTech": {"current_headcount": 226640}}
    mock_job_data = {"DeepMind": {"total_technical_jobs": 45}}

    result = build_metrics_structure(
        stock_data=mock_stock_data,
        headcount_data=mock_headcount_data,
        job_posting_data=mock_job_data,
        ai_summary="Test summary",
    )

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "low_end" in result
    assert "medium_end" in result
    assert "high_end" in result
    assert "ai_summary" in result


def test_build_metrics_structure_includes_metadata(mocker):
    """Should include metadata with timestamp."""
    result = build_metrics_structure(
        stock_data={}, headcount_data={}, job_posting_data={}, ai_summary=""
    )

    assert "last_updated" in result["metadata"]
    assert "collection_status" in result["metadata"]
    assert result["metadata"]["collection_status"] == "success"


def test_build_metrics_structure_low_end_tier(mocker):
    """Should build low-end tier with headcount."""
    mock_stock_data = {
        "HCLTech": {"current_price": 1450.50, "price_1_year_ago": 1320.00}
    }
    mock_headcount_data = {"HCLTech": {"current_headcount": 226640}}

    result = build_metrics_structure(
        stock_data=mock_stock_data,
        headcount_data=mock_headcount_data,
        job_posting_data={},
        ai_summary="",
    )

    assert "headcount" in result["low_end"]
    assert "stock_index" in result  # stock_index is at top level
    assert "companies" in result["low_end"]["headcount"]
    assert "aggregate_badge" in result["low_end"]["headcount"]


def test_build_metrics_structure_medium_end_tier(mocker):
    """Should build medium-end tier with headcount."""
    mock_headcount_data = {"Microsoft": {"current_headcount": 228000}}

    result = build_metrics_structure(
        stock_data={},
        headcount_data=mock_headcount_data,
        job_posting_data={},
        ai_summary="",
    )

    assert "headcount" in result["medium_end"]
    assert "companies" in result["medium_end"]["headcount"]
    assert "aggregate_badge" in result["medium_end"]["headcount"]


def test_build_metrics_structure_high_end_tier(mocker):
    """Should build high-end tier with job postings."""
    mock_job_data = {"DeepMind": {"total_technical_jobs": 45}}

    result = build_metrics_structure(
        stock_data={},
        headcount_data={},
        job_posting_data=mock_job_data,
        ai_summary="",
    )

    assert "job_postings" in result["high_end"]
    assert "companies" in result["high_end"]["job_postings"]
    assert "aggregate_badge" in result["high_end"]["job_postings"]
