"""Stock price processor for equal-weighted index calculation."""


class StockProcessor:
    """Calculate equal-weighted stock index for IT consultancies."""

    def calculate_index(
        self, current_prices: dict[str, float], baseline_prices: dict[str, float]
    ) -> float:
        """Calculate equal-weighted stock index.

        The index represents the average percentage change across all companies,
        normalized to 100 at baseline. Formula:
        Index = 100 × average((current_price / baseline_price) × 100)

        Args:
            current_prices: Dict of company name -> current stock price
            baseline_prices: Dict of company name -> baseline stock price

        Returns:
            Index value (100.0 = no change from baseline)

        Raises:
            ValueError: If companies don't match, prices invalid, or empty dicts
        """
        if not current_prices or not baseline_prices:
            raise ValueError("Price dictionaries must contain at least one company")

        if set(current_prices.keys()) != set(baseline_prices.keys()):
            raise ValueError("Companies must match between current and baseline prices")

        # Validate all prices are positive
        for company, price in current_prices.items():
            if price <= 0:
                raise ValueError(
                    f"Current price for {company} must be positive: {price}"
                )

        for company, price in baseline_prices.items():
            if price <= 0:
                raise ValueError(
                    f"Baseline price for {company} must be positive: {price}"
                )

        # Calculate percentage of baseline for each company
        percentage_changes = []
        for company in current_prices:
            pct = (current_prices[company] / baseline_prices[company]) * 100
            percentage_changes.append(pct)

        # Equal-weighted average
        index = sum(percentage_changes) / len(percentage_changes)
        return index

    def calculate_index_change(
        self, current_index: float, baseline_index: float
    ) -> float:
        """Calculate percentage point change in index.

        Args:
            current_index: Current index value
            baseline_index: Baseline index value (typically 100.0)

        Returns:
            Change in percentage points (e.g., 108.5 - 100.0 = 8.5)

        Raises:
            ValueError: If indices are not positive
        """
        if current_index <= 0:
            raise ValueError(f"Current index must be positive: {current_index}")
        if baseline_index <= 0:
            raise ValueError(f"Baseline index must be positive: {baseline_index}")

        return current_index - baseline_index

    def calculate_company_weights(self, companies: list[str]) -> dict[str, float]:
        """Calculate equal weights for all companies.

        Args:
            companies: List of company names

        Returns:
            Dict of company name -> weight (all weights = 1/n)

        Raises:
            ValueError: If company list is empty
        """
        if not companies:
            raise ValueError("Company list must contain at least one company")

        weight = 1.0 / len(companies)
        return {company: weight for company in companies}
