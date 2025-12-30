# GitHub Actions Documentation

This document describes how GitHub Actions workflows are configured and used in the Are Devs Cooked project.

## Overview

The project uses two GitHub Actions workflows:
1. **Daily Data Collection** - Automatically collects market data daily
2. **Deploy to GitHub Pages** - Deploys the website after data updates

## Workflow 1: Daily Data Collection

**File**: [.github/workflows/daily-collection.yml](../.github/workflows/daily-collection.yml)

### Purpose
Automatically runs the data collection script daily to gather:
- Stock prices for IT consultancies
- Headcount data for tech companies
- Job posting data for AI labs
- AI-generated market summary

### Triggers

```yaml
on:
  schedule:
    - cron: '5 8 * * *'  # 08:05 UTC daily
  workflow_dispatch:  # Allow manual triggering
```

- **Scheduled**: Runs automatically at 08:05 UTC every day
- **Manual**: Can be triggered manually via GitHub UI using workflow_dispatch

### Permissions

```yaml
permissions:
  contents: write
```

Requires write access to commit the collected data back to the repository.

### Steps Breakdown

#### 1. Checkout Repository
```yaml
- uses: actions/checkout@v6
```
- Uses the latest version (v6) of the checkout action
- Clones the repository to the runner

#### 2. Set Up Python
```yaml
- uses: actions/setup-python@v6
  with:
    python-version: '3.12'
```
- Installs Python 3.12 on the runner
- Uses the latest version (v6) of the setup-python action

#### 3. Install uv
```yaml
- run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.local/bin" >> $GITHUB_PATH
```
- Downloads and installs `uv` (fast Python package installer)
- Adds uv to the PATH for subsequent steps

#### 4. Install Dependencies
```yaml
- run: uv sync
```
- Installs all project dependencies using uv
- Equivalent to `pip install` but faster

#### 5. Verify API Key
```yaml
- env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    if [ -z "$GEMINI_API_KEY" ]; then
      echo "❌ GEMINI_API_KEY is NOT set"
      exit 1
    else
      echo "✓ GEMINI_API_KEY is set (length: ${#GEMINI_API_KEY} characters)"
    fi
```
- Checks that the GEMINI_API_KEY secret is configured
- Fails early if the secret is missing
- Shows the key length (but not the actual key) for debugging

#### 6. Run Data Collection
```yaml
- env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: uv run python scripts/run_collection.py
```
- Runs the main data collection script
- Passes the GEMINI_API_KEY as an environment variable
- Updates files in `data/processed/` and `website/`

#### 7. Commit and Push Changes
```yaml
- run: |
    git config --local user.email "github-actions[bot]@users.noreply.github.com"
    git config --local user.name "github-actions[bot]"
    git add data/processed/metrics_latest.json
    git add data/processed/metrics_history.json
    git add data/stocks.db
    git add website/metrics_latest.json
    git diff --staged --quiet || git commit -m "..."
    git push
```
- Configures git with the GitHub Actions bot identity
- Stages the updated data files
- Commits only if there are changes (`git diff --staged --quiet ||`)
- Pushes to the main branch
- Commit message includes the date and Claude Code attribution

### Files Updated by This Workflow

- `data/processed/metrics_latest.json` - Current market metrics
- `data/processed/metrics_history.json` - Historical snapshots
- `data/stocks.db` - SQLite database with stock price history
- `website/metrics_latest.json` - Copy of metrics for the website

## Workflow 2: Deploy to GitHub Pages

**File**: [.github/workflows/deploy-pages.yml](../.github/workflows/deploy-pages.yml)

### Purpose
Deploys the static website to GitHub Pages whenever:
- The website files are updated
- The daily data collection completes successfully

### Triggers

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'website/**'
  workflow_run:
    workflows: ["Daily Data Collection"]
    types:
      - completed
  workflow_dispatch:
```

Three trigger types:
1. **Push to main**: When any file in `website/` directory changes
2. **After data collection**: Automatically runs after "Daily Data Collection" completes
3. **Manual**: Can be triggered manually via GitHub UI

### Permissions

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

- `contents: read` - Read repository files
- `pages: write` - Deploy to GitHub Pages
- `id-token: write` - Required for GitHub Pages deployment authentication

### Concurrency Control

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: true
```

- Ensures only one Pages deployment runs at a time
- Cancels in-progress deployments if a new one is triggered
- Prevents conflicts and wasted resources

### Job Conditions

```yaml
if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
```

- If triggered by a `workflow_run` event, only proceeds if the triggering workflow succeeded
- Prevents deployment if data collection failed
- Always runs for other trigger types (push, manual)

### Steps Breakdown

#### 1. Checkout Repository
```yaml
- uses: actions/checkout@v6
  with:
    ref: main
```
- Checks out the main branch explicitly
- Ensures we're deploying the latest version

#### 2. Configure GitHub Pages
```yaml
- uses: actions/configure-pages@v5
```
- Sets up the Pages deployment environment
- Configures necessary metadata for deployment

