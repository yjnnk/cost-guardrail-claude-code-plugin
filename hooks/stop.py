#!/usr/bin/env python3
"""
Stop hook for cost guardrails plugin.
Shows session summary when Claude Code session ends.
"""

import json
import sys
import os
``
# Add plugin root to path
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PLUGIN_ROOT)

from core.cost_calculator import (``
    get_current_month_cost,
    format_summary_message
)
from core.state_manager import update_cost_check

# Budget configuration
BUDGET_LIMIT = 15.00  # $15 per month


def main():
    """Main entry point for Stop hook."""
    try:
        # Read hook input from stdin (though we don't need it for this hook)
        try:
            input_data = json.load(sys.stdin)
        except:
            input_data = {}

        # Calculate current cost
        current_cost = get_current_month_cost()

        # Update state (record that we checked)
        update_cost_check()

        # Format summary message
        message = format_summary_message(current_cost, BUDGET_LIMIT)

        # Output message to Claude Code
        output = {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "systemMessage": message
            }
        }
        print(json.dumps(output), file=sys.stdout, flush=True)

    except Exception:
        # Fail silently on Stop - don't show errors to user at session end
        pass

    finally:
        # Always exit 0 for Stop (never block)
        sys.exit(0)


if __name__ == '__main__':
    main()
