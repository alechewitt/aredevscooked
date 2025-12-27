"""Gemini API prompt templates for data collection."""

from datetime import date
from typing import Any


def create_stock_price_prompt(
    company_name: str, ticker: str, one_year_ago: date
) -> str:
    """Create prompt for collecting stock price data.

    Args:
        company_name: Full company name (e.g., "HCLTech")
        ticker: Stock ticker symbol (e.g., "HCL.NS")
        one_year_ago: Date from exactly 1 year ago

    Returns:
        Formatted prompt string for Gemini API
    """
    return f"""Search the web for the current stock price of {company_name} (ticker: {ticker}).
Also find the stock price from exactly 1 year ago ({one_year_ago.strftime('%Y-%m-%d')}).

Return ONLY a JSON object with this exact structure:
{{
  "company": "{company_name}",
  "ticker": "{ticker}",
  "current_price": 0.00,
  "current_date": "YYYY-MM-DD",
  "price_1_year_ago": 0.00,
  "price_1_year_ago_date": "{one_year_ago.strftime('%Y-%m-%d')}",
  "source_urls": ["https://..."]
}}

Replace the placeholder values with actual data. Ensure prices are positive numbers.
Include source URLs for verification."""


def create_headcount_prompt(company_name: str, target_date: str | None = None) -> str:
    """Create prompt for collecting employee headcount data.

    Args:
        company_name: Full company name (e.g., "Microsoft")
        target_date: Optional target date in YYYY-MM-DD format for historical data

    Returns:
        Formatted prompt string for Gemini API
    """
    # Special handling for Amazon to get corporate-only headcount
    additional_instruction = ""
    if company_name == "Amazon":
        additional_instruction = "\n\nIMPORTANT: For Amazon, report CORPORATE employee headcount only, excluding warehouse and fulfillment center workers. Look for breakdowns in SEC filings or investor presentations that separate corporate from operations employees."

    # Add date-specific instruction if target_date provided
    date_instruction = ""
    if target_date:
        date_instruction = f"\n\nIMPORTANT: Find the employee headcount AS OF {target_date} or the closest available date. Look for quarterly reports, SEC filings, or earnings calls from that time period."
    else:
        date_instruction = "\n\nFind the most recent total employee headcount."

    return f"""Search the web for the total employee headcount of {company_name}.{date_instruction}
Look for official investor reports, earnings calls, or recent news articles. If layoffs have been announced,
please infer how that impacts the headcount numbers.{additional_instruction}

Return ONLY a JSON object with this exact structure:
{{
  "company": "{company_name}",
  "current_headcount": 0,
  "data_date": "YYYY-MM-DD",
  "confidence": "high",
  "source_urls": ["https://..."]
}}

Confidence levels:
- "high": Data from official company reports or SEC filings
- "medium": Data from reputable news sources
- "low": Estimates or unverified sources

Replace placeholder values with actual data. Headcount should be an integer between 1,000 and 2,000,000.
Include source URLs for verification."""


def create_job_postings_prompt(company_name: str, greenhouse_board: str) -> str:
    """Create prompt for collecting job posting counts.

    Args:
        company_name: Full company name (e.g., "DeepMind")
        greenhouse_board: Greenhouse board name (e.g., "deepmind")

    Returns:
        Formatted prompt string for Gemini API
    """
    return f"""Search https://boards.greenhouse.io/v1/boards/{greenhouse_board}/jobs and count only technical roles.

Technical roles include:
- Engineering (Software Engineer, ML Engineer, etc.)
- Research (Research Scientist, Applied Scientist, etc.)
- Technical roles with AI, ML, Data Science in the title

Ignore non-technical roles like:
- HR, Recruiting, People Operations
- Marketing, Sales, Business Development
- Operations, Finance, Legal

Return ONLY a JSON object with this exact structure:
{{
  "company": "{company_name}",
  "total_technical_jobs": 0,
  "job_titles": ["Job Title 1", "Job Title 2", "..."],
  "collection_date": "YYYY-MM-DD",
  "source_url": "https://boards.greenhouse.io/v1/boards/{greenhouse_board}/jobs"
}}

Replace placeholder values with actual data. Include a representative sample of job titles (up to 10).
Total technical jobs should be a non-negative integer."""


def create_summary_prompt(metrics_data: dict[str, Any]) -> str:
    """Create prompt for generating market summary.

    Args:
        metrics_data: Complete metrics data structure with all three tiers

    Returns:
        Formatted prompt string for Gemini API
    """
    return f"""Based on this IT job market data:

{metrics_data}

Write a single paragraph (3-4 sentences) summarizing the current state of the tech job market.

Focus on notable changes across the three tiers:
1. Low-end (IT consultancies): Headcount trends and stock performance
2. Medium-end (Big Tech): Headcount changes
3. High-end (AI labs): Hiring momentum via job postings

Be concise and factual. Highlight significant trends and compare across time periods when notable.
Return ONLY the paragraph text, no JSON or additional formatting."""
