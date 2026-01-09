#!/usr/bin/env python3
"""
Standalone cost status command.
Shows detailed breakdown of current month spending.
"""

import sys
import os
from datetime import datetime

# Add plugin root to path
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PLUGIN_ROOT)

from core.cost_calculator import (
    get_current_month_cost,
    get_cost_breakdown,
    get_usage_stats
)
from core.usage_parser import get_current_month_usage

# Budget configuration
BUDGET_LIMIT = 15.00  # $15 per month


def main():
    """Main entry point for cost status command."""
    try:
        # Get current month info
        now = datetime.now()
        month_name = now.strftime("%B %Y")

        # Get usage data
        records = get_current_month_usage()
        current_cost = get_current_month_cost()
        breakdown = get_cost_breakdown(records)
        stats = get_usage_stats(records)

        # Calculate stats
        percentage = (current_cost / BUDGET_LIMIT) * 100 if BUDGET_LIMIT > 0 else 0
        remaining = BUDGET_LIMIT - current_cost

        # Print header
        print(f"\n📊 Cost Status for {month_name}\n")
        print("=" * 50)

        # Print summary
        print(f"\nCurrent spending: ${current_cost:.2f}")
        print(f"Monthly budget:   ${BUDGET_LIMIT:.2f}")
        print(f"Remaining:        ${remaining:.2f}")
        print(f"Usage:            {percentage:.1f}%\n")

        # Print breakdown by model
        if breakdown:
            print("Breakdown by model:")
            print("-" * 50)
            for model_name in sorted(breakdown.keys()):
                cost = breakdown[model_name]
                model_percentage = (cost / current_cost * 100) if current_cost > 0 else 0
                print(f"  {model_name:8} ${cost:6.2f} ({model_percentage:5.1f}%)")
            print()

        # Print usage statistics
        print(f"Total API calls: {stats['total_api_calls']}")
        print(f"Total tokens:")
        print(f"  Input:       {stats['total_input_tokens']:>12,}")
        print(f"  Output:      {stats['total_output_tokens']:>12,}")
        print(f"  Cache write: {stats['total_cache_write_tokens']:>12,}")
        print(f"  Cache read:  {stats['total_cache_read_tokens']:>12,}")
        print()

        # Show status indicator
        print("=" * 50)
        if percentage >= 125:
            print("🚨 ALERT: Budget exceeded by 25% or more!")
            print("   Consider reducing usage immediately.")
        elif percentage >= 100:
            print("🚨 WARNING: Monthly budget exceeded!")
            print("   You've used more than your $15 limit.")
        elif percentage >= 90:
            print("⚠️  CAUTION: Approaching budget limit (90%+)")
            print("   Consider monitoring usage closely.")
        elif percentage >= 75:
            print("⚠️  NOTICE: 75% of budget used")
            print("   You may want to optimize usage.")
        elif percentage >= 50:
            print("ℹ️  INFO: 50% of budget used")
            print("   Spending on track.")
        else:
            print("✅ HEALTHY: Budget usage under control")
            print("   Continue normal usage.")

        print("=" * 50)
        print()

        # Print tips if over budget
        if percentage >= 100:
            print("💡 Tips to reduce costs:")
            print("  • Use /compact to reduce context size")
            print("  • Switch to Haiku for simpler tasks (/model haiku)")
            print("  • Break complex tasks into smaller steps")
            print("  • Clear history between unrelated tasks (/clear)")
            print()

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        print("\nPlease check:", file=sys.stderr)
        print("  • ~/.claude/projects/ directory exists", file=sys.stderr)
        print("  • You have permission to read .jsonl files", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
