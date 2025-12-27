# Project Structure Documentation

## Overview

`aredevscooked` tracks IT job market health through three company tiers using Gemini API with web search grounding. Updates daily via GitHub Actions, displays badge-based health indicators on a static website.

## Directory Structure

```
aredevscooked/
├── .github/workflows/         # GitHub Actions automation
│   └── daily-collection.yml   # Daily cron at 08:05 UTC
├── data/                      # JSON data storage (git-committed)
│   ├── processed/
│   │   ├── metrics_latest.json       # Current market state
│   │   ├── metrics_history.json      # Time series data
│   │   └── baselines.json            # Q1 2023 & 1-year-ago baselines
│   └── raw/                           # Optional: Daily Gemini responses
├── docs/                      # Documentation
│   ├── GEMINI_API.md          # Gemini API integration guide
│   └── PROJECT_STRUCTURE.md   # This file
├── src/aredevscooked/
│   ├── collectors/            # Data collection via Gemini API
│   │   └── gemini_collector.py
│   ├── processors/            # Data processing & calculations
│   │   ├── stock_processor.py        # Equal-weighted index
│   │   ├── headcount_processor.py    # Employee count analysis
│   │   └── jobs_processor.py         # Job posting analysis
│   ├── generators/            # Output generation
│   │   ├── badge_generator.py        # Badge classification logic
│   │   ├── summary_generator.py      # AI summary (future)
│   │   └── html_generator.py         # Static site builder (future)
│   ├── models/                # Data models (future)
│   │   └── schemas.py                # Pydantic models
│   └── utils/                 # Configuration & utilities
│       ├── config.py                 # Constants, thresholds, company lists
│       └── gemini_prompts.py         # Prompt templates
├── tests/                     # pytest tests (TDD workflow)
│   ├── conftest.py            # pytest configuration
│   ├── test_collectors/
│   │   ├── test_gemini_collector.py       # 15 unit tests
│   │   └── test_gemini_collector_integration.py  # 9 integration tests
│   ├── test_generators/
│   │   └── test_badge_generator.py        # 39 tests
│   └── test_processors/
│       ├── test_stock_processor.py        # 19 tests
│       ├── test_headcount_processor.py    # 27 tests
│       └── test_jobs_processor.py         # 24 tests
├── scripts/                   # Utility scripts
│   ├── run_collection.py              # Main orchestrator (future)
│   ├── backfill_historical.py         # Q1 2023 baseline (future)
│   ├── test_gemini.py                 # Manual API testing
│   └── debug_gemini_response.py       # Response structure debugging
├── website/                   # Static site (future)
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── .env                       # API keys (gitignored)
├── .gitignore
├── pyproject.toml             # uv project configuration
├── CLAUDE.md                  # Development instructions
└── README.md                  # Project overview
```

## Component Architecture

### Data Collection Layer

**`collectors/gemini_collector.py`** (GeminiCollector)
- **Purpose**: Single API for all data collection via Gemini with web search grounding
- **Methods**:
  - `collect_stock_data(company, ticker, one_year_ago)` → dict
  - `collect_headcount(company)` → dict
  - `collect_job_postings(company, greenhouse_board)` → dict
  - `generate_summary(metrics_data)` → str
- **Key Features**:
  - JSON extraction from Gemini responses (markdown code blocks or plain text)
  - Validation (stock prices, headcount ranges, non-negative job counts)
  - Robust text extraction (`_get_response_text()` with fallbacks)
- **Tests**: 15 unit tests (mocked), 9 integration tests (real API)

### Processing Layer

**`processors/stock_processor.py`** (StockProcessor)
- **Purpose**: Equal-weighted stock index for 7 IT consultancies
- **Formula**: `Index = 100 × average((current_price / baseline_price) × 100)`
- **Methods**:
  - `calculate_index(current_prices, baseline_prices)` → float
  - `calculate_index_change(current_index, baseline_index)` → float
  - `calculate_company_weights(companies)` → dict (all 1/n)
- **Tests**: 19 tests

