#!/bin/bash
# Wrapper script for running GitHub Summary from cron
# This ensures proper environment setup including PATH and environment variables

# Source user's shell profile to get environment variables
# Try .zshrc first (for zsh), then .bash_profile, then .bashrc
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    source "$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi

# Ensure common binary paths are in PATH (where gh CLI is usually installed)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

# Change to script directory
cd "$(dirname "$0")" || exit 1

# Run the GitHub Summary tool with all passed arguments
./run.sh "$@"
