"""Credit report parser for PDF and text files."""

import re
from pathlib import Path
from typing import Optional
from datetime import datetime
import pdfplumber
from PyPDF2 import PdfReader


class CreditReportParser:
    """Parse credit reports from major bureaus."""

    def __init__(self):
        self.supported_bureaus = ["experian", "equifax", "transunion"]

    def parse_file(self, file_path: str) -> dict:
        """Parse a credit report file and extract key information."""
        path = Path(file_path)

        if path.suffix.lower() == ".pdf":
            text = self._extract_pdf_text(file_path)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        return self._parse_report_text(text)

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""

        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            pass

        # Fallback to PyPDF2
        if not text:
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception:
                pass

        return text

    def _parse_report_text(self, text: str) -> dict:
        """Parse the extracted text to identify credit report elements."""
        result = {
            "bureau": self._detect_bureau(text),
            "credit_score": self._extract_credit_score(text),
            "score_factors": self._extract_score_factors(text),
            "accounts": self._extract_accounts(text),
            "inquiries": self._extract_inquiries(text),
            "public_records": self._extract_public_records(text),
            "collections": self._extract_collections(text),
            "personal_info": self._extract_personal_info(text),
            "summary": self._generate_summary(text),
            "negative_items": [],
            "improvement_opportunities": [],
        }

        # Analyze and identify issues
        result["negative_items"] = self._identify_negative_items(result)
        result["improvement_opportunities"] = self._identify_improvements(result)

        return result

    def _detect_bureau(self, text: str) -> str:
        """Detect which credit bureau the report is from."""
        text_lower = text.lower()

        if "experian" in text_lower:
            return "Experian"
        elif "equifax" in text_lower:
            return "Equifax"
        elif "transunion" in text_lower:
            return "TransUnion"
        else:
            return "Unknown"

    def _extract_credit_score(self, text: str) -> Optional[int]:
        """Extract credit score from report."""
        # Common patterns for credit scores
        patterns = [
            r"(?:credit\s*score|fico\s*score|vantage\s*score)[:\s]*(\d{3})",
            r"(?:your\s*score)[:\s]*(\d{3})",
            r"(?:score)[:\s]*(\d{3})",
            r"\b([3-8]\d{2})\b(?:\s*(?:fico|vantage|credit))?",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 300 <= score <= 850:
                    return score

        return None

    def _extract_score_factors(self, text: str) -> list:
        """Extract factors affecting credit score."""
        factors = []

        # Common negative factors
        negative_patterns = {
            "high_utilization": r"(?:high\s*(?:credit\s*)?utilization|utilization\s*(?:is\s*)?(?:too\s*)?high)",
            "late_payments": r"(?:late\s*payment|payment\s*(?:was\s*)?late|delinquent\s*payment)",
            "collections": r"(?:collection\s*account|account\s*in\s*collection)",
            "short_history": r"(?:short\s*credit\s*history|limited\s*credit\s*history)",
            "too_many_inquiries": r"(?:too\s*many\s*inquiries|multiple\s*inquiries)",
            "high_balances": r"(?:high\s*balance|balance\s*(?:is\s*)?(?:too\s*)?high)",
            "few_accounts": r"(?:few\s*accounts|limited\s*(?:number\s*of\s*)?accounts)",
        }

        for factor_name, pattern in negative_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                factors.append({
                    "type": factor_name,
                    "impact": "negative",
                    "description": self._get_factor_description(factor_name)
                })

        return factors

    def _get_factor_description(self, factor: str) -> str:
        """Get description for a credit factor."""
        descriptions = {
            "high_utilization": "Credit utilization ratio is too high. Aim for under 30%.",
            "late_payments": "Late payments negatively impact your score. Set up autopay.",
            "collections": "Collection accounts severely damage credit. Consider pay-for-delete.",
            "short_history": "Credit history length is limited. Keep old accounts open.",
            "too_many_inquiries": "Multiple hard inquiries can lower score temporarily.",
            "high_balances": "High balances relative to limits hurt your score.",
            "few_accounts": "Limited credit mix. Consider diversifying account types.",
        }
        return descriptions.get(factor, "Factor affecting your credit score.")

    def _extract_accounts(self, text: str) -> list:
        """Extract account information from report."""
        accounts = []

        # Pattern to find account blocks
        account_patterns = [
            # Creditor name followed by account details
            r"([A-Z][A-Z\s&\-\.]+(?:BANK|CARD|AUTO|MORTGAGE|LOAN|CREDIT|FINANCIAL))\s*"
            r"(?:Account\s*#?:?\s*)?([X\d\-]+)?\s*"
            r"(?:Balance[:\s]*\$?([\d,]+))?\s*"
            r"(?:Limit[:\s]*\$?([\d,]+))?\s*"
            r"(?:Status[:\s]*)?([\w\s]+)?",
        ]

        for pattern in account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                account = {
                    "creditor": match[0].strip() if match[0] else "Unknown",
                    "account_number": match[1] if len(match) > 1 and match[1] else "N/A",
                    "balance": self._parse_amount(match[2]) if len(match) > 2 else 0,
                    "credit_limit": self._parse_amount(match[3]) if len(match) > 3 else 0,
                    "status": match[4].strip() if len(match) > 4 and match[4] else "Unknown",
                }
                if account["creditor"] != "Unknown":
                    accounts.append(account)

        return accounts

    def _extract_inquiries(self, text: str) -> list:
        """Extract credit inquiries from report."""
        inquiries = []

        # Look for inquiry section
        inquiry_section = re.search(
            r"(?:inquiries|credit\s*checks)(.*?)(?:public\s*records|accounts|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if inquiry_section:
            section_text = inquiry_section.group(1)
            # Find company names and dates
            matches = re.findall(
                r"([A-Z][A-Za-z\s&\-\.]+)\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})?",
                section_text
            )
            for match in matches[:20]:  # Limit to prevent false positives
                if len(match[0].strip()) > 3:
                    inquiries.append({
                        "company": match[0].strip(),
                        "date": match[1] if match[1] else "Unknown"
                    })

        return inquiries

    def _extract_public_records(self, text: str) -> list:
        """Extract public records (bankruptcies, liens, judgments)."""
        records = []

        # Bankruptcy patterns
        if re.search(r"bankruptcy", text, re.IGNORECASE):
            bankruptcy_match = re.search(
                r"(chapter\s*\d+)\s*bankruptcy.*?(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})?",
                text,
                re.IGNORECASE
            )
            if bankruptcy_match:
                records.append({
                    "type": "Bankruptcy",
                    "details": bankruptcy_match.group(1),
                    "date": bankruptcy_match.group(2) if bankruptcy_match.group(2) else "Unknown"
                })

        # Tax liens
        if re.search(r"tax\s*lien", text, re.IGNORECASE):
            records.append({
                "type": "Tax Lien",
                "details": "Tax lien found on record",
                "date": "Unknown"
            })

        # Judgments
        if re.search(r"judgment|civil\s*judgment", text, re.IGNORECASE):
            records.append({
                "type": "Judgment",
                "details": "Civil judgment found on record",
                "date": "Unknown"
            })

        return records

    def _extract_collections(self, text: str) -> list:
        """Extract collection accounts."""
        collections = []

        # Collection account patterns
        collection_matches = re.findall(
            r"(?:collection|collections|coll)\s*(?:agency)?[:\s]*"
            r"([A-Za-z\s&\-\.]+)\s*"
            r"(?:\$?([\d,]+))?",
            text,
            re.IGNORECASE
        )

        for match in collection_matches:
            if match[0].strip():
                collections.append({
                    "agency": match[0].strip(),
                    "amount": self._parse_amount(match[1]) if match[1] else 0
                })

        return collections

    def _extract_personal_info(self, text: str) -> dict:
        """Extract personal information from report."""
        info = {}

        # Name
        name_match = re.search(r"(?:name|consumer)[:\s]*([A-Za-z\s]+)", text, re.IGNORECASE)
        if name_match:
            info["name"] = name_match.group(1).strip()

        # Address
        address_match = re.search(
            r"(?:address)[:\s]*([A-Za-z0-9\s,\.]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln))",
            text,
            re.IGNORECASE
        )
        if address_match:
            info["address"] = address_match.group(1).strip()

        return info

    def _generate_summary(self, text: str) -> dict:
        """Generate a summary of the credit report."""
        # Count accounts
        total_accounts = len(re.findall(r"account", text, re.IGNORECASE))
        open_accounts = len(re.findall(r"(?:open|active)\s*account", text, re.IGNORECASE))

        # Count negatives
        late_payments = len(re.findall(r"late\s*payment|past\s*due", text, re.IGNORECASE))
        collections = len(re.findall(r"collection", text, re.IGNORECASE))

        return {
            "estimated_accounts": min(total_accounts // 5, 30),  # Rough estimate
            "open_accounts": open_accounts,
            "late_payments": late_payments,
            "collections": collections,
            "has_public_records": bool(re.search(r"bankruptcy|lien|judgment", text, re.IGNORECASE))
        }

    def _identify_negative_items(self, parsed_data: dict) -> list:
        """Identify negative items that can be disputed or improved."""
        negative_items = []

        # Check collections
        for collection in parsed_data.get("collections", []):
            negative_items.append({
                "type": "Collection",
                "creditor": collection.get("agency", "Unknown"),
                "amount": collection.get("amount", 0),
                "impact": "high",
                "disputable": True,
                "dispute_reasons": [
                    "Debt validation request",
                    "Statute of limitations expired",
                    "Inaccurate reporting",
                    "Not my account",
                    "Paid but not updated"
                ]
            })

        # Check public records
        for record in parsed_data.get("public_records", []):
            negative_items.append({
                "type": record.get("type", "Public Record"),
                "details": record.get("details", ""),
                "impact": "severe",
                "disputable": True,
                "dispute_reasons": [
                    "Inaccurate information",
                    "Should have been removed (time-barred)",
                    "Discharged in bankruptcy"
                ]
            })

        # Check score factors
        for factor in parsed_data.get("score_factors", []):
            if factor.get("impact") == "negative":
                negative_items.append({
                    "type": "Score Factor",
                    "details": factor.get("type", ""),
                    "description": factor.get("description", ""),
                    "impact": "medium",
                    "disputable": False,
                    "improvement_action": self._get_improvement_action(factor.get("type", ""))
                })

        return negative_items

    def _identify_improvements(self, parsed_data: dict) -> list:
        """Identify opportunities for credit improvement."""
        opportunities = []

        score = parsed_data.get("credit_score")
        if score:
            if score < 580:
                opportunities.append({
                    "priority": 1,
                    "action": "Address Collections",
                    "description": "Focus on removing or settling collection accounts first.",
                    "potential_impact": "50-100 points"
                })
            elif score < 670:
                opportunities.append({
                    "priority": 1,
                    "action": "Reduce Credit Utilization",
                    "description": "Pay down credit card balances to under 30% of limits.",
                    "potential_impact": "20-50 points"
                })
            elif score < 740:
                opportunities.append({
                    "priority": 1,
                    "action": "Maintain Payment History",
                    "description": "Continue on-time payments and consider authorized user status.",
                    "potential_impact": "10-30 points"
                })
            else:
                opportunities.append({
                    "priority": 1,
                    "action": "Optimize Credit Mix",
                    "description": "Consider adding different types of credit accounts.",
                    "potential_impact": "5-15 points"
                })

        # General opportunities
        opportunities.extend([
            {
                "priority": 2,
                "action": "Dispute Inaccurate Items",
                "description": "Review all negative items and dispute any inaccuracies.",
                "potential_impact": "Varies by item"
            },
            {
                "priority": 3,
                "action": "Request Goodwill Deletions",
                "description": "Contact creditors to request removal of late payments.",
                "potential_impact": "10-30 points per item"
            },
            {
                "priority": 4,
                "action": "Become Authorized User",
                "description": "Get added to a family member's old, good-standing account.",
                "potential_impact": "10-50 points"
            }
        ])

        return opportunities

    def _get_improvement_action(self, factor_type: str) -> str:
        """Get improvement action for a specific factor."""
        actions = {
            "high_utilization": "Pay down balances to under 30% of credit limits",
            "late_payments": "Set up automatic payments to avoid future late payments",
            "collections": "Negotiate pay-for-delete or dispute inaccurate collections",
            "short_history": "Keep old accounts open and active",
            "too_many_inquiries": "Limit new credit applications for 6-12 months",
            "high_balances": "Create a debt payoff plan using avalanche or snowball method",
            "few_accounts": "Consider a secured card or credit-builder loan",
        }
        return actions.get(factor_type, "Review and address this factor")

    def _parse_amount(self, amount_str: str) -> float:
        """Parse a dollar amount string to float."""
        if not amount_str:
            return 0.0
        try:
            cleaned = re.sub(r"[^\d.]", "", amount_str)
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
