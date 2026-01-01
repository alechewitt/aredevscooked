"""Gemini API prompt templates for data collection."""

from datetime import date, timedelta
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
  "price_1_year_ago_date": "{one_year_ago.strftime('%Y-%m-%d')}"
}}

Replace the placeholder values with actual data. Ensure prices are positive numbers."""


def create_headcount_prompt(company_name: str, target_date: str | None = None) -> str:
    """Create prompt for collecting employee headcount data across multiple time periods.

    Args:
        company_name: Full company name (e.g., "Microsoft")
        target_date: Optional target date in YYYY-MM-DD format (currently unused,
            kept for backward compatibility)

    Returns:
        Formatted prompt string for Gemini API
    """
    today = date.today()
    one_year_ago = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    q1_2023 = "2023-03-31"

    additional_instruction = ""
    if company_name == "Amazon":
        additional_instruction = """
AMAZON NOTE: Amazon does not separately report corporate vs warehouse headcount in SEC filings so you will need to rely on other sources to get an estimate of corporate workers. 
If you see a number 
above 1 million employees, that's the number including hourly workers and you should not consider number."""

    return f"""Search for employee headcount data for {company_name} across multiple time periods.

IMPORTANT RULES:
1. Use QUARTERLY earnings reports or 10-K/10-Q SEC filings as primary sources
2. Each company reports headcount quarterly - find the closest quarterly report to each target date
3. If layoffs were announced AFTER the quarterly report date, subtract them and note this in the "notes" field
{additional_instruction}

Find headcount for these time periods (use closest available quarterly report):
1. CURRENT: Most recent quarterly report + any subsequent layoff adjustments
2. ONE YEAR AGO: Quarterly report closest to {one_year_ago}
3. Q1 2023: Quarterly report closest to {q1_2023}

Return ONLY a JSON object with this exact structure:
{{
  "company": "{company_name}",
  "current": {{
    "headcount": 0,
    "as_of_date": "YYYY-MM-DD",
    "notes": "e.g., 'Q3 2024 10-Q filing minus 5k Jan 2025 layoffs'"
  }},
  "one_year_ago": {{
    "headcount": 0,
    "as_of_date": "YYYY-MM-DD",
    "notes": "e.g., 'Q4 2023 earnings report'"
  }},
  "q1_2023": {{
    "headcount": 0,
    "as_of_date": "YYYY-MM-DD",
    "notes": "e.g., 'FY2023 10-K filing'"
  }},
  "confidence": "high"
}}

RULES:
- headcount must be integers between 1,000 and 2,000,000
- as_of_date is when the headcount number is valid (after any layoff adjustments)
- notes should explain the source and any adjustments made (e.g., layoffs subtracted)
- confidence: "high" (SEC/official filings), "medium" (reputable news), "low" (estimates)

If data for a time period is unavailable, use null for that period's object."""


def create_job_postings_prompt(company_name: str, jobs_url: str) -> str:
    """Create prompt for collecting job posting counts.

    Args:
        company_name: Full company name (e.g., "DeepMind")
        jobs_url: URL to the company's job board

    Returns:
        Formatted prompt string for Gemini API
    """
    return f"""Search {jobs_url} and count only technical roles.

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
  "collection_date": "YYYY-MM-DD"
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

Write a humorous but informative paragraph (MAX 60 words) about whether devs are actually cooked.

Context: Small changes like -3% headcount aren't bad news - that's just normal market dynamics.
Real concerns are double-digit declines, collapsing stock prices, or AI labs going on hiring freezes.
Be witty about whether the sky is actually falling or if this is just another day in tech.

Focus on:
1. IT consultancies: Headcount & stock trends
2. Big Tech: Headcount changes
3. AI labs: Job posting momentum

Return ONLY the paragraph text, no JSON or additional formatting."""
