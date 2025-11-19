"""Legal knowledge base for credit laws - US and International."""


class LegalKnowledgeBase:
    """Comprehensive legal knowledge for credit repair and financial rights."""

    def __init__(self):
        self.us_laws = self._load_us_laws()
        self.international_laws = self._load_international_laws()
        self.dispute_templates = self._load_dispute_templates()

    def _load_us_laws(self) -> dict:
        """Load US credit and consumer protection laws."""
        return {
            "FCRA": {
                "name": "Fair Credit Reporting Act",
                "code": "15 U.S.C. § 1681",
                "overview": "The FCRA promotes accuracy, fairness, and privacy of consumer information in credit reports.",
                "key_provisions": {
                    "Section 609": {
                        "title": "Disclosures to Consumers",
                        "description": "You have the right to obtain all information in your credit file.",
                        "citation": "15 U.S.C. § 1681g",
                        "use_case": "Request full disclosure of your credit file"
                    },
                    "Section 611": {
                        "title": "Procedure in Case of Disputed Accuracy",
                        "description": "Credit bureaus must investigate disputed items within 30 days.",
                        "citation": "15 U.S.C. § 1681i",
                        "use_case": "Dispute inaccurate information on your credit report"
                    },
                    "Section 623": {
                        "title": "Responsibilities of Furnishers",
                        "description": "Data furnishers must report accurate information and investigate disputes.",
                        "citation": "15 U.S.C. § 1681s-2",
                        "use_case": "Hold creditors accountable for inaccurate reporting"
                    },
                    "Section 605": {
                        "title": "Time Limits on Reporting",
                        "description": "Most negative items must be removed after 7 years (10 for bankruptcy).",
                        "citation": "15 U.S.C. § 1681c",
                        "use_case": "Request removal of time-barred information"
                    },
                    "Section 604": {
                        "title": "Permissible Purposes",
                        "description": "Credit reports can only be accessed for specific legitimate purposes.",
                        "citation": "15 U.S.C. § 1681b",
                        "use_case": "Challenge unauthorized credit inquiries"
                    },
                    "Section 616": {
                        "title": "Civil Liability - Willful Noncompliance",
                        "description": "Statutory damages of $100-$1,000 plus actual damages for willful violations.",
                        "citation": "15 U.S.C. § 1681n",
                        "use_case": "Sue for damages when your rights are violated"
                    },
                    "Section 617": {
                        "title": "Civil Liability - Negligent Noncompliance",
                        "description": "Actual damages plus attorney fees for negligent violations.",
                        "citation": "15 U.S.C. § 1681o",
                        "use_case": "Recover damages for negligent credit reporting"
                    }
                }
            },
            "FDCPA": {
                "name": "Fair Debt Collection Practices Act",
                "code": "15 U.S.C. § 1692",
                "overview": "The FDCPA prohibits abusive debt collection practices.",
                "key_provisions": {
                    "Section 805": {
                        "title": "Communication in Connection with Debt Collection",
                        "description": "Restrictions on when and how collectors can contact you.",
                        "citation": "15 U.S.C. § 1692c",
                        "use_case": "Stop collector harassment"
                    },
                    "Section 806": {
                        "title": "Harassment or Abuse",
                        "description": "Collectors cannot use threats, obscene language, or repeated calls to harass.",
                        "citation": "15 U.S.C. § 1692d",
                        "use_case": "Report and sue for collector abuse"
                    },
                    "Section 807": {
                        "title": "False or Misleading Representations",
                        "description": "Collectors cannot lie about debt amounts or threaten illegal actions.",
                        "citation": "15 U.S.C. § 1692e",
                        "use_case": "Challenge false statements about your debt"
                    },
                    "Section 809": {
                        "title": "Validation of Debts",
                        "description": "You can demand proof that you owe the debt within 30 days.",
                        "citation": "15 U.S.C. § 1692g",
                        "use_case": "Request debt validation letter"
                    },
                    "Section 813": {
                        "title": "Civil Liability",
                        "description": "Up to $1,000 in statutory damages plus actual damages per violation.",
                        "citation": "15 U.S.C. § 1692k",
                        "use_case": "Sue collectors for FDCPA violations"
                    }
                }
            },
            "ECOA": {
                "name": "Equal Credit Opportunity Act",
                "code": "15 U.S.C. § 1691",
                "overview": "Prohibits credit discrimination based on race, color, religion, national origin, sex, marital status, age, or public assistance status.",
                "key_provisions": {
                    "Section 701": {
                        "title": "Prohibited Discrimination",
                        "description": "Creditors cannot discriminate in any aspect of credit transaction.",
                        "citation": "15 U.S.C. § 1691(a)",
                        "use_case": "Challenge discriminatory credit denials"
                    },
                    "Section 706": {
                        "title": "Civil Liability",
                        "description": "Punitive damages up to $10,000 individual, $500,000 class action.",
                        "citation": "15 U.S.C. § 1691e",
                        "use_case": "Sue for credit discrimination"
                    }
                }
            },
            "TILA": {
                "name": "Truth in Lending Act",
                "code": "15 U.S.C. § 1601",
                "overview": "Requires clear disclosure of loan terms and costs.",
                "key_provisions": {
                    "Section 125": {
                        "title": "Right of Rescission",
                        "description": "3-day right to cancel certain loans secured by your home.",
                        "citation": "15 U.S.C. § 1635",
                        "use_case": "Cancel home equity loans within 3 days"
                    },
                    "Section 130": {
                        "title": "Civil Liability",
                        "description": "Statutory and actual damages for TILA violations.",
                        "citation": "15 U.S.C. § 1640",
                        "use_case": "Sue for improper loan disclosures"
                    }
                }
            },
            "FACTA": {
                "name": "Fair and Accurate Credit Transactions Act",
                "code": "15 U.S.C. § 1681",
                "overview": "Amendment to FCRA providing identity theft protections and free annual credit reports.",
                "key_provisions": {
                    "Section 151": {
                        "title": "Free Annual Credit Reports",
                        "description": "Consumers entitled to one free report annually from each bureau.",
                        "citation": "15 U.S.C. § 1681j",
                        "use_case": "Obtain free annual credit reports"
                    },
                    "Section 152": {
                        "title": "Fraud Alerts",
                        "description": "Right to place fraud alerts on your credit file.",
                        "citation": "15 U.S.C. § 1681c-1",
                        "use_case": "Protect against identity theft"
                    },
                    "Section 153": {
                        "title": "Credit Freezes",
                        "description": "Right to freeze credit file to prevent new accounts.",
                        "citation": "15 U.S.C. § 1681c-2",
                        "use_case": "Lock credit file from new inquiries"
                    }
                }
            },
            "STATE_LAWS": {
                "name": "State Consumer Protection Laws",
                "overview": "Many states have additional consumer protection laws.",
                "examples": {
                    "California": {
                        "law": "California Consumer Credit Reporting Agencies Act",
                        "code": "Cal. Civ. Code § 1785",
                        "benefits": "Stronger protections than federal FCRA"
                    },
                    "New York": {
                        "law": "NY Fair Credit Reporting Act",
                        "code": "NY Gen. Bus. Law § 380",
                        "benefits": "Additional accuracy requirements"
                    },
                    "Texas": {
                        "law": "Texas Finance Code",
                        "code": "Tex. Fin. Code § 20",
                        "benefits": "Enhanced dispute procedures"
                    }
                }
            }
        }

    def _load_international_laws(self) -> dict:
        """Load international credit and data protection laws."""
        return {
            "EU": {
                "GDPR": {
                    "name": "General Data Protection Regulation",
                    "code": "Regulation (EU) 2016/679",
                    "overview": "Comprehensive data protection law giving individuals control over personal data.",
                    "key_rights": {
                        "Right to Access": {
                            "article": "Article 15",
                            "description": "Right to obtain confirmation and access to your personal data."
                        },
                        "Right to Rectification": {
                            "article": "Article 16",
                            "description": "Right to have inaccurate personal data corrected."
                        },
                        "Right to Erasure": {
                            "article": "Article 17",
                            "description": "Right to have personal data deleted (Right to be Forgotten)."
                        },
                        "Right to Data Portability": {
                            "article": "Article 20",
                            "description": "Right to receive your data in portable format."
                        }
                    },
                    "penalties": "Up to €20 million or 4% of global annual revenue"
                }
            },
            "UK": {
                "Consumer_Credit_Act": {
                    "name": "Consumer Credit Act 1974",
                    "overview": "Regulates consumer credit and hire businesses.",
                    "key_sections": {
                        "Section 77-79": "Right to receive copies of credit agreements",
                        "Section 87": "Default notice requirements",
                        "Section 129": "Court power to make time orders"
                    }
                },
                "Data_Protection_Act": {
                    "name": "Data Protection Act 2018",
                    "overview": "UK implementation of GDPR principles.",
                    "regulator": "Information Commissioner's Office (ICO)"
                }
            },
            "Canada": {
                "Consumer_Reporting": {
                    "name": "Consumer Reporting Acts (Provincial)",
                    "overview": "Each province has its own consumer reporting legislation.",
                    "examples": {
                        "Ontario": "Consumer Reporting Act, R.S.O. 1990, c. C.33",
                        "British Columbia": "Business Practices and Consumer Protection Act",
                        "Alberta": "Fair Trading Act"
                    },
                    "common_rights": [
                        "Right to access your credit file",
                        "Right to dispute inaccurate information",
                        "Time limits on negative reporting (6-7 years)"
                    ]
                },
                "PIPEDA": {
                    "name": "Personal Information Protection and Electronic Documents Act",
                    "overview": "Federal privacy law governing collection and use of personal information.",
                    "key_principles": [
                        "Accountability",
                        "Consent",
                        "Accuracy",
                        "Individual access"
                    ]
                }
            },
            "Australia": {
                "Privacy_Act": {
                    "name": "Privacy Act 1988",
                    "part": "Part IIIA - Credit Reporting",
                    "overview": "Regulates credit reporting and credit information.",
                    "key_rights": [
                        "Access to credit information",
                        "Correction of inaccurate information",
                        "Complaints to OAIC"
                    ],
                    "retention_periods": {
                        "defaults": "5 years",
                        "serious_credit_infringements": "7 years",
                        "bankruptcy": "5 years from discharge"
                    }
                }
            },
            "India": {
                "Credit_Information": {
                    "name": "Credit Information Companies (Regulation) Act, 2005",
                    "overview": "Regulates credit information companies in India.",
                    "regulator": "Reserve Bank of India (RBI)",
                    "bureaus": ["CIBIL", "Experian", "Equifax", "CRIF High Mark"],
                    "key_rights": [
                        "Right to access credit report",
                        "Right to dispute errors",
                        "30-day resolution timeline"
                    ]
                }
            },
            "South_Africa": {
                "NCA": {
                    "name": "National Credit Act, 2005",
                    "overview": "Comprehensive credit regulation including reporting.",
                    "regulator": "National Credit Regulator (NCR)",
                    "key_rights": [
                        "Right to access credit report",
                        "Right to challenge information",
                        "Debt counselling rights"
                    ]
                }
            },
            "Mexico": {
                "Credit_Bureau_Law": {
                    "name": "Ley para Regular las Sociedades de Información Crediticia",
                    "overview": "Regulates credit bureaus in Mexico.",
                    "bureaus": ["Buró de Crédito", "Círculo de Crédito"],
                    "retention": "6 years for most negative items"
                }
            },
            "Brazil": {
                "Positive_Credit": {
                    "name": "Lei do Cadastro Positivo (Law 12,414/2011)",
                    "overview": "Regulates positive credit scoring in Brazil.",
                    "key_rights": [
                        "Right to access credit score",
                        "Right to correction",
                        "Right to exclusion in some cases"
                    ]
                }
            }
        }

    def _load_dispute_templates(self) -> dict:
        """Load dispute letter templates with legal citations."""
        return {
            "debt_validation": {
                "name": "Debt Validation Request",
                "law": "FDCPA Section 809",
                "citation": "15 U.S.C. § 1692g",
                "timing": "Within 30 days of first contact",
                "purpose": "Require collector to prove you owe the debt"
            },
            "dispute_to_bureau": {
                "name": "Credit Bureau Dispute",
                "law": "FCRA Section 611",
                "citation": "15 U.S.C. § 1681i",
                "timing": "Any time",
                "purpose": "Challenge inaccurate information on credit report"
            },
            "dispute_to_furnisher": {
                "name": "Direct Furnisher Dispute",
                "law": "FCRA Section 623",
                "citation": "15 U.S.C. § 1681s-2",
                "timing": "After bureau investigation",
                "purpose": "Dispute directly with the company reporting the information"
            },
            "cease_and_desist": {
                "name": "Cease and Desist Letter",
                "law": "FDCPA Section 805(c)",
                "citation": "15 U.S.C. § 1692c(c)",
                "timing": "Any time",
                "purpose": "Stop collector from contacting you"
            },
            "goodwill_deletion": {
                "name": "Goodwill Deletion Request",
                "law": "No specific law",
                "citation": "N/A",
                "timing": "After account is paid",
                "purpose": "Request creditor remove negative mark as courtesy"
            },
            "pay_for_delete": {
                "name": "Pay for Delete Agreement",
                "law": "No specific law",
                "citation": "N/A",
                "timing": "Before paying collection",
                "purpose": "Negotiate deletion in exchange for payment"
            },
            "method_of_verification": {
                "name": "Method of Verification Request",
                "law": "FCRA Section 611(a)(7)",
                "citation": "15 U.S.C. § 1681i(a)(7)",
                "timing": "After investigation",
                "purpose": "Learn how bureau verified disputed information"
            },
            "intent_to_sue": {
                "name": "Intent to Sue Letter",
                "law": "FCRA/FDCPA",
                "citation": "15 U.S.C. § 1681n, § 1692k",
                "timing": "After violations occur",
                "purpose": "Final demand before litigation"
            }
        }

    def get_law(self, law_code: str) -> dict:
        """Get information about a specific law."""
        # Check US laws
        if law_code.upper() in self.us_laws:
            return self.us_laws[law_code.upper()]

        # Check international laws
        for region, laws in self.international_laws.items():
            if law_code.upper() in laws:
                return laws[law_code.upper()]

        return {}

    def get_citation_for_dispute(self, dispute_type: str) -> dict:
        """Get the appropriate legal citation for a dispute type."""
        dispute_lower = dispute_type.lower()

        if "validation" in dispute_lower or "verify" in dispute_lower:
            return {
                "primary": self.us_laws["FDCPA"]["key_provisions"]["Section 809"],
                "law": "FDCPA",
                "template": "debt_validation"
            }
        elif "collection" in dispute_lower:
            return {
                "primary": self.us_laws["FCRA"]["key_provisions"]["Section 611"],
                "secondary": self.us_laws["FDCPA"]["key_provisions"]["Section 809"],
                "law": "FCRA/FDCPA",
                "template": "dispute_to_bureau"
            }
        elif "late" in dispute_lower or "payment" in dispute_lower:
            return {
                "primary": self.us_laws["FCRA"]["key_provisions"]["Section 611"],
                "law": "FCRA",
                "template": "dispute_to_bureau"
            }
        elif "inquiry" in dispute_lower:
            return {
                "primary": self.us_laws["FCRA"]["key_provisions"]["Section 604"],
                "law": "FCRA",
                "template": "dispute_to_bureau"
            }
        elif "harassment" in dispute_lower:
            return {
                "primary": self.us_laws["FDCPA"]["key_provisions"]["Section 806"],
                "law": "FDCPA",
                "template": "cease_and_desist"
            }
        else:
            return {
                "primary": self.us_laws["FCRA"]["key_provisions"]["Section 611"],
                "law": "FCRA",
                "template": "dispute_to_bureau"
            }

    def get_statute_of_limitations(self, state: str = None) -> dict:
        """Get statute of limitations for credit reporting."""
        return {
            "federal": {
                "most_negative_items": "7 years from date of first delinquency",
                "chapter_7_bankruptcy": "10 years from filing date",
                "chapter_13_bankruptcy": "7 years from filing date",
                "tax_liens_paid": "7 years from payment",
                "tax_liens_unpaid": "Indefinite (until paid)",
                "hard_inquiries": "2 years",
                "judgments": "7 years or until statute expires"
            },
            "collection_debt": {
                "typical_range": "3-6 years (varies by state)",
                "note": "Separate from credit reporting time limits",
                "restart_triggers": [
                    "Making a payment",
                    "Acknowledging the debt in writing",
                    "Entering a payment plan"
                ]
            }
        }

    def get_consumer_rights_summary(self) -> list:
        """Get a summary of key consumer rights."""
        return [
            {
                "right": "Free Annual Credit Reports",
                "description": "You're entitled to one free report from each bureau annually.",
                "how_to_exercise": "Visit AnnualCreditReport.com",
                "law": "FACTA Section 151"
            },
            {
                "right": "Dispute Inaccurate Information",
                "description": "You can dispute any inaccurate information on your credit report.",
                "how_to_exercise": "Send written dispute to credit bureau",
                "law": "FCRA Section 611"
            },
            {
                "right": "30-Day Investigation",
                "description": "Bureaus must investigate disputes within 30 days.",
                "how_to_exercise": "Track your dispute and follow up",
                "law": "FCRA Section 611"
            },
            {
                "right": "Debt Validation",
                "description": "Collectors must prove you owe the debt if you request.",
                "how_to_exercise": "Send validation letter within 30 days of first contact",
                "law": "FDCPA Section 809"
            },
            {
                "right": "Stop Collector Contact",
                "description": "You can demand collectors stop contacting you.",
                "how_to_exercise": "Send cease and desist letter",
                "law": "FDCPA Section 805(c)"
            },
            {
                "right": "Sue for Violations",
                "description": "You can sue for FCRA/FDCPA violations and recover damages.",
                "how_to_exercise": "Consult with consumer protection attorney",
                "law": "FCRA Section 616-617, FDCPA Section 813"
            },
            {
                "right": "Fraud Alerts & Credit Freezes",
                "description": "Protect yourself from identity theft.",
                "how_to_exercise": "Contact any credit bureau to place alerts/freezes",
                "law": "FACTA Sections 152-153"
            },
            {
                "right": "Adverse Action Notice",
                "description": "Creditors must explain why they denied you credit.",
                "how_to_exercise": "Request explanation if denied",
                "law": "FCRA Section 615, ECOA"
            }
        ]
