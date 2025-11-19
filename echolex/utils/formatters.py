"""
Formatting Utilities

Helper functions for formatting legal data.
"""

from datetime import timedelta
from typing import Optional


def format_case_number(case_number: str, jurisdiction: str = None) -> str:
    """
    Format a case number for display.

    Args:
        case_number: The raw case number
        jurisdiction: Optional jurisdiction code

    Returns:
        Formatted case number
    """
    # Clean up the case number
    formatted = case_number.strip().upper()

    if jurisdiction:
        return f"{jurisdiction}: {formatted}"

    return formatted


def format_citation(
    case_name: str,
    volume: int,
    reporter: str,
    page: int,
    year: int,
    court: str = None
) -> str:
    """
    Format a legal citation in Bluebook style.

    Args:
        case_name: Name of the case
        volume: Reporter volume
        reporter: Reporter abbreviation
        page: Starting page
        year: Decision year
        court: Optional court name

    Returns:
        Formatted citation string

    Example:
        >>> format_citation("Miranda v. Arizona", 384, "U.S.", 436, 1966)
        "Miranda v. Arizona, 384 U.S. 436 (1966)"
    """
    citation = f"{case_name}, {volume} {reporter} {page}"

    if court:
        citation += f" ({court} {year})"
    else:
        citation += f" ({year})"

    return citation


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format a currency amount.

    Args:
        amount: The amount
        currency: Currency code

    Returns:
        Formatted currency string
    """
    if currency == "USD":
        if amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.1f}K"
        else:
            return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_duration(
    months: float = 0,
    days: float = 0,
    hours: float = 0,
    short: bool = False
) -> str:
    """
    Format a duration for display.

    Args:
        months: Number of months
        days: Number of days
        hours: Number of hours
        short: Use short format

    Returns:
        Formatted duration string
    """
    parts = []

    if months > 0:
        years = int(months // 12)
        remaining_months = int(months % 12)

        if years > 0:
            if short:
                parts.append(f"{years}y")
            else:
                parts.append(f"{years} year{'s' if years != 1 else ''}")

        if remaining_months > 0:
            if short:
                parts.append(f"{remaining_months}m")
            else:
                parts.append(f"{remaining_months} month{'s' if remaining_months != 1 else ''}")

    if days > 0:
        days = int(days)
        if short:
            parts.append(f"{days}d")
        else:
            parts.append(f"{days} day{'s' if days != 1 else ''}")

    if hours > 0:
        hours = int(hours)
        if short:
            parts.append(f"{hours}h")
        else:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    if not parts:
        return "0 days" if not short else "0d"

    return " ".join(parts) if not short else " ".join(parts)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a value as a percentage.

    Args:
        value: The value (0.0 to 1.0)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_sentence_summary(
    incarceration_months: int = 0,
    probation_months: int = 0,
    fine_amount: float = 0,
    community_service_hours: int = 0
) -> str:
    """
    Format a sentence summary.

    Args:
        incarceration_months: Months of incarceration
        probation_months: Months of probation
        fine_amount: Fine amount
        community_service_hours: Community service hours

    Returns:
        Formatted sentence summary
    """
    parts = []

    if incarceration_months > 0:
        parts.append(format_duration(months=incarceration_months) + " incarceration")

    if probation_months > 0:
        parts.append(format_duration(months=probation_months) + " probation")

    if fine_amount > 0:
        parts.append(f"{format_currency(fine_amount)} fine")

    if community_service_hours > 0:
        parts.append(f"{community_service_hours} hours community service")

    if not parts:
        return "No sentence"

    return ", ".join(parts)