**`processors/headcount_processor.py`** (HeadcountProcessor)
- **Purpose**: Employee count analysis with badge classification
- **Methods**:
  - `calculate_percentage_change(current, baseline)` → float
  - `calculate_absolute_change(current, baseline)` → int
  - `classify_change(percentage_change)` → str (badge)
  - `process_company_metrics(...)` → dict
  - `calculate_aggregate_badge(badges)` → str
- **Thresholds**: Percentage-based (±5%, ±10%, ±20%)
- **Tests**: 27 tests

**`processors/jobs_processor.py`** (JobsProcessor)
- **Purpose**: Job posting analysis using absolute thresholds
- **Methods**: Similar to HeadcountProcessor but uses absolute numbers
- **Thresholds**: Absolute-based (±10, ±20, ±40 jobs)
- **Tests**: 24 tests

### Generation Layer

**`generators/badge_generator.py`** (BadgeGenerator)
- **Purpose**: Classify metric changes into badge levels
- **Badge Levels** (worst to best):
  - `collapsing` (severity 0)
  - `weak` (severity 1)
  - `reasonably_weak` (severity 2)
  - `neutral` (severity 3)
  - `strong` (severity 4)
- **Methods**:
  - `get_headcount_badge(change_pct)` → str
  - `get_job_posting_badge(change_count)` → str
  - `get_aggregate_badge(badges)` → str (worst wins)
  - `get_badge_css_class(badge)` → str
  - `get_badge_display_text(badge)` → str
- **Critical**: Boundary conditions fixed (-10, -20, -40 go to more severe category)
- **Tests**: 39 tests

### Configuration

**`utils/config.py`**
- **Company Lists**:
  - `IT_CONSULTANCIES` (7): HCLTech, LTIMindtree, Cognizant, Infosys, TCS, Tech Mahindra, Wipro
  - `BIG_TECH` (5): Microsoft, Meta, Apple, Amazon, NVIDIA
  - `AI_LABS` (3): DeepMind, Anthropic, OpenAI
- **Thresholds**: `HEADCOUNT_THRESHOLDS`, `JOB_POSTING_THRESHOLDS`
- **Validation**: Ranges for stock prices, headcount, job postings
- **Gemini Config**: Model name, temperature, retries

**`utils/gemini_prompts.py`**
- Prompt templates requesting JSON responses
- Functions: `create_stock_price_prompt()`, `create_headcount_prompt()`, `create_job_postings_prompt()`, `create_summary_prompt()`

## Data Schema

### metrics_latest.json Structure

```json
{
  "metadata": {
    "last_updated": "2025-12-26T08:05:00Z",
    "collection_status": "success"
  },
  "low_end": {
    "headcount": {
      "companies": {
        "HCLTech": {
          "current": 226640,
          "changes": {
            "1_day": {"value": -100, "pct": -0.04, "badge": "neutral"},
            "30_day": {"value": -5000, "pct": -2.2, "badge": "neutral"},
            "1_year": {"value": -15000, "pct": -6.6, "badge": "reasonably_weak"},
            "since_q1_2023": {"value": +696, "pct": +0.3, "badge": "neutral"}
          }
        }
        // ... 7 companies
      },
      "aggregate_badge": "reasonably_weak"
    },
    "stock_index": {
      "current_value": 87.5,
      "baseline_date": "2024-12-26",
      "changes": {
        "1_day": -0.5,
        "30_day": -3.2,
        "1_year": -12.5
      },
      "companies": {
        "HCLTech": {"ticker": "HCL.NS", "current_price": 1450.50, "weight": 0.1429}
        // ... equal weights (1/7 each)
      }
    }
  },
  "medium_end": {
    "headcount": {
      "companies": { /* ... */ },
      "aggregate_badge": "neutral"
    }
  },
  "high_end": {
    "job_postings": {
      "companies": { /* ... */ },
      "aggregate_badge": "neutral"
    }
  },
  "ai_summary": "Market shows mixed signals..."
}
```

## Testing Strategy

### Test Organization

**Unit Tests**: Mock all external dependencies (Gemini API)
- Fast execution (< 1 second)
- Run by default: `uv run pytest`
- Coverage: 109 tests across all components

