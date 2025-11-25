# Quick Start Guide

Get your first GitHub merge summary in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- GitHub CLI (`gh`) installed and authenticated
- Anthropic API key (Shopify AI proxy token)

## Step 1: Install GitHub CLI (if needed)

```bash
# macOS
brew install gh

# Authenticate
gh auth login
```

## Step 2: Setup Virtual Environment

```bash
cd github-summary

# Run setup script (creates venv and installs all dependencies)
./setup.sh
```

## Step 3: Set Environment Variables

```bash
# Required: Anthropic API key
export OPENAI_API_KEY="your-shopify-ai-proxy-token"

# Required if using email output
export SMTP_USER="your.email@company.com"
export SMTP_PASSWORD="your-app-password"
export SMTP_FROM="your.email@company.com"
```

**Getting an SMTP app password:** See [docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md) for detailed instructions (takes 2 minutes).

## Step 4: Run Your First Summary

```bash
# Generate a summary and save to file
./run.sh --repos "shop/world" \
  --time-range 24h \
  --file my-first-summary.md

# View the result
cat my-first-summary.md
```

## Step 5: Try Email Output

```bash
./run.sh --repos "shop/world" \
  --time-range 24h \
  --email your.email@company.com
```

Check your inbox for a beautifully formatted HTML email!

## What's Next?

### Filter by Labels
```bash
./run.sh --repos "shop/world" \
  --labels "bug,feature,Slice: delivery" \
  --time-range 7d \
  --email team@example.com
```

### Track Specific Contributors
```bash
./run.sh --repos "org/repo" \
  --usernames "alice,bob" \
  --time-range 48h \
  --file team-report.md
```

### Use a Config File
```bash
# Copy example config
cp github_summary_config.yaml.example github_summary_config.yaml

# Edit with your preferences
nano github_summary_config.yaml

# Run with config
./run.sh --config github_summary_config.yaml
```

### Automate with Cron
See [examples/crontab.example](examples/crontab.example) for automated daily reports.

## Common Issues

**"gh: command not found"**
- Install GitHub CLI: `brew install gh` (macOS)
- Authenticate: `gh auth login`

**"No repositories specified"**
- Add `--repos "owner/repo"` to your command

**"At least one output method required"**
- Add `--email`, `--slack`, or `--file` to your command

**Email not working**
- See [docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md) for detailed setup

## Need Help?

- Full documentation: [README.md](README.md)
- Email setup: [docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md)
- Cron examples: [examples/crontab.example](examples/crontab.example)
