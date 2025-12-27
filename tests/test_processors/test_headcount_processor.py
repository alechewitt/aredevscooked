"""Tests for HeadcountProcessor class."""

import pytest
from datetime import date
from aredevscooked.processors.headcount_processor import HeadcountProcessor


@pytest.fixture
def processor():
    """Create a HeadcountProcessor instance."""
    return HeadcountProcessor()


# Percentage Change Calculation Tests


def test_calculate_percentage_change_increase(processor):
    """Should calculate positive percentage change."""
    current = 110000
    baseline = 100000

    pct_change = processor.calculate_percentage_change(current, baseline)

    assert pct_change == pytest.approx(10.0, rel=1e-2)


def test_calculate_percentage_change_decrease(processor):
    """Should calculate negative percentage change."""
    current = 90000
    baseline = 100000

    pct_change = processor.calculate_percentage_change(current, baseline)

    assert pct_change == pytest.approx(-10.0, rel=1e-2)


def test_calculate_percentage_change_no_change(processor):
    """Should return zero for no change."""
    current = 100000
    baseline = 100000

    pct_change = processor.calculate_percentage_change(current, baseline)

    assert pct_change == pytest.approx(0.0, rel=1e-2)


def test_calculate_percentage_change_large_increase(processor):
    """Should handle large increases."""
    current = 250000
    baseline = 100000

    pct_change = processor.calculate_percentage_change(current, baseline)

    assert pct_change == pytest.approx(150.0, rel=1e-2)


def test_calculate_percentage_change_validates_positive_baseline(processor):
    """Should raise error for non-positive baseline."""
    with pytest.raises(ValueError, match="positive"):
        processor.calculate_percentage_change(100000, 0)


def test_calculate_percentage_change_validates_non_negative_current(processor):
    """Should raise error for negative current headcount."""
    with pytest.raises(ValueError, match="non-negative"):
        processor.calculate_percentage_change(-1000, 100000)


# Absolute Change Calculation Tests


def test_calculate_absolute_change_increase(processor):
    """Should calculate positive absolute change."""
    current = 110000
    baseline = 100000

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == 10000


def test_calculate_absolute_change_decrease(processor):
    """Should calculate negative absolute change."""
    current = 90000
    baseline = 100000

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == -10000


def test_calculate_absolute_change_no_change(processor):
    """Should return zero for no change."""
    current = 100000
    baseline = 100000

    abs_change = processor.calculate_absolute_change(current, baseline)

    assert abs_change == 0


def test_calculate_absolute_change_validates_non_negative_current(processor):
    """Should raise error for negative current headcount."""
    with pytest.raises(ValueError, match="non-negative"):
        processor.calculate_absolute_change(-1000, 100000)


def test_calculate_absolute_change_validates_non_negative_baseline(processor):
    """Should raise error for negative baseline headcount."""
    with pytest.raises(ValueError, match="non-negative"):
        processor.calculate_absolute_change(100000, -1000)


# Badge Classification with BadgeGenerator Tests


def test_classify_change_uses_badge_generator(processor, mocker):
    """Should delegate to BadgeGenerator for classification."""
    mock_badge_gen = mocker.patch.object(processor, "badge_generator")
    mock_badge_gen.get_headcount_badge.return_value = "strong"

    badge = processor.classify_change(8.5)

    mock_badge_gen.get_headcount_badge.assert_called_once_with(8.5)
    assert badge == "strong"


def test_classify_change_strong(processor):
    """Should classify ≥5% as strong."""
    badge = processor.classify_change(6.0)
    assert badge == "strong"


def test_classify_change_neutral(processor):
    """Should classify [-5%, 5%] as neutral."""
    assert processor.classify_change(3.0) == "neutral"
    assert processor.classify_change(-3.0) == "neutral"
    assert processor.classify_change(0.0) == "neutral"


def test_classify_change_reasonably_weak(processor):
    """Should classify (-10%, -5%) as reasonably_weak."""
    badge = processor.classify_change(-7.5)
    assert badge == "reasonably_weak"


def test_classify_change_weak(processor):
    """Should classify (-20%, -10%] as weak."""
    badge = processor.classify_change(-15.0)
    assert badge == "weak"


def test_classify_change_collapsing(processor):
    """Should classify ≤-20% as collapsing."""
    badge = processor.classify_change(-25.0)
    assert badge == "collapsing"


# Company Metrics Processing Tests


