"""Job postings processor for AI lab hiring analysis."""

from typing import Any
from aredevscooked.generators.badge_generator import BadgeGenerator


class JobsProcessor:
    """Process job posting data and classify changes with badges."""

    def __init__(self):
        """Initialize jobs processor with badge generator."""
        self.badge_generator = BadgeGenerator()

    def calculate_absolute_change(self, current: int, baseline: int) -> int:
        """Calculate absolute change in job postings.

        Args:
            current: Current job posting count
            baseline: Baseline job posting count

        Returns:
            Absolute change (e.g., 15 for 15 more jobs, -20 for 20 fewer jobs)

        Raises:
            ValueError: If current or baseline is negative
        """
        if current < 0:
            raise ValueError(f"Current job count must be non-negative: {current}")
        if baseline < 0:
            raise ValueError(f"Baseline job count must be non-negative: {baseline}")

        return current - baseline

    def classify_change(self, absolute_change: int) -> str:
        """Classify job posting change into badge level.

        Delegates to BadgeGenerator for consistent badge logic with absolute thresholds.

        Args:
            absolute_change: Absolute change in job count

        Returns:
            Badge level: strong, neutral, reasonably_weak, weak, or collapsing
        """
        return self.badge_generator.get_job_posting_badge(absolute_change)

    def process_company_metrics(
        self, company_name: str, current_jobs: int, baseline_jobs: int
    ) -> dict[str, Any]:
        """Process job posting metrics for a single company.

        Args:
            company_name: Company name
            current_jobs: Current technical job posting count
            baseline_jobs: Baseline technical job posting count

        Returns:
            Dictionary with company metrics including badge

        Raises:
            ValueError: If company name is empty or job counts invalid
        """
        if not company_name:
            raise ValueError("Company name cannot be empty")

        change = self.calculate_absolute_change(current_jobs, baseline_jobs)
        badge = self.classify_change(change)

        return {
            "company": company_name,
            "current": current_jobs,
            "change": change,
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
