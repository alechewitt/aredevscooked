"""Badge generator for market health indicators."""

from aredevscooked.config import HEADCOUNT_THRESHOLDS, JOB_POSTING_THRESHOLDS


class BadgeGenerator:
    """Generate badges based on metric changes."""

    # Badge severity order (worst to best)
    BADGE_SEVERITY = {
        "collapsing": 0,
        "weak": 1,
        "reasonably_weak": 2,
        "neutral": 3,
        "strong": 4,
    }

    def get_headcount_badge(self, change_pct: float) -> str:
        """Get badge for headcount percentage change.

        Args:
            change_pct: Percentage change (e.g., -5.5 for -5.5%)

        Returns:
            Badge level: strong, neutral, reasonably_weak, weak, or collapsing
        """
        if change_pct >= HEADCOUNT_THRESHOLDS["strong"]:
            return "strong"
        elif (
            HEADCOUNT_THRESHOLDS["neutral"]["min"]
            <= change_pct
            <= HEADCOUNT_THRESHOLDS["neutral"]["max"]
        ):
            return "neutral"
        elif (
            HEADCOUNT_THRESHOLDS["reasonably_weak"]["min"]
            < change_pct
            <= HEADCOUNT_THRESHOLDS["reasonably_weak"]["max"]
        ):
            return "reasonably_weak"
        elif (
            HEADCOUNT_THRESHOLDS["weak"]["min"]
            < change_pct
            <= HEADCOUNT_THRESHOLDS["weak"]["max"]
        ):
            return "weak"
        else:  # change_pct <= HEADCOUNT_THRESHOLDS["collapsing"]
            return "collapsing"

    def get_job_posting_badge(self, change_count: int) -> str:
        """Get badge for job posting absolute change.

        Args:
            change_count: Absolute change in job count (e.g., -15 for 15 fewer jobs)

        Returns:
            Badge level: strong, neutral, reasonably_weak, weak, or collapsing
        """
        if change_count >= JOB_POSTING_THRESHOLDS["strong"]:
            return "strong"
        elif (
            JOB_POSTING_THRESHOLDS["neutral"]["min"]
            <= change_count
            <= JOB_POSTING_THRESHOLDS["neutral"]["max"]
        ):
            return "neutral"
        elif (
            JOB_POSTING_THRESHOLDS["reasonably_weak"]["min"]
            < change_count
            <= JOB_POSTING_THRESHOLDS["reasonably_weak"]["max"]
        ):
            return "reasonably_weak"
        elif (
            JOB_POSTING_THRESHOLDS["weak"]["min"]
            < change_count
            <= JOB_POSTING_THRESHOLDS["weak"]["max"]
        ):
            return "weak"
        else:  # change_count <= JOB_POSTING_THRESHOLDS["collapsing"]
            return "collapsing"

    def get_aggregate_badge(self, badges: list[str]) -> str:
        """Get aggregate badge from list of individual badges.

        Uses "worst badge wins" strategy - returns the most concerning badge.

        Args:
            badges: List of badge levels

        Returns:
            Worst (most concerning) badge level
        """
        if not badges:
            return "neutral"

        # Find badge with lowest severity (worst/most concerning)
        worst_badge = min(badges, key=lambda b: self.BADGE_SEVERITY.get(b, 3))
        return worst_badge

    def get_badge_css_class(self, badge: str) -> str:
        """Get CSS class for badge.

        Args:
            badge: Badge level

        Returns:
            CSS class name (e.g., "badge-strong")
        """
        return f"badge-{badge.replace('_', '-')}"

    def get_badge_display_text(self, badge: str) -> str:
        """Get display text for badge.

        Args:
            badge: Badge level

        Returns:
            Formatted display text (e.g., "Reasonably Weak")
        """
        return badge.replace("_", " ").title()
