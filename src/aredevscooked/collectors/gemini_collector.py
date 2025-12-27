"""Gemini API collector for market data."""

import json
import re
import os
from datetime import date
from typing import Any
from google import genai
from google.genai import types
from aredevscooked.utils.gemini_prompts import (
    create_stock_price_prompt,
    create_headcount_prompt,
    create_job_postings_prompt,
    create_summary_prompt,
)
from aredevscooked.utils.config import GEMINI_CONFIG, VALIDATION


class GeminiCollector:
    """Collect market data using Gemini API with web search grounding."""

    def __init__(self, api_key: str | None = None):
        """Initialize Gemini collector.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = GEMINI_CONFIG["model"]
        self.generation_config = types.GenerateContentConfig(
            temperature=GEMINI_CONFIG["temperature"],
        )

    def collect_stock_data(
        self, company_name: str, ticker: str, one_year_ago: date
    ) -> dict[str, Any]:
        """Collect stock price data for a company.

        Args:
            company_name: Full company name
            ticker: Stock ticker symbol
            one_year_ago: Date from exactly 1 year ago

        Returns:
            Dictionary with stock price data

        Raises:
            ValueError: If prices are invalid or out of range
        """
        prompt = create_stock_price_prompt(company_name, ticker, one_year_ago)
        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt, config=self.generation_config
        )
        data = self._extract_json(response.text)

        # Validate prices
        current_price = data.get("current_price", 0)
        price_1_year_ago = data.get("price_1_year_ago", 0)

        if current_price <= 0 or price_1_year_ago <= 0:
            raise ValueError(
                f"Stock prices must be positive: current={current_price}, "
                f"1_year_ago={price_1_year_ago}"
            )

        max_change = VALIDATION["stock_price"]["max_daily_change_pct"]
        # This is actually 1-year change, but we use a looser validation
        change_pct = abs((current_price - price_1_year_ago) / price_1_year_ago * 100)
        if change_pct > max_change * 10:  # 500% max change over 1 year
            raise ValueError(
                f"Stock price change seems unrealistic: {change_pct:.1f}% over 1 year"
            )

        return data

    def collect_headcount(self, company_name: str) -> dict[str, Any]:
        """Collect employee headcount data for a company.

        Args:
            company_name: Full company name

        Returns:
            Dictionary with headcount data

        Raises:
            ValueError: If headcount is out of plausible range
        """
        prompt = create_headcount_prompt(company_name)
        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt, config=self.generation_config
        )
        data = self._extract_json(response.text)

        # Validate headcount range
        headcount = data.get("current_headcount", 0)
        min_headcount = VALIDATION["headcount"]["min"]
        max_headcount = VALIDATION["headcount"]["max"]

        if not (min_headcount <= headcount <= max_headcount):
            raise ValueError(
                f"Headcount {headcount} outside plausible range "
                f"[{min_headcount}, {max_headcount}]"
            )

        return data

    def collect_job_postings(
        self, company_name: str, greenhouse_board: str
    ) -> dict[str, Any]:
        """Collect job posting counts for a company.

        Args:
            company_name: Full company name
            greenhouse_board: Greenhouse board name

        Returns:
            Dictionary with job posting data

        Raises:
            ValueError: If job count is negative
        """
        prompt = create_job_postings_prompt(company_name, greenhouse_board)
        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt, config=self.generation_config
        )
        data = self._extract_json(response.text)

        # Validate job count
        job_count = data.get("total_technical_jobs", 0)
        if job_count < 0:
            raise ValueError(f"Job posting count must be non-negative: {job_count}")

        return data

    def generate_summary(self, metrics_data: dict[str, Any]) -> str:
        """Generate AI-powered market summary.

        Args:
            metrics_data: Complete metrics data structure

        Returns:
            One-paragraph summary text
        """
        prompt = create_summary_prompt(metrics_data)
        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt, config=self.generation_config
        )
        return response.text.strip()

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from Gemini response text.

        Handles responses that may have JSON in markdown code blocks or plain text.

        Args:
            text: Response text from Gemini

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        # Try to extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError(f"Could not extract JSON from response: {text[:200]}")

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}")
