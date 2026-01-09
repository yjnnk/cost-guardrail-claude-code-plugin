#!/usr/bin/env python3
"""
Usage parser module for extracting token usage from Claude Code logs.
Parses JSONL files in ~/.claude/projects/ to extract usage data.
"""

import json
import glob
import os
from datetime import datetime
from pathlib import Path


def find_all_jsonl_files(base_path="~/.claude/projects"):
    """
    Recursively find all .jsonl files in the projects directory.

    Args:
        base_path: Base directory to search (default: ~/.claude/projects)

    Returns:
        List of absolute file paths to .jsonl files
    """
    expanded_path = os.path.expanduser(base_path)

    # Check if directory exists
    if not os.path.exists(expanded_path):
        return []

    # Find all .jsonl files recursively
    pattern = os.path.join(expanded_path, "**", "*.jsonl")
    return glob.glob(pattern, recursive=True)


def parse_jsonl_file(file_path):
    """
    Parse a single JSONL file and extract usage records.

    Each line in the JSONL file is a JSON object. We look for objects
    with message.usage data and extract relevant information.

    Args:
        file_path: Path to the .jsonl file

    Returns:
        List of usage records, each dict with:
            - timestamp: ISO 8601 timestamp string
            - model: Model ID
            - usage: Dict with token counts
            - session_id: Session ID (if available)
    """
    records = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                try:
                    entry = json.loads(line)

                    # Extract message data
                    message = entry.get("message", {})
                    usage = message.get("usage")

                    # Only include entries with usage data
                    if usage:
                        record = {
                            "timestamp": entry.get("timestamp"),
                            "model": message.get("model"),
                            "usage": usage,
                            "session_id": entry.get("sessionId"),
                            "file_path": file_path,
                            "line_number": line_num
                        }
                        records.append(record)

                except json.JSONDecodeError as e:
                    # Skip malformed JSON lines
                    continue
                except Exception as e:
                    # Skip lines with other errors
                    continue

    except (IOError, FileNotFoundError, PermissionError):
        # Skip files that can't be read
        pass
    except Exception:
        # Skip any other errors
        pass

    return records


def parse_timestamp(timestamp_str):
    """
    Parse ISO 8601 timestamp string to datetime object.

    Args:
        timestamp_str: ISO 8601 timestamp string

    Returns:
        datetime object or None if parsing fails
    """
    if not timestamp_str:
        return None

    try:
        # Handle both with and without 'Z' suffix
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'

        # Parse ISO 8601 format
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, AttributeError):
        return None


def filter_records_by_month(records, year, month):
    """
    Filter usage records to a specific calendar month.

    Args:
        records: List of usage records
        year: Year (int)
        month: Month (int, 1-12)

    Returns:
        Filtered list of records from the specified month
    """
    filtered = []

    for record in records:
        timestamp_str = record.get("timestamp")
        dt = parse_timestamp(timestamp_str)

        if dt and dt.year == year and dt.month == month:
            filtered.append(record)

    return filtered


def get_current_month_usage():
    """
    Get all usage records for the current calendar month.

    This is the main function to call for getting current month's data.
    It finds all JSONL files, parses them, and filters to current month.

    Returns:
        List of usage records for the current month
    """
    # Get current year and month
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Find all JSONL files
    all_files = find_all_jsonl_files()

    # Parse all files and collect records
    all_records = []
    for file_path in all_files:
        records = parse_jsonl_file(file_path)
        all_records.extend(records)

    # Filter to current month
    current_month_records = filter_records_by_month(
        all_records, current_year, current_month
    )

    return current_month_records


def get_usage_for_month(year, month):
    """
    Get all usage records for a specific calendar month.

    Args:
        year: Year (int)
        month: Month (int, 1-12)

    Returns:
        List of usage records for the specified month
    """
    # Find all JSONL files
    all_files = find_all_jsonl_files()

    # Parse all files and collect records
    all_records = []
    for file_path in all_files:
        records = parse_jsonl_file(file_path)
        all_records.extend(records)

    # Filter to specified month
    month_records = filter_records_by_month(all_records, year, month)

    return month_records


def get_all_usage():
    """
    Get all usage records from all JSONL files.

    Returns:
        List of all usage records
    """
    all_files = find_all_jsonl_files()

    all_records = []
    for file_path in all_files:
        records = parse_jsonl_file(file_path)
        all_records.extend(records)

    return all_records
