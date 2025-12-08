#!/bin/bash
# Wrapper script for running GitHub Summary from cron
# This ensures proper environment setup including PATH and environment variables

# Ensure HOME is set (cron may not set it)
if [ -z "$HOME" ]; then
    export HOME=$(eval echo ~$(whoami))
fi

# Try to load exports from shell profiles
# Only extract 'export' lines to avoid issues with interactive-only scripts
for profile in "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.zshenv"; do
    if [ -f "$profile" ]; then
        eval "$(grep -E '^\s*export\s+' "$profile" 2>/dev/null)"
    fi
done

# Ensure common binary paths are in PATH (where gh CLI is usually installed)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

# Change to script directory
cd "$(dirname "$0")" || exit 1

# Run the GitHub Summary tool with all passed arguments
./run.sh "$@"
