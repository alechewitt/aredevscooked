"""Tests for JobsProcessor class."""

import pytest
from aredevscooked.processors.jobs_processor import JobsProcessor


@pytest.fixture
def processor():
    """Create a JobsProcessor instance."""
    return JobsProcessor()


# Absolute Change Calculation Tests


def test_calculate_absolute_change_increase(processor):
    """Should calculate positive absolute change."""
    current = 50
    baseline = 40

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == 10


def test_calculate_absolute_change_decrease(processor):
    """Should calculate negative absolute change."""
    current = 30
    baseline = 50

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == -20


def test_calculate_absolute_change_no_change(processor):
    """Should return zero for no change."""
    current = 45
    baseline = 45

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == 0


def test_calculate_absolute_change_large_increase(processor):
    """Should handle large increases."""
    current = 100
    baseline = 25

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == 75


def test_calculate_absolute_change_validates_non_negative_current(processor):
    """Should raise error for negative current count."""
    with pytest.raises(ValueError, match="non-negative"):
        processor.calculate_absolute_change(-5, 50)


def test_calculate_absolute_change_validates_non_negative_baseline(processor):
    """Should raise error for negative baseline count."""
    with pytest.raises(ValueError, match="non-negative"):
        processor.calculate_absolute_change(50, -10)


# Badge Classification with BadgeGenerator Tests


def test_classify_change_uses_badge_generator(processor, mocker):
    """Should delegate to BadgeGenerator for classification."""
    mock_badge_gen = mocker.patch.object(processor, "badge_generator")
    mock_badge_gen.get_job_posting_badge.return_value = "strong"

    badge = processor.classify_change(15)

    mock_badge_gen.get_job_posting_badge.assert_called_once_with(15)
    assert badge == "strong"


def test_classify_change_strong(processor):
    """Should classify ≥10 as strong."""
    badge = processor.classify_change(12)
    assert badge == "strong"


def test_classify_change_neutral(processor):
    """Should classify [-10, 9] as neutral."""
    assert processor.classify_change(5) == "neutral"
    assert processor.classify_change(-5) == "neutral"
    assert processor.classify_change(0) == "neutral"
    assert processor.classify_change(9) == "neutral"
    assert processor.classify_change(-10) == "neutral"


def test_classify_change_reasonably_weak(processor):
    """Should classify (-20, -10) as reasonably_weak."""
    badge = processor.classify_change(-15)
    assert badge == "reasonably_weak"


def test_classify_change_weak(processor):
    """Should classify (-40, -20] as weak."""
    badge = processor.classify_change(-30)
    assert badge == "weak"


def test_classify_change_collapsing(processor):
    """Should classify ≤-40 as collapsing."""
    badge = processor.classify_change(-50)
    assert badge == "collapsing"


# Company Metrics Processing Tests


def test_process_company_metrics_increase(processor):
    """Should process metrics with increase."""
    current_jobs = 55
    baseline_jobs = 40

    result = processor.process_company_metrics(
        company_name="DeepMind", current_jobs=current_jobs, baseline_jobs=baseline_jobs
    )

    assert result["company"] == "DeepMind"
    assert result["current"] == 55
    assert result["change"] == 15
    assert result["badge"] == "strong"


def test_process_company_metrics_no_change(processor):
    """Should process metrics with no change."""
    result = processor.process_company_metrics(
        company_name="Anthropic", current_jobs=30, baseline_jobs=30
    )

    assert result["company"] == "Anthropic"
    assert result["current"] == 30
    assert result["change"] == 0
    assert result["badge"] == "neutral"


def test_process_company_metrics_decrease(processor):
    """Should process metrics with decrease."""
    result = processor.process_company_metrics(
        company_name="OpenAI", current_jobs=25, baseline_jobs=50
    )

    assert result["company"] == "OpenAI"
    assert result["current"] == 25
    assert result["change"] == -25
    assert result["badge"] == "weak"


def test_process_company_metrics_large_decrease(processor):
    """Should process metrics with large decrease."""
    result = processor.process_company_metrics(
        company_name="OpenAI", current_jobs=10, baseline_jobs=60
    )

    assert result["company"] == "OpenAI"
    assert result["current"] == 10
    assert result["change"] == -50
    assert result["badge"] == "collapsing"


