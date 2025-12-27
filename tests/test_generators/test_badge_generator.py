"""Tests for badge generator."""

import pytest
from aredevscooked.generators.badge_generator import BadgeGenerator


@pytest.fixture
def generator():
    """Create a BadgeGenerator instance."""
    return BadgeGenerator()


# Headcount Badge Tests (Percentage-based)


@pytest.mark.parametrize(
    "change_pct,expected_badge",
    [
        (6.0, "strong"),
        (5.0, "strong"),
        (4.9, "neutral"),
        (3.0, "neutral"),
        (0.0, "neutral"),
        (-3.0, "neutral"),
        (-5.0, "neutral"),
        (-5.1, "reasonably_weak"),
        (-7.0, "reasonably_weak"),
        (-9.9, "reasonably_weak"),
        (-10.0, "weak"),
        (-15.0, "weak"),
        (-19.9, "weak"),
        (-20.0, "collapsing"),
        (-25.0, "collapsing"),
        (-50.0, "collapsing"),
    ],
)
def test_get_headcount_badge(generator, change_pct, expected_badge):
    """Headcount badge should match threshold rules."""
    badge = generator.get_headcount_badge(change_pct)
    assert badge == expected_badge


# Job Posting Badge Tests (Absolute numbers)


@pytest.mark.parametrize(
    "change_count,expected_badge",
    [
        (15, "strong"),
        (10, "strong"),
        (9, "neutral"),
        (5, "neutral"),
        (0, "neutral"),
        (-5, "neutral"),
        (-10, "neutral"),
        (-11, "reasonably_weak"),
        (-15, "reasonably_weak"),
        (-19, "reasonably_weak"),
        (-20, "weak"),
        (-30, "weak"),
        (-39, "weak"),
        (-40, "collapsing"),
        (-50, "collapsing"),
        (-100, "collapsing"),
    ],
)
def test_get_job_posting_badge(generator, change_count, expected_badge):
    """Job posting badge should match absolute number thresholds."""
    badge = generator.get_job_posting_badge(change_count)
    assert badge == expected_badge


# Aggregate Badge Tests


def test_get_aggregate_badge_all_strong(generator):
    """Aggregate badge should be strong when all are strong."""
    badges = ["strong", "strong", "strong"]
    assert generator.get_aggregate_badge(badges) == "strong"


def test_get_aggregate_badge_all_neutral(generator):
    """Aggregate badge should be neutral when all are neutral."""
    badges = ["neutral", "neutral", "neutral"]
    assert generator.get_aggregate_badge(badges) == "neutral"


def test_get_aggregate_badge_worst_wins(generator):
    """Aggregate badge should be the worst badge (most concerning)."""
    # Collapsing is worst
    assert (
        generator.get_aggregate_badge(["strong", "neutral", "collapsing"])
        == "collapsing"
    )
    # Weak is second worst
    assert generator.get_aggregate_badge(["strong", "neutral", "weak"]) == "weak"
    # Reasonably weak is third worst
    assert (
        generator.get_aggregate_badge(["strong", "neutral", "reasonably_weak"])
        == "reasonably_weak"
    )


def test_get_aggregate_badge_empty_list(generator):
    """Aggregate badge should handle empty list."""
    assert generator.get_aggregate_badge([]) == "neutral"


def test_get_aggregate_badge_mixed_good_neutral(generator):
    """Aggregate with strong and neutral should be neutral."""
    assert generator.get_aggregate_badge(["strong", "neutral"]) == "neutral"


# Badge CSS Class Tests


def test_get_badge_css_class(generator):
    """Badge CSS class should match badge level."""
    assert generator.get_badge_css_class("strong") == "badge-strong"
    assert generator.get_badge_css_class("neutral") == "badge-neutral"
    assert generator.get_badge_css_class("reasonably_weak") == "badge-reasonably-weak"
    assert generator.get_badge_css_class("weak") == "badge-weak"
    assert generator.get_badge_css_class("collapsing") == "badge-collapsing"


def test_get_badge_display_text(generator):
    """Badge display text should be properly formatted."""
    assert generator.get_badge_display_text("strong") == "Strong"
    assert generator.get_badge_display_text("neutral") == "Neutral"
    assert generator.get_badge_display_text("reasonably_weak") == "Reasonably Weak"
    assert generator.get_badge_display_text("weak") == "Weak"
    assert generator.get_badge_display_text("collapsing") == "Collapsing"
