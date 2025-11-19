"""
Validation Utilities

Helper functions for validating legal data.
"""

import re
from typing import Optional, Tuple


def validate_case_number(case_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a case number format.

    Args:
        case_number: The case number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not case_number:
        return False, "Case number is required"

    # Remove whitespace
    case_number = case_number.strip()

    if len(case_number) < 3:
        return False, "Case number too short"

    if len(case_number) > 50:
        return False, "Case number too long"

    # Common case number patterns
    patterns = [
        r'^[A-Z]{1,3}-\d{2,4}-\d+$',  # e.g., CR-2023-12345
        r'^\d{2,4}-[A-Z]{1,3}-\d+$',  # e.g., 2023-CV-12345
        r'^[A-Z]+\d+$',                # e.g., CF123456
        r'^\d+$',                       # Numeric only
    ]

    for pattern in patterns:
        if re.match(pattern, case_number, re.IGNORECASE):
            return True, None

    # Allow if it contains some alphanumeric characters
    if re.match(r'^[A-Z0-9\-:]+$', case_number, re.IGNORECASE):
        return True, None

    return False, "Invalid case number format"


def validate_bar_number(bar_number: str, jurisdiction: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate an attorney bar number.

    Args:
        bar_number: The bar number to validate
        jurisdiction: Optional jurisdiction for specific rules

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not bar_number:
        return False, "Bar number is required"

    bar_number = bar_number.strip()

    if len(bar_number) < 2:
        return False, "Bar number too short"

    if len(bar_number) > 20:
        return False, "Bar number too long"

    # Jurisdiction-specific validation
    if jurisdiction:
        jurisdiction = jurisdiction.upper()

        # California bar numbers are numeric
        if jurisdiction == "CA":
            if not bar_number.isdigit():
                return False, "California bar numbers must be numeric"
            if len(bar_number) > 7:
                return False, "California bar numbers have at most 7 digits"

        # New York bar numbers are numeric
        elif jurisdiction == "NY":
            if not bar_number.isdigit():
                return False, "New York bar numbers must be numeric"

    # General validation - alphanumeric
    if not re.match(r'^[A-Z0-9]+$', bar_number, re.IGNORECASE):
        return False, "Bar number must be alphanumeric"

    return True, None


def validate_statute_code(statute_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a statute code format.

    Args:
        statute_code: The statute code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not statute_code:
        return False, "Statute code is required"

    statute_code = statute_code.strip()

    if len(statute_code) < 2:
        return False, "Statute code too short"

    if len(statute_code) > 50:
        return False, "Statute code too long"

    # Common patterns
    patterns = [
        r'^\d+\.\d+$',                    # e.g., 18.2
        r'^\d+-\d+-\d+$',                 # e.g., 720-5-8
        r'^[A-Z]+\s+\d+\.\d+$',           # e.g., PC 187.5
        r'^[A-Z]+\s+\d+$',                # e.g., USC 18
        r'^\d+\s+[A-Z]+\s+\d+$',          # e.g., 18 USC 1001
        r'^[A-Z]+\.\s*[A-Z]+\.\s*\d+',    # e.g., Cal. Pen. Code 187
    ]

    for pattern in patterns:
        if re.match(pattern, statute_code, re.IGNORECASE):
            return True, None

    # Allow basic alphanumeric with common separators
    if re.match(r'^[A-Z0-9\s\.\-:§]+$', statute_code, re.IGNORECASE):
        return True, None

    return False, "Invalid statute code format"


def validate_citation(citation: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a legal citation format.

    Args:
        citation: The citation to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not citation:
        return False, "Citation is required"

    citation = citation.strip()

    if len(citation) < 5:
        return False, "Citation too short"

    if len(citation) > 200:
        return False, "Citation too long"

    # Check for basic citation structure
    # Should contain volume number and page number
    if not re.search(r'\d+', citation):
        return False, "Citation must contain numbers"

    # Should contain reporter abbreviation
    reporters = [
        'U.S.', 'S.Ct.', 'L.Ed.', 'F.', 'F.2d', 'F.3d', 'F.4th',
        'Cal.', 'N.Y.', 'Tex.', 'Ill.', 'Pa.', 'Ohio', 'Fla.',
        'A.', 'A.2d', 'A.3d', 'N.E.', 'N.E.2d', 'N.E.3d',
        'N.W.', 'N.W.2d', 'P.', 'P.2d', 'P.3d', 'S.E.', 'S.E.2d',
        'S.W.', 'S.W.2d', 'S.W.3d', 'So.', 'So.2d', 'So.3d'
    ]

    has_reporter = any(r.lower() in citation.lower() for r in reporters)
    if not has_reporter:
        # Allow if it looks like a citation (has numbers and parentheses)
        if not re.search(r'\d+.*\(\d{4}\)', citation):
            return False, "Citation should include a reporter abbreviation"

    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address.

    Args:
        email: The email to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    email = email.strip()

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        return True, None

    return False, "Invalid email format"


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a phone number.

    Args:
        phone: The phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"

    # Remove common formatting
    digits = re.sub(r'[\s\-\.\(\)]+', '', phone)

    if not digits.isdigit():
        return False, "Phone number must contain only digits"

    if len(digits) < 10:
        return False, "Phone number too short"

    if len(digits) > 15:
        return False, "Phone number too long"

    return True, None
