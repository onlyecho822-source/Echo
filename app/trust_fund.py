"""Trust fund guidance and planning module."""

from typing import Optional
from datetime import datetime


class TrustFundGuide:
    """Comprehensive trust fund guidance and planning assistance."""

    def __init__(self):
        self.trust_types = self._load_trust_types()
        self.state_requirements = self._load_state_requirements()

    def _load_trust_types(self) -> dict:
        """Load information about different types of trusts."""
        return {
            "revocable_living": {
                "name": "Revocable Living Trust",
                "description": "A trust you create during your lifetime that you can modify or revoke at any time.",
                "benefits": [
                    "Avoid probate - assets transfer immediately",
                    "Privacy - unlike wills, trusts are not public record",
                    "Flexibility - can be changed anytime during your life",
                    "Incapacity planning - successor trustee can manage if you're unable",
                    "No court involvement for asset distribution"
                ],
                "drawbacks": [
                    "No tax benefits - assets still in your estate",
                    "Setup cost higher than simple will",
                    "Requires funding - must transfer assets into trust",
                    "No asset protection from creditors"
                ],
                "best_for": [
                    "Avoiding probate",
                    "Privacy concerns",
                    "Owning property in multiple states",
                    "Blended families",
                    "Incapacity planning"
                ],
                "typical_cost": "$1,000 - $3,000",
                "complexity": "Low to Medium",
                "minimum_assets": "Generally beneficial when assets exceed $100,000"
            },
            "irrevocable": {
                "name": "Irrevocable Trust",
                "description": "A trust that cannot be modified or revoked once created.",
                "benefits": [
                    "Estate tax reduction - removes assets from taxable estate",
                    "Asset protection from creditors",
                    "Medicaid planning - assets not counted after lookback period",
                    "Generation-skipping tax benefits",
                    "Life insurance trust benefits"
                ],
                "drawbacks": [
                    "Cannot change or revoke once created",
                    "Lose control of assets",
                    "Gift tax may apply when funding",
                    "Complex to set up and maintain",
                    "Requires separate tax return"
                ],
                "best_for": [
                    "High net worth individuals (estate over $12M+)",
                    "Asset protection needs",
                    "Medicaid planning",
                    "Life insurance policies",
                    "Charitable giving"
                ],
                "typical_cost": "$2,000 - $10,000+",
                "complexity": "High",
                "minimum_assets": "Generally beneficial for estates exceeding estate tax exemption"
            },
            "testamentary": {
                "name": "Testamentary Trust",
                "description": "A trust created through your will that takes effect after death.",
                "benefits": [
                    "Control over inheritance for minors",
                    "Can specify age distributions",
                    "Lower setup cost - part of will",
                    "Flexibility until death"
                ],
                "drawbacks": [
                    "Must go through probate first",
                    "Becomes public record",
                    "No lifetime benefits",
                    "No incapacity planning"
                ],
                "best_for": [
                    "Parents with minor children",
                    "Providing for special needs dependents",
                    "Controlling inheritance for spendthrift heirs",
                    "Those with modest estates"
                ],
                "typical_cost": "$500 - $2,000 (as part of will)",
                "complexity": "Low",
                "minimum_assets": "Any amount left to minors or those needing protection"
            },
            "special_needs": {
                "name": "Special Needs Trust (SNT)",
                "description": "Provides for a disabled beneficiary without disqualifying them from government benefits.",
                "benefits": [
                    "Preserves eligibility for SSI and Medicaid",
                    "Provides supplemental support",
                    "Professional management option",
                    "Protects inheritance"
                ],
                "drawbacks": [
                    "Strict rules on distributions",
                    "Requires special expertise to draft",
                    "May require court approval for major decisions",
                    "Medicaid payback may be required (first-party SNT)"
                ],
                "types": {
                    "First-Party SNT": "Funded with beneficiary's own assets (lawsuit settlement, inheritance)",
                    "Third-Party SNT": "Funded by family members (no Medicaid payback)"
                },
                "best_for": [
                    "Disabled family members receiving government benefits",
                    "Personal injury settlements",
                    "Inheritance planning for disabled heirs"
                ],
                "typical_cost": "$2,500 - $5,000",
                "complexity": "High",
                "minimum_assets": "$10,000+"
            },
            "charitable": {
                "name": "Charitable Trust",
                "description": "Provides benefits to charity while potentially providing income or tax benefits to grantor.",
                "types": {
                    "Charitable Remainder Trust (CRT)": {
                        "description": "Provides income to you, remainder goes to charity",
                        "benefits": [
                            "Income tax deduction",
                            "Capital gains tax avoidance",
                            "Lifetime income stream",
                            "Estate tax reduction"
                        ]
                    },
                    "Charitable Lead Trust (CLT)": {
                        "description": "Provides income to charity, remainder goes to heirs",
                        "benefits": [
                            "Estate tax reduction",
                            "Gift tax benefits",
                            "Transfer wealth to heirs at reduced tax cost"
                        ]
                    }
                },
                "best_for": [
                    "Philanthropic goals",
                    "Highly appreciated assets",
                    "High income individuals",
                    "Estate tax reduction"
                ],
                "typical_cost": "$3,000 - $10,000",
                "complexity": "High",
                "minimum_assets": "$250,000+ (to justify cost)"
            },
            "spendthrift": {
                "name": "Spendthrift Trust",
                "description": "Protects assets from beneficiary's creditors and poor financial decisions.",
                "benefits": [
                    "Creditor protection for beneficiary",
                    "Protection from divorce settlements",
                    "Trustee controls distributions",
                    "Protects irresponsible heirs"
                ],
                "best_for": [
                    "Heirs with creditor issues",
                    "Beneficiaries with addiction problems",
                    "Protection from divorce",
                    "Financially irresponsible heirs"
                ],
                "typical_cost": "$2,000 - $5,000",
                "complexity": "Medium"
            },
            "asset_protection": {
                "name": "Asset Protection Trust",
                "description": "Irrevocable trust designed to protect assets from creditors.",
                "benefits": [
                    "Strong creditor protection",
                    "May retain some control as beneficiary",
                    "Domestic options available (Nevada, Delaware, etc.)"
                ],
                "drawbacks": [
                    "Must be created before creditor issues arise",
                    "Complex and expensive",
                    "Fraudulent transfer risks",
                    "May not protect against all creditors"
                ],
                "best_for": [
                    "High liability professions (doctors, business owners)",
                    "Asset protection planning",
                    "Those in litigious industries"
                ],
                "typical_cost": "$5,000 - $20,000+",
                "complexity": "High",
                "minimum_assets": "$500,000+"
            },
            "land_trust": {
                "name": "Land Trust",
                "description": "Holds title to real estate with beneficiary remaining private.",
                "benefits": [
                    "Privacy - ownership not public record",
                    "Easier transfer of real estate",
                    "Avoid due-on-sale clause issues",
                    "Simple probate avoidance for property"
                ],
                "best_for": [
                    "Real estate investors",
                    "Privacy in property ownership",
                    "Estate planning for real property"
                ],
                "typical_cost": "$500 - $1,500 per property",
                "complexity": "Low",
                "states": "Not available in all states"
            },
            "dynasty": {
                "name": "Dynasty Trust",
                "description": "Designed to pass wealth through multiple generations without estate tax.",
                "benefits": [
                    "Multi-generational wealth transfer",
                    "Avoids estate tax at each generation",
                    "Asset protection",
                    "Family legacy preservation"
                ],
                "best_for": [
                    "Very high net worth families",
                    "Multi-generational wealth planning",
                    "Tax minimization across generations"
                ],
                "typical_cost": "$5,000 - $15,000+",
                "complexity": "Very High",
                "minimum_assets": "Several million dollars"
            }
        }

    def _load_state_requirements(self) -> dict:
        """Load state-specific trust requirements."""
        return {
            "general_requirements": {
                "creator": "Must be of legal age and sound mind",
                "intent": "Must clearly intend to create a trust",
                "property": "Must have specific property to transfer",
                "beneficiary": "Must have identifiable beneficiaries (or charitable purpose)",
                "trustee": "Must name a trustee",
                "purpose": "Must have a legal purpose"
            },
            "favorable_states": {
                "Nevada": {
                    "benefits": [
                        "No state income tax on trust",
                        "Strong asset protection (2 year statute)",
                        "Self-settled asset protection trusts",
                        "No rule against perpetuities (dynasty trusts)"
                    ]
                },
                "Delaware": {
                    "benefits": [
                        "No state income tax for non-resident beneficiaries",
                        "Strong asset protection",
                        "Directed trusts allowed",
                        "No rule against perpetuities"
                    ]
                },
                "South_Dakota": {
                    "benefits": [
                        "No state income tax",
                        "No rule against perpetuities",
                        "Strong privacy laws",
                        "Domestic asset protection trusts"
                    ]
                },
                "Wyoming": {
                    "benefits": [
                        "No state income tax",
                        "Strong asset protection",
                        "LLC-trust combinations",
                        "1000-year trust duration"
                    ]
                }
            }
        }

    def get_trust_recommendation(self, user_profile: dict) -> list:
        """Get trust recommendations based on user profile."""
        recommendations = []

        net_worth = user_profile.get("net_worth", 0)
        has_minor_children = user_profile.get("has_minor_children", False)
        has_disabled_dependent = user_profile.get("has_disabled_dependent", False)
        owns_business = user_profile.get("owns_business", False)
        owns_real_estate = user_profile.get("owns_real_estate", False)
        charitable_intent = user_profile.get("charitable_intent", False)
        asset_protection_needed = user_profile.get("asset_protection_needed", False)

        # Always recommend revocable living trust for basic estate planning
        if net_worth >= 100000:
            recommendations.append({
                "trust_type": "revocable_living",
                "priority": "High",
                "reason": "Foundation for avoiding probate and incapacity planning"
            })

        # Special needs trust for disabled dependents
        if has_disabled_dependent:
            recommendations.append({
                "trust_type": "special_needs",
                "priority": "Critical",
                "reason": "Protect government benefits while providing supplemental support"
            })

        # Testamentary trust for minor children
        if has_minor_children and net_worth < 500000:
            recommendations.append({
                "trust_type": "testamentary",
                "priority": "High",
                "reason": "Manage inheritance for minor children"
            })

        # Irrevocable trust for high net worth
        if net_worth >= 5000000:
            recommendations.append({
                "trust_type": "irrevocable",
                "priority": "High",
                "reason": "Estate tax planning and asset protection"
            })

        # Asset protection trust for business owners
        if owns_business or asset_protection_needed:
            recommendations.append({
                "trust_type": "asset_protection",
                "priority": "Medium",
                "reason": "Protect assets from business liability and creditors"
            })

        # Land trust for real estate
        if owns_real_estate:
            recommendations.append({
                "trust_type": "land_trust",
                "priority": "Medium",
                "reason": "Privacy and easier transfer of real estate"
            })

        # Charitable trust for philanthropic goals
        if charitable_intent and net_worth >= 250000:
            recommendations.append({
                "trust_type": "charitable",
                "priority": "Medium",
                "reason": "Tax benefits while supporting causes you care about"
            })

        # Dynasty trust for multi-generational wealth
        if net_worth >= 10000000:
            recommendations.append({
                "trust_type": "dynasty",
                "priority": "Medium",
                "reason": "Multi-generational wealth transfer with tax efficiency"
            })

        return recommendations

    def get_trust_creation_checklist(self, trust_type: str) -> dict:
        """Get a checklist for creating a specific type of trust."""
        base_checklist = {
            "preparation": [
                "Inventory all assets (accounts, property, investments)",
                "List all debts and liabilities",
                "Identify beneficiaries and their contact information",
                "Decide on trustee and successor trustee",
                "Gather important documents (deeds, titles, account statements)",
                "Consider your goals and concerns"
            ],
            "legal_steps": [
                "Consult with estate planning attorney",
                "Draft trust document",
                "Review and sign trust document (proper witnessing/notarization)",
                "Obtain EIN for trust if required (irrevocable trusts)"
            ],
            "funding": [
                "Transfer bank accounts to trust",
                "Transfer investment accounts to trust",
                "Deed real estate to trust",
                "Assign personal property to trust",
                "Update beneficiary designations (life insurance, retirement)",
                "Retitle vehicles if desired"
            ],
            "maintenance": [
                "Keep trust document in safe place",
                "Inform successor trustee of location",
                "Review trust every 3-5 years",
                "Update for life changes (marriage, divorce, birth, death)",
                "Ensure new assets are properly titled"
            ]
        }

        # Add type-specific items
        if trust_type == "irrevocable":
            base_checklist["additional"] = [
                "Understand you cannot change or revoke",
                "File separate tax return (Form 1041)",
                "Consider gift tax implications",
                "May need formal trust accounting"
            ]
        elif trust_type == "special_needs":
            base_checklist["additional"] = [
                "Coordinate with benefits planners",
                "Ensure trustee understands government benefit rules",
                "Include specific distribution guidelines",
                "Consider professional trustee or trust company"
            ]
        elif trust_type == "charitable":
            base_checklist["additional"] = [
                "Select qualified charitable organization",
                "Obtain qualified appraisal for non-cash assets",
                "Understand payout requirements",
                "File required IRS forms"
            ]

        return base_checklist

    def calculate_trust_benefits(self, trust_type: str, assets: float, annual_income: float = 0) -> dict:
        """Calculate potential benefits of creating a trust."""
        benefits = {
            "trust_type": trust_type,
            "assets": assets
        }

        if trust_type == "revocable_living":
            # Probate cost savings
            probate_cost = assets * 0.05  # Typical 3-7% of estate
            benefits["probate_savings"] = probate_cost
            benefits["time_savings"] = "6-18 months probate time avoided"
            benefits["privacy"] = "Assets remain private"

        elif trust_type == "irrevocable":
            # Estate tax calculation (2024 exemption ~$13.61M)
            estate_tax_exemption = 13610000
            if assets > estate_tax_exemption:
                taxable_estate = assets - estate_tax_exemption
                estate_tax = taxable_estate * 0.40  # Top estate tax rate
                benefits["potential_estate_tax_savings"] = estate_tax
            else:
                benefits["potential_estate_tax_savings"] = 0
            benefits["asset_protection"] = True

        elif trust_type == "charitable":
            # Income tax deduction estimate
            if assets > 0:
                # Rough estimate - actual depends on many factors
                deduction = assets * 0.30  # Varies widely
                tax_savings = deduction * 0.37  # Top marginal rate
                benefits["estimated_tax_deduction"] = deduction
                benefits["estimated_tax_savings"] = tax_savings

        return benefits

    def get_professional_resources(self) -> dict:
        """Get resources for finding trust professionals."""
        return {
            "attorneys": {
                "organizations": [
                    {
                        "name": "American College of Trust and Estate Counsel (ACTEC)",
                        "website": "actec.org",
                        "description": "Organization of top trust and estate attorneys"
                    },
                    {
                        "name": "National Academy of Elder Law Attorneys (NAELA)",
                        "website": "naela.org",
                        "description": "Specialists in elder law and special needs planning"
                    },
                    {
                        "name": "State Bar Association",
                        "description": "Lawyer referral services in your state"
                    }
                ],
                "questions_to_ask": [
                    "What percentage of your practice is estate planning?",
                    "How many trusts have you drafted?",
                    "What is your fee structure?",
                    "Do you provide ongoing maintenance?",
                    "Can you help with funding the trust?"
                ]
            },
            "financial_advisors": {
                "designations": [
                    "CFP (Certified Financial Planner)",
                    "ChFC (Chartered Financial Consultant)",
                    "AEP (Accredited Estate Planner)"
                ]
            },
            "trust_companies": {
                "description": "Can serve as professional trustee",
                "when_to_use": [
                    "No suitable family member to serve as trustee",
                    "Complex assets requiring professional management",
                    "Potential family conflicts",
                    "Long-term trusts (dynasty, special needs)"
                ]
            },
            "diy_options": {
                "warning": "Trusts have significant legal implications. DIY should only be considered for simple situations.",
                "resources": [
                    "Nolo Press legal guides",
                    "Online legal services (limited, simple trusts only)"
                ],
                "recommended_for": "Only very simple revocable trusts with limited assets"
            }
        }

    def get_wealth_building_with_trusts(self) -> dict:
        """Guide to building wealth using trusts as part of strategy."""
        return {
            "overview": "Trusts are wealth preservation tools, not wealth creation tools. Build wealth first, then protect it.",
            "wealth_building_stages": {
                "stage_1": {
                    "name": "Foundation (Net Worth < $100K)",
                    "trust_recommendation": "Generally not needed yet",
                    "focus": [
                        "Emergency fund",
                        "Paying off high-interest debt",
                        "Basic will",
                        "Term life insurance if dependents"
                    ]
                },
                "stage_2": {
                    "name": "Accumulation ($100K - $500K)",
                    "trust_recommendation": "Consider revocable living trust",
                    "focus": [
                        "Maximize retirement contributions",
                        "Build investment portfolio",
                        "Protect assets with proper insurance",
                        "Basic estate plan with trust"
                    ]
                },
                "stage_3": {
                    "name": "Growth ($500K - $2M)",
                    "trust_recommendation": "Revocable trust, possibly asset protection",
                    "focus": [
                        "Tax optimization",
                        "Asset protection planning",
                        "Consider real estate investment trusts",
                        "Comprehensive estate plan"
                    ]
                },
                "stage_4": {
                    "name": "Preservation ($2M - $10M)",
                    "trust_recommendation": "Multiple trust types",
                    "focus": [
                        "Estate tax planning",
                        "Irrevocable trusts for tax efficiency",
                        "Charitable giving strategies",
                        "Family limited partnerships"
                    ]
                },
                "stage_5": {
                    "name": "Legacy ($10M+)",
                    "trust_recommendation": "Comprehensive trust strategy",
                    "focus": [
                        "Dynasty trusts",
                        "Private foundations",
                        "Family office considerations",
                        "Multi-generational planning"
                    ]
                }
            },
            "wealth_protection_strategies": [
                {
                    "strategy": "Retirement Account Protection",
                    "description": "IRAs and 401(k)s have built-in creditor protection in most states",
                    "action": "Maximize retirement contributions before funding trusts"
                },
                {
                    "strategy": "Insurance as First Line",
                    "description": "Liability insurance protects before trusts needed",
                    "action": "Umbrella policy of at least $1M"
                },
                {
                    "strategy": "Business Entity Structure",
                    "description": "LLCs and corporations protect personal assets",
                    "action": "Properly structure any business ventures"
                },
                {
                    "strategy": "Trust Planning",
                    "description": "Trusts protect assets already built",
                    "action": "Implement appropriate trusts based on wealth stage"
                }
            ]
        }
