"""Mock Gemini API responses for testing."""

# Mock stock price response
MOCK_STOCK_RESPONSE = """```json
{
  "company": "HCLTech",
  "ticker": "HCL.NS",
  "current_price": 1450.50,
  "current_date": "2025-12-26",
  "price_1_year_ago": 1320.00,
  "price_1_year_ago_date": "2024-12-26",
  "source_urls": ["https://finance.yahoo.com/quote/HCL.NS"]
}
```"""

# Mock headcount response
MOCK_HEADCOUNT_RESPONSE = """```json
{
  "company": "Microsoft",
  "current_headcount": 228000,
  "data_date": "2025-09-30",
  "confidence": "high",
  "source_urls": ["https://microsoft.com/investor-relations"]
}
```"""

# Mock job postings response
MOCK_JOB_POSTINGS_RESPONSE = """```json
{
  "company": "DeepMind",
  "total_technical_jobs": 45,
  "job_titles": ["Senior ML Engineer", "Research Scientist", "Software Engineer"],
  "collection_date": "2025-12-26",
  "source_url": "https://job-boards.greenhouse.io/deepmind"
}
```"""

# Mock summary response
MOCK_SUMMARY_RESPONSE = """The tech job market shows mixed signals across tiers. IT consultancies continue modest headcount declines with stock performance at 87.5% of baseline. Big tech maintains stable headcount with slight growth. AI research labs demonstrate strong hiring momentum with 45 technical positions posted."""
