"""Headcount processor for employee count analysis."""

from typing import Any
from aredevscooked.generators.badge_generator import BadgeGenerator


class HeadcountProcessor:
    """Process headcount data and classify changes with badges."""

    def __init__(self):
        """Initialize headcount processor with badge generator."""
        self.badge_generator = BadgeGenerator()

    def calculate_percentage_change(self, current: int, baseline: int) -> float:
        """Calculate percentage change in headcount.

        Args:
            current: Current headcount
            baseline: Baseline headcount

        Returns:
            Percentage change (e.g., 10.0 for +10%)

        Raises:
            ValueError: If current is negative or baseline is non-positive
        """
        if current < 0:
            raise ValueError(f"Current headcount must be non-negative: {current}")
        if baseline <= 0:
            raise ValueError(f"Baseline headcount must be positive: {baseline}")

        return ((current - baseline) / baseline) * 100

    def calculate_absolute_change(self, current: int, baseline: int) -> int:
        """Calculate absolute change in headcount.

        Args:
            current: Current headcount
            baseline: Baseline headcount

        Returns:
            Absolute change (e.g., 5000 for 5000 more employees)

        Raises:
            ValueError: If current or baseline is negative
        """
        if current < 0:
            raise ValueError(f"Current headcount must be non-negative: {current}")
        if baseline < 0:
            raise ValueError(f"Baseline headcount must be non-negative: {baseline}")

        return current - baseline

    def classify_change(self, percentage_change: float) -> str:
        """Classify headcount change into badge level.

        Delegates to BadgeGenerator for consistent badge logic.

        Args:
            percentage_change: Percentage change value

        Returns:
            Badge level: strong, neutral, reasonably_weak, weak, or collapsing
        """
        return self.badge_generator.get_headcount_badge(percentage_change)

    def process_company_metrics(
        self, company_name: str, current_headcount: int, baseline_headcount: int
    ) -> dict[str, Any]:
        """Process headcount metrics for a single company.

        Args:
            company_name: Company name
            current_headcount: Current employee count
            baseline_headcount: Baseline employee count

        Returns:
            Dictionary with company metrics including badge

        Raises:
            ValueError: If company name is empty or headcounts invalid
        """
        if not company_name:
            raise ValueError("Company name cannot be empty")

        change_pct = self.calculate_percentage_change(
            current_headcount, baseline_headcount
        )
        change_abs = self.calculate_absolute_change(
            current_headcount, baseline_headcount
        )
        badge = self.classify_change(change_pct)

        return {
            "company": company_name,
            "current": current_headcount,
            "change_absolute": change_abs,
            "change_pct": change_pct,
            "badge": badge,
        }

    def calculate_aggregate_badge(self, badges: list[str]) -> str:
        """Calculate aggregate badge from list of individual badges.

        Uses "worst badge wins" strategy via BadgeGenerator.

        Args:
            badges: List of badge levels

        Returns:
            Worst (most concerning) badge level
        """
        return self.badge_generator.get_aggregate_badge(badges)
