#!/bin/bash
# Wrapper script for running GitHub Summary from launchd
# Automatically uses 72h on Monday (covers weekend), 24h on other days

set -e

# Ensure HOME is set
if [ -z "$HOME" ]; then
    export HOME=$(eval echo ~$(whoami))
fi

# Load environment variables from shell profiles
for profile in "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.zshenv"; do
    if [ -f "$profile" ]; then
        eval "$(grep -E '^\s*export\s+' "$profile" 2>/dev/null)"
    fi
done

# Ensure PATH includes common binary locations (for gh, python, etc.)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

cd "$(dirname "$0")"

# Determine time range based on day of week
# 1 = Monday, use 72h to cover weekend
DAY_OF_WEEK=$(date +%u)

if [ "$DAY_OF_WEEK" -eq 1 ]; then
    TIME_RANGE="72h"
else
    TIME_RANGE="24h"
fi

echo "$(date): Running github-summary with ${TIME_RANGE} time range"

# Run with the config file, overriding time-range
./run.sh --config github_summary_config.yaml --time-range "$TIME_RANGE"
