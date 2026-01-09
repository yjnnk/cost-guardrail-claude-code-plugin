#!/usr/bin/env bash
# Standalone command to check cost status
# Can be run from anywhere: ~/.claude/plugins/cost-guardrails/commands/cost-status.sh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Set CLAUDE_PLUGIN_ROOT environment variable
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"

# Run the Python script
python3 "${SCRIPT_DIR}/cost_status.py"
