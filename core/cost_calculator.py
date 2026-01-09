#!/usr/bin/env python3
"""
Cost calculator module for aggregating costs and determining warning levels.
"""

import os
import sys

# Add parent directory to path to import sibling modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pricing import calculate_message_cost, get_model_display_name
from core.usage_parser import get_current_month_usage


def calculate_total_cost(records):
    """
    Calculate total cost from a list of usage records.

    Args:
        records: List of usage records (each with 'model' and 'usage' keys)

    Returns:
        Total cost in dollars (float)
    """
    total = 0.0

    for record in records:
        model = record.get("model")
        usage = record.get("usage")

        if model and usage:
            cost = calculate_message_cost(model, usage)
            total += cost

    return total


def get_current_month_cost():
    """
    Get the total cost for the current calendar month.

    This is the main function for getting current spending.

    Returns:
        Cost in dollars (float)
    """
    records = get_current_month_usage()
    return calculate_total_cost(records)


def determine_warning_level(current_cost, budget_limit):
    """
    Determine what warning level should be shown based on spending.

    Warning levels:
    - "none": Below 50% of budget
    - "50": 50% or more of budget used
    - "75": 75% or more of budget used
    - "90": 90% or more of budget used
    - "100": 100% or more of budget used (over budget)
    - "125": 125% or more of budget used (significantly over)

    Args:
        current_cost: Current spending in dollars (float)
        budget_limit: Monthly budget limit in dollars (float)

    Returns:
        Tuple of (warning_level, percentage_used)
        - warning_level: String ("none", "50", "75", "90", "100", "125")
        - percentage_used: Float (0-100+)
    """
    if budget_limit <= 0:
        return "none", 0.0

    percentage = (current_cost / budget_limit) * 100

    # Determine level based on percentage
    if percentage >= 125:
        return "125", percentage
    elif percentage >= 100:
        return "100", percentage
    elif percentage >= 90:
        return "90", percentage
    elif percentage >= 75:
        return "75", percentage
    elif percentage >= 50:
        return "50", percentage
    else:
        return "none", percentage


def get_cost_breakdown(records):
    """
    Get cost breakdown by model.

    Args:
        records: List of usage records

    Returns:
        Dict mapping model display names to costs
        Example: {"Sonnet": 10.50, "Haiku": 2.30}
    """
    breakdown = {}

    for record in records:
        model = record.get("model")
        usage = record.get("usage")

        if model and usage:
            cost = calculate_message_cost(model, usage)
            display_name = get_model_display_name(model)

            if display_name in breakdown:
                breakdown[display_name] += cost
            else:
                breakdown[display_name] = cost

    return breakdown


def get_usage_stats(records):
    """
    Get usage statistics from records.

    Args:
        records: List of usage records

    Returns:
        Dict with statistics:
        - total_api_calls: Number of API calls
        - total_input_tokens: Total input tokens
        - total_output_tokens: Total output tokens
        - total_cache_write_tokens: Total cache write tokens
        - total_cache_read_tokens: Total cache read tokens
    """
    stats = {
        "total_api_calls": len(records),
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cache_write_tokens": 0,
        "total_cache_read_tokens": 0
    }

    for record in records:
        usage = record.get("usage", {})
        stats["total_input_tokens"] += usage.get("input_tokens", 0)
        stats["total_output_tokens"] += usage.get("output_tokens", 0)
        stats["total_cache_write_tokens"] += usage.get("cache_creation_input_tokens", 0)
        stats["total_cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)

    return stats


def format_warning_message(level, current_cost, budget, breakdown):
    """
    Format a warning message for the user.

    Args:
        level: Warning level ("50", "75", "90", "100", "125")
        current_cost: Current spending in dollars
        budget: Budget limit in dollars
        breakdown: Cost breakdown by model (dict)

    Returns:
        Formatted string message
    """
    percentage = (current_cost / budget) * 100 if budget > 0 else 0
    remaining = budget - current_cost

    # Emoji and message based on severity
    emoji = {
        "50": "ℹ️",
        "75": "⚠️",
        "90": "⚠️",
        "100": "🚨",
        "125": "🚨"
    }

    messages = {
        "50": "You've used 50% of your monthly budget",
        "75": "You've used 75% of your monthly budget",
        "90": "You're approaching your monthly budget limit (90% used)",
        "100": "You've reached your $15 monthly budget",
        "125": "You've exceeded your monthly budget by 25%"
    }

    # Build message
    lines = []
    lines.append(f"{emoji.get(level, 'ℹ️')} Cost Guardrails: {messages.get(level, 'Budget check')}")
    lines.append("")
    lines.append(f"Current spending: ${current_cost:.2f} / ${budget:.2f} ({percentage:.1f}%)")
    lines.append(f"Remaining: ${remaining:.2f}")
    lines.append("")

    # Add breakdown if available
    if breakdown:
        lines.append("Breakdown by model:")
        for model_name in sorted(breakdown.keys()):
            cost = breakdown[model_name]
            lines.append(f"  - {model_name}: ${cost:.2f}")
        lines.append("")

    # Add suggestions if over budget
    if level in ["100", "125"]:
        lines.append("Consider:")
        lines.append("  - Using /compact to reduce context size")
        lines.append("  - Switching to Haiku for simpler tasks (/model haiku)")
        lines.append("  - Breaking complex tasks into smaller steps")

    return "\n".join(lines)


def format_summary_message(current_cost, budget):
    """
    Format a brief summary message for session end.

    Args:
        current_cost: Current spending in dollars
        budget: Budget limit in dollars

    Returns:
        Formatted string message
    """
    remaining = budget - current_cost
    percentage = (current_cost / budget) * 100 if budget > 0 else 0

    if percentage >= 100:
        return f"🚨 Monthly spending: ${current_cost:.2f} / ${budget:.2f} (OVER BUDGET by ${-remaining:.2f})"
    elif percentage >= 90:
        return f"⚠️  Monthly spending: ${current_cost:.2f} / ${budget:.2f} (${remaining:.2f} remaining)"
    else:
        return f"Monthly spending: ${current_cost:.2f} / ${budget:.2f} (${remaining:.2f} remaining)"