#### 3. Upload Artifact
```yaml
- uses: actions/upload-pages-artifact@v4
  with:
    path: './website'
```
- Packages the `website/` directory as a deployment artifact
- This artifact will be deployed to Pages

#### 4. Deploy to GitHub Pages
```yaml
- uses: actions/deploy-pages@v4
```
- Deploys the uploaded artifact to GitHub Pages
- Makes the website live at the configured Pages URL

## Workflow Interaction

```
Daily Collection (08:05 UTC)
    |
    ├─> Collects data
    ├─> Updates data files
    ├─> Commits & pushes
    |
    └─> Triggers Deploy Pages (via workflow_run)
            |
            └─> Deploys updated website
```

The two workflows work together:
1. Daily Collection runs on schedule and updates data files
2. The commit triggers Deploy Pages (via workflow_run)
3. Deploy Pages publishes the updated website with fresh data

## GitHub Actions Versions

The project uses the latest versions of GitHub Actions as specified in [Simon Willison's actions-latest](https://simonw.github.io/actions-latest/versions.txt):

- `actions/checkout@v6` - Latest stable checkout action
- `actions/setup-python@v6` - Latest Python setup action
- `actions/configure-pages@v5` - Latest Pages configuration
- `actions/upload-pages-artifact@v4` - Latest artifact upload
- `actions/deploy-pages@v4` - Latest Pages deployment

## Secrets Configuration

The workflows require one secret to be configured in the GitHub repository settings:

### GEMINI_API_KEY

**Purpose**: API key for Google's Gemini API (used for data collection and AI summaries)

**Required By**: Daily Data Collection workflow

**How to Set**:
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GEMINI_API_KEY`
4. Value: Your Gemini API key
5. Click "Add secret"

**Security Notes**:
- Never commit API keys to the repository
- The workflow verifies the key is set before running collection
- The key is only accessible to workflow steps that explicitly request it via `env:`

## Manual Triggering

Both workflows support manual triggering:

1. Go to Actions tab in GitHub
2. Select the workflow (Daily Data Collection or Deploy to GitHub Pages)
3. Click "Run workflow" button
4. Select the branch (usually main)
5. Click "Run workflow"

This is useful for:
- Testing changes to workflows
- Triggering data collection outside the schedule
- Forcing a website deployment
- Debugging workflow issues

## Troubleshooting

### Data Collection Fails

**Check**:
1. GEMINI_API_KEY is set correctly in repository secrets
2. API key has sufficient quota/credits
3. Network connectivity to Gemini API
4. Workflow logs for specific error messages

### Deployment Fails

**Check**:
1. GitHub Pages is enabled in repository settings
2. Source is set to "GitHub Actions" (not branch)
3. website/ directory contains valid files
4. Workflow logs for deployment errors

### Commits Not Pushing

**Check**:
1. Workflow has `contents: write` permission
2. Branch protection rules allow bot commits
3. Git configuration is correct in workflow
4. Changes were actually made (not skipped by `git diff --staged --quiet`)

## Best Practices

### Implemented in This Project

1. **Use workflow_dispatch**: Allows manual testing without waiting for scheduled runs
2. **Verify secrets early**: Check GEMINI_API_KEY before running expensive operations
3. **Use concurrency control**: Prevents multiple Pages deployments from conflicting
4. **Conditional commits**: Only commit if files changed (`git diff --staged --quiet ||`)
5. **Latest action versions**: Use Simon Willison's actions-latest for current versions
6. **Descriptive commit messages**: Include date and attribution in automated commits
7. **Workflow chaining**: Use workflow_run to automatically deploy after data collection
8. **Path filters**: Only trigger Pages deployment when website/ changes

### Edge Cases Handled

1. **API key missing**: Workflow fails early with clear error message
2. **Collection failures**: Deploy only runs if collection succeeded (via workflow_run condition)
3. **No changes**: Skip commit if data hasn't changed
4. **Concurrent deployments**: Cancel in-progress deployments to prevent conflicts
5. **Server errors during collection**: New fallback mechanism uses yesterday's data (see [run_collection.py:394-433](../scripts/run_collection.py#L394-L433))

## Implementation Quirks

### Commit Message Format

The automated commit message follows a specific format:

```
data: automated daily collection YYYY-MM-DD

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

This format:
- Starts with `data:` prefix (conventional commit type)
- Includes ISO date for easy tracking
- Attributes to Claude Code
- Uses co-author for proper attribution

## Future Considerations

### Potential Improvements

1. **Notifications**: Add Slack/email notifications for collection failures
2. **Retry logic**: Automatically retry failed API calls before falling back to historical data
3. **Artifact storage**: Archive raw API responses for debugging
4. **Performance**: Cache dependencies between workflow runs
5. **Testing**: Add workflow to run tests before deployment
6. **Monitoring**: Track collection duration and data quality metrics

## Related Documentation

- [GEMINI_API.md](GEMINI_API.md) - Details on Gemini API usage
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Overall project structure
- [CLAUDE.md](../CLAUDE.md) - Project coding standards and instructions
