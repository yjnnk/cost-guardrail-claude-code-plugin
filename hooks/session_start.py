#!/usr/bin/env python3
"""
SessionStart hook for cost guardrails plugin.
Checks spending at session start and shows warning if thresholds exceeded.
"""

import json
import sys
import os

# Add plugin root to path
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PLUGIN_ROOT)

from core.cost_calculator import (
    get_current_month_cost,
    determine_warning_level,
    format_warning_message,
    get_cost_breakdown
)
from core.usage_parser import get_current_month_usage
from core.state_manager import (
    should_show_warning,
    update_warning_shown,
    get_current_month_string
)

# Budget configuration
BUDGET_LIMIT = 15.00  # $15 per month


def main():
    """Main entry point for SessionStart hook."""
    try:
        # Read hook input from stdin (though we don't need it for this hook)
        try:
            input_data = json.load(sys.stdin)
        except:
            input_data = {}

        # Get current month
        current_month = get_current_month_string()

        # Calculate current spending
        current_cost = get_current_month_cost()

        # Determine warning level
        warning_level, percentage = determine_warning_level(current_cost, BUDGET_LIMIT)

        # Check if we should show warning
        if should_show_warning(warning_level, current_month):
            # Get usage records and breakdown
            records = get_current_month_usage()
            breakdown = get_cost_breakdown(records)

            # Format warning message
            message = format_warning_message(warning_level, current_cost, BUDGET_LIMIT, breakdown)

            # Update state to record that we showed this warning
            update_warning_shown(warning_level, current_month)

            # Output message to Claude Code
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "systemMessage": message
                }
            }
            print(json.dumps(output), file=sys.stdout, flush=True)

    except Exception as e:
        # Log error but don't block session
        # In production, we want to fail gracefully
        error_output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "systemMessage": f"⚠️  Cost guardrails plugin error: {str(e)}\nPlease check ~/.claude/cost_guardrails_state.json"
            }
        }
        print(json.dumps(error_output), file=sys.stdout, flush=True)

    finally:
        # Always exit 0 for SessionStart (don't block)
        sys.exit(0)


if __name__ == '__main__':
    main()