def test_process_company_metrics_validates_company_name(processor):
    """Should raise error for empty company name."""
    with pytest.raises(ValueError, match="Company name"):
        processor.process_company_metrics(
            company_name="", current_jobs=50, baseline_jobs=40
        )


# Aggregate Badge Calculation Tests


def test_calculate_aggregate_badge_uses_badge_generator(processor, mocker):
    """Should delegate to BadgeGenerator for aggregate badge."""
    mock_badge_gen = mocker.patch.object(processor, "badge_generator")
    mock_badge_gen.get_aggregate_badge.return_value = "reasonably_weak"

    badges = ["strong", "neutral", "reasonably_weak"]
    aggregate = processor.calculate_aggregate_badge(badges)

    mock_badge_gen.get_aggregate_badge.assert_called_once_with(badges)
    assert aggregate == "reasonably_weak"


def test_calculate_aggregate_badge_all_strong(processor):
    """Should return strong when all companies strong."""
    badges = ["strong", "strong", "strong"]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "strong"


def test_calculate_aggregate_badge_worst_wins(processor):
    """Should return worst badge (weak beats neutral)."""
    badges = ["strong", "neutral", "weak"]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "weak"


def test_calculate_aggregate_badge_empty_list(processor):
    """Should return neutral for empty list."""
    aggregate = processor.calculate_aggregate_badge([])
    assert aggregate == "neutral"


# Integration Tests


def test_full_workflow_three_ai_labs(processor):
    """Test complete workflow with three AI labs."""
    companies_data = [
        {"name": "DeepMind", "current": 50, "baseline": 45},  # +5
        {"name": "Anthropic", "current": 35, "baseline": 30},  # +5
        {"name": "OpenAI", "current": 60, "baseline": 55},  # +5
    ]

    results = []
    for company in companies_data:
        result = processor.process_company_metrics(
            company_name=company["name"],
            current_jobs=company["current"],
            baseline_jobs=company["baseline"],
        )
        results.append(result)

    # Verify individual results
    assert results[0]["company"] == "DeepMind"
    assert results[0]["change"] == 5
    assert results[0]["badge"] == "neutral"

    assert results[1]["company"] == "Anthropic"
    assert results[1]["change"] == 5
    assert results[1]["badge"] == "neutral"

    assert results[2]["company"] == "OpenAI"
    assert results[2]["change"] == 5
    assert results[2]["badge"] == "neutral"

    # Calculate aggregate
    badges = [r["badge"] for r in results]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "neutral"


def test_full_workflow_with_mixed_badges(processor):
    """Test workflow with mixed performance across AI labs."""
    companies_data = [
        {"name": "DeepMind", "current": 60, "baseline": 45},  # +15 strong
        {"name": "Anthropic", "current": 25, "baseline": 30},  # -5 neutral
        {"name": "OpenAI", "current": 30, "baseline": 55},  # -25 weak
    ]

    results = []
    for company in companies_data:
        result = processor.process_company_metrics(
            company_name=company["name"],
            current_jobs=company["current"],
            baseline_jobs=company["baseline"],
        )
        results.append(result)

    assert results[0]["badge"] == "strong"
    assert results[1]["badge"] == "neutral"
    assert results[2]["badge"] == "weak"

    # Aggregate should be "weak" (worst wins)
    badges = [r["badge"] for r in results]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "weak"


def test_full_workflow_hiring_freeze_scenario(processor):
    """Test scenario where all AI labs have hiring freeze."""
    companies_data = [
        {"name": "DeepMind", "current": 40, "baseline": 65},  # -25 weak
        {"name": "Anthropic", "current": 25, "baseline": 55},  # -30 weak
        {"name": "OpenAI", "current": 30, "baseline": 75},  # -45 collapsing
    ]

    results = []
    for company in companies_data:
        result = processor.process_company_metrics(
            company_name=company["name"],
            current_jobs=company["current"],
            baseline_jobs=company["baseline"],
        )
        results.append(result)

    assert results[0]["badge"] == "weak"
    assert results[1]["badge"] == "weak"
    assert results[2]["badge"] == "collapsing"

    # Aggregate should be "collapsing" (worst wins)
    badges = [r["badge"] for r in results]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "collapsing"