**Integration Tests**: Real Gemini API calls
- Marked with `@pytest.mark.integration`
- Require `GEMINI_API_KEY` in environment
- Skip by default: `pytest -k "not integration"`
- Run explicitly: `pytest -m integration`

### TDD Workflow

1. Write failing test first
2. Run test to confirm failure: `uv run pytest path/to/test.py -v`
3. Implement minimum code to pass
4. Run test to confirm pass
5. Refactor if needed
6. Format: `uv run black .`
7. Commit: Bundle test + implementation + docs together

### Test Fixtures

**`conftest.py`**: pytest configuration
- Custom markers for integration tests
- Shared fixtures (future)

**Test Structure**: Functions with pytest fixtures (NOT classes)
```python
@pytest.fixture
def processor():
    return StockProcessor()

def test_calculate_index(processor):
    result = processor.calculate_index(...)
    assert result == expected
```

## Development Workflow

### Tools

- **Package Manager**: `uv` (modern Python package manager)
- **Formatter**: `black`
- **Testing**: `pytest` with `pytest-mock`, `pytest-cov`
- **API Client**: `google-genai` (v1.0.0+)

### Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest                    # Unit tests only
uv run pytest -m integration     # Integration tests
uv run pytest --cov=src          # With coverage

# Format code
uv run black .

# Manual Gemini API testing
uv run scripts/test_gemini.py
uv run scripts/debug_gemini_response.py
```

### Commit Guidelines

- **Early & Often**: Commit after each passing test
- **Bundle**: Test + implementation + docs in single commit
- **Message Format**: `feat/fix: description` with co-author footer
- **Example**:
  ```
  feat: implement stock processor for equal-weighted index

  - Create StockProcessor class with index calculation
  - Add validation for matching companies
  - All 19 tests passing

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

## Key Design Decisions

1. **Gemini-First Architecture**: Single API (no yfinance, no multi-API complexity)
2. **Git-Committed JSON**: No database needed, version control built-in
3. **Static HTML Site**: Zero backend, fast loading, GitHub Pages compatible
4. **Equal-Weighted Index**: User-specified, normalized to 100 baseline
5. **Absolute Thresholds for AI Labs**: Small numbers make percentages too noisy
6. **Badge "Worst Wins" Strategy**: Aggregate badge = most concerning individual badge
7. **TDD Everything**: No code without tests first

## Future Implementation Phases

### Phase 1: Orchestration (Current Priority)
- `scripts/run_collection.py`: Main data collection orchestrator
- Integrate all collectors + processors + generators
- Output metrics_latest.json

### Phase 2: Historical Data
- `scripts/backfill_historical.py`: Collect Q1 2023 baseline
- Create baselines.json
- Initialize metrics_history.json

### Phase 3: HTML Generation
- `generators/html_generator.py`: Build static site
- `website/index.html`: Three-tier dashboard
- `website/styles.css`: Badge colors, responsive grid
- `website/script.js`: Load and display metrics

### Phase 4: GitHub Actions
- `.github/workflows/daily-collection.yml`: Daily automation
- Schedule: `cron: '5 8 * * *'` (08:05 UTC)
- Steps: Checkout → Setup → Install → Collect → Commit → Push
- Secret: `GEMINI_API_KEY`

### Phase 5: Deployment
- Enable GitHub Pages from `website/` directory
- Custom domain: aredevscooked.com
- Monitor first automated runs

## Current Status

**✅ Completed** (109 tests passing):
- Configuration & prompts (13 config tests, 15 prompt tests)
- Gemini collector (15 unit + 9 integration tests)
- Badge generator (39 tests)
- Stock processor (19 tests)
- Headcount processor (27 tests)
- Jobs processor (24 tests)

**🚧 In Progress**:
- Fixing Gemini API MALFORMED_FUNCTION_CALL error
- Proper response_mime_type configuration

**📋 TODO**:
- Orchestration script
- Historical data backfill
- HTML generation
- GitHub Actions workflow
- Website deployment
