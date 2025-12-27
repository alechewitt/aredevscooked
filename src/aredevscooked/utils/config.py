"""Configuration constants for aredevscooked."""

# IT Consultancies (Low-End Companies)
IT_CONSULTANCIES = [
    {"name": "HCLTech", "ticker": "HCL.NS"},
    {"name": "LTIMindtree", "ticker": "LTIM.NS"},
    {"name": "Cognizant", "ticker": "CTSH"},
    {"name": "Infosys", "ticker": "INFY"},
    {"name": "TCS", "ticker": "TCS.NS"},
    {"name": "Tech Mahindra", "ticker": "TECHM.NS"},
    {"name": "Wipro", "ticker": "WIT"},
]

# Big Tech Companies (Medium-End Companies)
BIG_TECH_COMPANIES = [
    {"name": "Microsoft"},
    {"name": "Meta"},
    {"name": "Apple"},
    {"name": "Amazon"},
    {"name": "NVIDIA"},
]

# AI Research Labs (High-End Companies)
AI_LABS = [
    {"name": "DeepMind", "greenhouse_board": "deepmind"},
    {"name": "Anthropic", "greenhouse_board": "anthropic"},
    {"name": "OpenAI", "greenhouse_board": "openai"},
]

# Badge Thresholds for Headcount (Percentage-based)
# Applied to IT Consultancies and Big Tech Companies
HEADCOUNT_THRESHOLDS = {
    "strong": 5.0,  # >= +5%
    "neutral": {
        "min": -5.0,
        "max": 5.0,
    },  # [-5%, +5%]
    "reasonably_weak": {
        "min": -10.0,
        "max": -5.0,
    },  # [-10%, -5%)
    "weak": {
        "min": -20.0,
        "max": -10.0,
    },  # [-20%, -10%)
    "collapsing": -20.0,  # < -20%
}

# Badge Thresholds for Job Postings (Absolute numbers)
# Applied to AI Labs
JOB_POSTING_THRESHOLDS = {
    "strong": 10,  # >= +10 postings
    "neutral": {
        "min": -10,
        "max": 10,
    },  # [-10, +10]
    "reasonably_weak": {
        "min": -20,
        "max": -10,
    },  # [-20, -10)
    "weak": {
        "min": -40,
        "max": -20,
    },  # [-40, -20)
    "collapsing": -40,  # < -40
}

# Q1 2023 Baseline Date (before ChatGPT impact)
Q1_2023_BASELINE_DATE = "2023-04-01"

# Time period configurations (in days)
TIME_PERIODS = {
    "1_day": 1,
    "30_day": 30,
    "1_year": 365,
}

# Validation ranges
VALIDATION = {
    "headcount": {
        "min": 1000,  # Minimum plausible headcount
        "max": 2_000_000,  # Maximum plausible headcount (Amazon has 1.5M+)
        "max_daily_change_pct": 5.0,  # Max 5% change in 1 day
        "max_30day_change_pct": 20.0,  # Max 20% change in 30 days
    },
    "stock_price": {
        "min": 0.01,  # Must be positive
        "max_daily_change_pct": 50.0,  # Max 50% change in 1 day
    },
    "job_postings": {
        "min": 0,  # Can be zero
        "max": 1000,  # Max plausible job postings
        "max_daily_change": 100,  # Max 100 new postings in 1 day
    },
}

# Gemini API Configuration
GEMINI_CONFIG = {
    "model": "gemini-3-flash-preview",  # Gemini 3 Flash with grounding support
    "max_retries": 3,
    "retry_delay_seconds": [1, 2, 4],  # Exponential backoff
    "temperature": 0.0,  # Deterministic for structured output
    "enable_grounding": True,
}

# GitHub Actions Cron Schedule
CRON_SCHEDULE = "5 8 * * *"  # 08:05 UTC daily