def test_process_company_metrics_single_timepoint(processor):
    """Should process metrics with single timepoint comparison."""
    current_headcount = 110000
    baseline_headcount = 100000

    result = processor.process_company_metrics(
        company_name="Microsoft",
        current_headcount=current_headcount,
        baseline_headcount=baseline_headcount,
    )

    assert result["company"] == "Microsoft"
    assert result["current"] == 110000
    assert result["change_absolute"] == 10000
    assert result["change_pct"] == pytest.approx(10.0, rel=1e-2)
    assert result["badge"] == "strong"


def test_process_company_metrics_no_change(processor):
    """Should process metrics with no change."""
    result = processor.process_company_metrics(
        company_name="Meta", current_headcount=67000, baseline_headcount=67000
    )

    assert result["company"] == "Meta"
    assert result["current"] == 67000
    assert result["change_absolute"] == 0
    assert result["change_pct"] == pytest.approx(0.0, rel=1e-2)
    assert result["badge"] == "neutral"


def test_process_company_metrics_decrease(processor):
    """Should process metrics with decrease."""
    result = processor.process_company_metrics(
        company_name="HCLTech", current_headcount=210000, baseline_headcount=226640
    )

    assert result["company"] == "HCLTech"
    assert result["current"] == 210000
    assert result["change_absolute"] == -16640
    # (210000 - 226640) / 226640 * 100 = -7.34%
    assert result["change_pct"] == pytest.approx(-7.34, rel=1e-2)
    assert result["badge"] == "reasonably_weak"


def test_process_company_metrics_validates_company_name(processor):
    """Should raise error for empty company name."""
    with pytest.raises(ValueError, match="Company name"):
        processor.process_company_metrics(
            company_name="", current_headcount=100000, baseline_headcount=100000
        )


# Aggregate Badge Calculation Tests


def test_calculate_aggregate_badge_uses_badge_generator(processor, mocker):
    """Should delegate to BadgeGenerator for aggregate badge."""
    mock_badge_gen = mocker.patch.object(processor, "badge_generator")
    mock_badge_gen.get_aggregate_badge.return_value = "weak"

    badges = ["strong", "neutral", "weak"]
    aggregate = processor.calculate_aggregate_badge(badges)

    mock_badge_gen.get_aggregate_badge.assert_called_once_with(badges)
    assert aggregate == "weak"


def test_calculate_aggregate_badge_all_strong(processor):
    """Should return strong when all companies strong."""
    badges = ["strong", "strong", "strong"]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "strong"


def test_calculate_aggregate_badge_worst_wins(processor):
    """Should return worst badge (collapsing beats everything)."""
    badges = ["strong", "neutral", "collapsing"]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "collapsing"


def test_calculate_aggregate_badge_empty_list(processor):
    """Should return neutral for empty list."""
    aggregate = processor.calculate_aggregate_badge([])
    assert aggregate == "neutral"


# Integration Tests


def test_full_workflow_multiple_companies(processor):
    """Test complete workflow with multiple companies."""
    companies_data = [
        {"name": "Microsoft", "current": 228000, "baseline": 221000},
        {"name": "Meta", "current": 67000, "baseline": 67000},
        {"name": "Apple", "current": 164000, "baseline": 164000},
    ]

    results = []
    for company in companies_data:
        result = processor.process_company_metrics(
            company_name=company["name"],
            current_headcount=company["current"],
            baseline_headcount=company["baseline"],
        )
        results.append(result)

    # Verify individual results
    assert results[0]["company"] == "Microsoft"
    assert results[0]["change_pct"] == pytest.approx(3.17, rel=1e-2)
    assert results[0]["badge"] == "neutral"

    assert results[1]["company"] == "Meta"
    assert results[1]["change_pct"] == pytest.approx(0.0, rel=1e-2)
    assert results[1]["badge"] == "neutral"

    # Calculate aggregate
    badges = [r["badge"] for r in results]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "neutral"


def test_full_workflow_with_mixed_badges(processor):
    """Test workflow with mixed performance."""
    companies_data = [
        {"name": "HCLTech", "current": 210000, "baseline": 226640},  # -7.34% weak
        {"name": "Infosys", "current": 321000, "baseline": 314000},  # +2.23% neutral
        {"name": "TCS", "current": 550000, "baseline": 614000},  # -10.42% weak
    ]

    results = []
    for company in companies_data:
        result = processor.process_company_metrics(
            company_name=company["name"],
            current_headcount=company["current"],
            baseline_headcount=company["baseline"],
        )
        results.append(result)

    assert results[0]["badge"] == "reasonably_weak"
    assert results[1]["badge"] == "neutral"
    assert results[2]["badge"] == "weak"

    # Aggregate should be "weak" (worst wins)
    badges = [r["badge"] for r in results]
    aggregate = processor.calculate_aggregate_badge(badges)
    assert aggregate == "weak"
