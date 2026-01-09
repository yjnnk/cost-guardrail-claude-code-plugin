#!/usr/bin/env python3
"""
State manager module for tracking warning state and preventing duplicates.
Manages the state file that stores last shown warning level and timestamp.
"""

import json
import os
from datetime import datetime


# State file location
STATE_FILE = os.path.expanduser("~/.claude/cost_guardrails_state.json")


def load_state():
    """
    Load state from the state file.

    Returns:
        Dict with keys:
        - last_warning_level: Last warning level shown ("none", "50", "75", etc.)
        - last_warning_month: Last month warning was shown (YYYY-MM format)
        - last_cost_check: Last time cost was checked (ISO 8601 timestamp)
    """
    default_state = {
        "last_warning_level": "none",
        "last_warning_month": None,
        "last_cost_check": None
    }

    # Check if state file exists
    if not os.path.exists(STATE_FILE):
        return default_state

    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # Validate state has required keys
        if not isinstance(state, dict):
            return default_state

        # Ensure all keys exist
        for key in default_state.keys():
            if key not in state:
                state[key] = default_state[key]

        return state

    except (json.JSONDecodeError, IOError, PermissionError):
        # If file is corrupted or unreadable, return default
        return default_state
    except Exception:
        return default_state


def save_state(state):
    """
    Save state to the state file.

    Args:
        state: Dict with state information
    """
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except (IOError, PermissionError):
        # Fail silently if can't write
        pass
    except Exception:
        pass


def should_show_warning(current_level, current_month):
    """
    Determine if a warning should be shown to the user.

    Logic:
    - Show warning if level increased (e.g., 50% → 75%)
    - Show warning if new month (reset warnings)
    - Don't show if level is same or decreased

    Args:
        current_level: Current warning level ("none", "50", "75", "90", "100", "125")
        current_month: Current month string (YYYY-MM format)

    Returns:
        Boolean indicating whether to show warning
    """
    state = load_state()
    last_level = state.get("last_warning_level", "none")
    last_month = state.get("last_warning_month")

    # If new month, reset and show warning if over 50%
    if last_month != current_month:
        return current_level != "none"

    # Same month - only show if level increased
    level_hierarchy = ["none", "50", "75", "90", "100", "125"]

    try:
        current_idx = level_hierarchy.index(current_level)
    except ValueError:
        current_idx = 0

    try:
        last_idx = level_hierarchy.index(last_level)
    except ValueError:
        last_idx = 0

    # Show warning if we've moved to a higher level
    return current_idx > last_idx


def update_warning_shown(level, month):
    """
    Update state to reflect that a warning was shown.

    Args:
        level: Warning level that was shown
        month: Month string (YYYY-MM format)
    """
    state = load_state()
    state["last_warning_level"] = level
    state["last_warning_month"] = month
    state["last_cost_check"] = datetime.now().isoformat()
    save_state(state)


def update_cost_check():
    """
    Update the last cost check timestamp without changing warning level.
    Used for session end updates.
    """
    state = load_state()
    state["last_cost_check"] = datetime.now().isoformat()
    save_state(state)


def get_current_month_string():
    """
    Get the current month in YYYY-MM format.

    Returns:
        String in YYYY-MM format (e.g., "2026-01")
    """
    return datetime.now().strftime("%Y-%m")


def reset_state():
    """
    Reset state to default values.
    Useful for testing or manual resets.
    """
    default_state = {
        "last_warning_level": "none",
        "last_warning_month": None,
        "last_cost_check": None
    }
    save_state(default_state)


def get_state_summary():
    """
    Get a human-readable summary of the current state.

    Returns:
        String with state summary
    """
    state = load_state()

    lines = []
    lines.append("Cost Guardrails State:")
    lines.append(f"  Last warning level: {state.get('last_warning_level', 'none')}")
    lines.append(f"  Last warning month: {state.get('last_warning_month', 'never')}")

    last_check = state.get('last_cost_check')
    if last_check:
        lines.append(f"  Last cost check: {last_check}")
    else:
        lines.append("  Last cost check: never")

    return "\n".join(lines)
