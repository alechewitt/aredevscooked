# Gemini API Integration Guide

## Model Information

**Current Model**: `gemini-3-flash-preview`
- Latest Gemini 3 Flash model with web search grounding support
- Available through Google AI Developer API (ai.google.dev)
- Free tier: 1,500 grounded requests/day
- Has 1000 RPM

## Python SDK

**Library**: `google-genai` (v1.0.0+)
- Official unified SDK for Gemini API (replacing deprecated `google-generativeai`)
- Works with both Google AI Developer API and Vertex AI
- Installation: `pip install google-genai`

## Response MIME Types

The `response_mime_type` parameter in `GenerateContentConfig` controls output format:

### Supported Types:

1. **Default (no parameter)**: Free-form text generation
   - Returns unstructured text responses
   - Use when you want plain text that you'll parse yourself

2. **`application/json`**: Structured JSON output
   - MUST be used with `response_schema` or `response_json_schema`
   - Guarantees schema-compliant JSON responses
   - Example:
     ```python
     config = types.GenerateContentConfig(
         response_mime_type='application/json',
         response_schema=MySchema,
     )
     ```

3. **`text/x.enum`**: Enum value output
   - For classification tasks
   - Returns single enum value from schema

### DO NOT Use:
- `text/plain` - This is NOT supported and may cause issues

**Sources**:
- [Structured Outputs Documentation](https://ai.google.dev/gemini-api/docs/structured-output)
- [Generate content API Reference](https://ai.google.dev/api/generate-content)

## Common Issues

### MALFORMED_FUNCTION_CALL Error

**Symptom**: Response has `finish_reason=MALFORMED_FUNCTION_CALL` and empty content

**Causes**:
- Gemini incorrectly interprets JSON structure in prompt as function call
- Using `response_mime_type='text/plain'` (not officially supported)
- Missing or malformed `response_schema` when using `application/json`

**Solutions**:
1. Remove `response_mime_type` entirely for free-form text with JSON in prompt
2. OR use `application/json` with proper `response_schema`
3. Ensure prompts don't include JSON that looks like function schemas

**Related Issues**:
- [python-genai #1120](https://github.com/googleapis/python-genai/issues/1120)
- [python-genai #1789](https://github.com/googleapis/python-genai/issues/1789)
- [Forum Discussion](https://discuss.ai.google.dev/t/malformed-function-call-finish-reason-happens-too-frequently-with-vertex-ai/93630)

## Response Text Extraction

Gemini API responses can be accessed in multiple ways:

### Primary Method:
```python
response = client.models.generate_content(...)
text = response.text  # Most common, direct access
```

### Fallback Methods (if `response.text` is None):
```python
# Via candidates structure
if response.candidates:
    candidate = response.candidates[0]
    if candidate.content and candidate.content.parts:
        text = candidate.content.parts[0].text
```

**Our Implementation**: `gemini_collector._get_response_text()` tries both methods

## Web Search Grounding

Gemini models support web search grounding for up-to-date information:

**Enabling**: Specify in prompts ("Search the web for...") or use tools configuration

**Free Tier Limits**:
- 1,500 grounded requests/day
- Separate quota from regular requests

## Configuration Best Practices

### Basic Text Generation (our current approach):
```python
config = types.GenerateContentConfig(
    temperature=0.0,  # Deterministic output
)
```

### Structured JSON Output (alternative):
```python
from pydantic import BaseModel

class StockData(BaseModel):
    company: str
    ticker: str
    current_price: float
    # ... more fields

config = types.GenerateContentConfig(
    temperature=0.0,
    response_mime_type='application/json',
    response_schema=StockData,
)
```

## API Authentication

**Environment Variable**: `GEMINI_API_KEY`
- Get API key from [Google AI Studio](https://aistudio.google.com/apikey)
- Set in `.env` file: `GEMINI_API_KEY=your-key-here`
- Load with `python-dotenv`

## Rate Limiting

**Free Tier Quotas** (per day):
- Regular requests: varies by model
- Grounded requests: 1,500/day
- Per-minute limits also apply

**Handling**:
- SDK has built-in retry with exponential backoff (via tenacity)
- 429 errors indicate quota exceeded
- Check usage: https://ai.dev/usage?tab=rate-limit

## Project-Specific Implementation

### Current Setup:
- **Model**: `gemini-3-flash-preview`
- **Config**: Temperature 0.0 for deterministic output
- **Response Format**: Free-form text with JSON in prompt (no `response_mime_type`)
- **Parsing**: Extract JSON from markdown code blocks with regex

### Data Collection Methods:
1. `collect_stock_data()` - Stock prices with 1-year comparison
2. `collect_headcount()` - Employee counts from official reports
3. `collect_job_postings()` - Technical jobs from Greenhouse boards
4. `generate_summary()` - AI-powered market analysis

### Validation:
- Stock prices: Must be positive, < 500% change over 1 year
- Headcount: Range [1,000 - 1,000,000], < 20% change in 30 days
- Job postings: Non-negative integers

## Testing

### Unit Tests:
- Mock Gemini API responses
- Test JSON extraction from various formats
- Validate error handling

### Integration Tests:
- Mark with `@pytest.mark.integration`
- Require real API key
- Skip by default: `pytest -k "not integration"`

### Manual Testing:
```bash
# Test all data collection methods
uv run scripts/test_gemini.py

# Debug response structure
uv run scripts/debug_gemini_response.py
```

## References

- [Google Gen AI SDK Documentation](https://googleapis.github.io/python-genai/)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Structured Outputs Guide](https://ai.google.dev/gemini-api/docs/structured-output)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
