#!/usr/bin/env python3
"""
Pricing module for Claude Code cost calculations.
Contains pricing constants and cost calculation functions.
"""

# Pricing per MTok (million tokens) as of January 2025
PRICING = {
    "claude-sonnet-4-5-20250929": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30
    },
    "claude-haiku-4-5-20251001": {
        "input": 0.80,
        "output": 4.00,
        "cache_write": 1.00,
        "cache_read": 0.08
    }
}

# Model aliases for normalization
MODEL_ALIASES = {
    "claude-sonnet": "claude-sonnet-4-5-20250929",
    "claude-haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-5-20250929",
    "haiku": "claude-haiku-4-5-20251001"
}


def normalize_model_name(model):
    """
    Normalize model name to full model ID.

    Args:
        model: Model name or ID

    Returns:
        Normalized model ID
    """
    if not model:
        return "claude-sonnet-4-5-20250929"  # Default to Sonnet

    # Check if it's already a full model ID
    if model in PRICING:
        return model

    # Check aliases
    model_lower = model.lower()
    if model_lower in MODEL_ALIASES:
        return MODEL_ALIASES[model_lower]

    # Check if model name contains sonnet or haiku
    if "sonnet" in model_lower:
        return "claude-sonnet-4-5-20250929"
    elif "haiku" in model_lower:
        return "claude-haiku-4-5-20251001"

    # Default to Sonnet (conservative, higher cost estimate)
    return "claude-sonnet-4-5-20250929"


def calculate_message_cost(model, usage):
    """
    Calculate cost for a single message based on token usage.

    Args:
        model: Model ID (e.g., "claude-sonnet-4-5-20250929")
        usage: Dict with keys:
            - input_tokens: Regular input tokens
            - output_tokens: Output tokens
            - cache_creation_input_tokens: Tokens written to cache
            - cache_read_input_tokens: Tokens read from cache

    Returns:
        Cost in dollars (float)
    """
    # Normalize model name
    normalized_model = normalize_model_name(model)

    # Get pricing for this model
    pricing = PRICING.get(normalized_model)
    if not pricing:
        # Fallback to Sonnet pricing if unknown
        pricing = PRICING["claude-sonnet-4-5-20250929"]

    # Calculate cost for each token type
    cost = 0.0

    # Regular input tokens
    input_tokens = usage.get("input_tokens", 0)
    cost += (input_tokens / 1_000_000) * pricing["input"]

    # Output tokens
    output_tokens = usage.get("output_tokens", 0)
    cost += (output_tokens / 1_000_000) * pricing["output"]

    # Cache write tokens (creating cache)
    cache_write_tokens = usage.get("cache_creation_input_tokens", 0)
    cost += (cache_write_tokens / 1_000_000) * pricing["cache_write"]

    # Cache read tokens (reading from cache)
    cache_read_tokens = usage.get("cache_read_input_tokens", 0)
    cost += (cache_read_tokens / 1_000_000) * pricing["cache_read"]

    return cost


def get_model_display_name(model):
    """
    Get a friendly display name for a model.

    Args:
        model: Model ID

    Returns:
        Display name (e.g., "Sonnet", "Haiku")
    """
    normalized = normalize_model_name(model)

    if "sonnet" in normalized.lower():
        return "Sonnet"
    elif "haiku" in normalized.lower():
        return "Haiku"
    else:
        return "Unknown"


def format_cost(cost):
    """
    Format cost as a currency string.

    Args:
        cost: Cost in dollars (float)

    Returns:
        Formatted string (e.g., "$12.34")
    """
    return f"${cost:.2f}"
