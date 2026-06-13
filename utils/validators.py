"""
validators.py - Input validation utilities.

Centralises all validation logic so CLI handlers stay clean.
"""

import re
from datetime import datetime


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> str:
    """
    Validate an email address format.

    Args:
        email (str): Email string to validate.

    Returns:
        str: The validated email (stripped).

    Raises:
        ValueError: If the email does not match basic RFC format.
    """
    stripped = email.strip()
    if not EMAIL_RE.match(stripped):
        raise ValueError(f"'{stripped}' is not a valid email address.")
    return stripped


def validate_date(date_str: str) -> str:
    """
    Validate a date string in YYYY-MM-DD format.

    Args:
        date_str (str): Date string to validate.

    Returns:
        str: The validated date string.

    Raises:
        ValueError: If the format is wrong.
    """
    stripped = date_str.strip()
    try:
        datetime.strptime(stripped, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Date '{stripped}' must be in YYYY-MM-DD format.")
    return stripped


def validate_non_empty(value: str, field_name: str = "value") -> str:
    """
    Ensure a string is not empty after stripping whitespace.

    Args:
        value (str): Input string.
        field_name (str): Human-readable field name for the error message.

    Returns:
        str: Stripped, non-empty string.

    Raises:
        ValueError: If the string is blank.
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} cannot be empty.")
    return stripped
