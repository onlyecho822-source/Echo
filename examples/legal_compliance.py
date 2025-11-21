"""
Example: Legal Document Analysis and Compliance Checking
Using EchoLex for legal operations
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

# from echo_engines.echo_lex import EchoLexEngine, ComplianceFramework, DocumentType


class LegalComplianceSystem:
    """Automated legal and compliance system"""

    def __init__(self, jurisdiction: str = "US"):
        # self.engine = EchoLexEngine(config={"jurisdiction": jurisdiction})
        self.jurisdiction = jurisdiction

    async def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """Comprehensive contract analysis"""

        print("Analyzing contract...")

        # Analyze contract
        # analysis = await self.engine.analyze_contract(contract_text)

        analysis = {
            "document_type": "contract",
            "jurisdiction": self.jurisdiction,
            "key_terms": [
                {
                    "term": "Payment Terms",
                    "details": "Net 30 days from invoice date",
                    "importance": "high"
                },
                {
                    "term": "Termination Clause",
                    "details": "Either party may terminate with 30 days notice",
                    "importance": "high"
                },
                {
                    "term": "Liability Limitation",
                    "details": "Limited to fees paid in prior 12 months",
                    "importance": "critical"
                },
                {
                    "term": "Intellectual Property",
                    "details": "All IP remains with original owner",
                    "importance": "critical"
                },
                {
                    "term": "Confidentiality",
                    "details": "2 year confidentiality obligation",
                    "importance": "medium"
                }
            ],
            "risks": [
                {
                    "level": "high",
                    "category": "liability",
                    "description": "Unlimited liability for data breaches",
                    "recommendation": "Add liability cap for security incidents",
                    "impact": "Could result in unlimited financial exposure"
                },
                {
                    "level": "medium",
                    "category": "termination",
                    "description": "Short notice period may be insufficient",
                    "recommendation": "Negotiate 60-90 day notice period",
                    "impact": "Risk of sudden service disruption"
                },
                {
                    "level": "low",
                    "category": "payment",
                    "description": "No late payment penalties specified",
                    "recommendation": "Add interest on late payments",
                    "impact": "Minor cash flow risk"
                }
            ],
            "compliance_issues": [],
            "overall_risk_score": 65,
            "recommendation": "Review and negotiate key terms before signing",
            "analyzed_at": datetime.now().isoformat()
        }

        return analysis

    async def check_compliance(self, content: str, frameworks: List[str]) -> Dict[str, Any]:
        """Check compliance against multiple frameworks"""

        print(f"Checking compliance for: {', '.join(frameworks)}")

        results = {}

        for framework in frameworks:
            # compliance = await self.engine.check_compliance(
            #     content,
            #     ComplianceFramework[framework]
            # )

            # Simulate compliance check
            if framework == "GDPR":
                compliance = {
                    "framework": "GDPR",
                    "status": "compliant",
                    "score": 92,
                    "issues": [
                        {
                            "severity": "low",
                            "article": "Article 13",
                            "description": "Privacy notice could be more prominent",
                            "recommendation": "Update notice placement"
                        }
                    ],
                    "requirements_met": [
                        "Right to access",
                        "Right to erasure",
                        "Data portability",
                        "Consent management",
                        "Data breach notification"
                    ]
                }
            elif framework == "CCPA":
                compliance = {
                    "framework": "CCPA",
                    "status": "compliant",
                    "score": 95,
                    "issues": [],
                    "requirements_met": [
                        "Right to know",
                        "Right to delete",
                        "Right to opt-out",
                        "Non-discrimination"
                    ]
                }
            elif framework == "HIPAA":
                compliance = {
                    "framework": "HIPAA",
                    "status": "needs_review",
                    "score": 78,
                    "issues": [
                        {
                            "severity": "high",
                            "rule": "Security Rule",
                            "description": "Encryption at rest not documented",
                            "recommendation": "Implement and document encryption"
                        },
                        {
                            "severity": "medium",
                            "rule": "Privacy Rule",
                            "description": "Business Associate Agreement required",
                            "recommendation": "Execute BAA with all vendors"
                        }
                    ],
                    "requirements_met": [
                        "Access controls",
                        "Audit logs",
                        "Data backup"
                    ]
                }
            else:
                compliance = {
                    "framework": framework,
                    "status": "unknown",
                    "score": 0,
                    "issues": []
                }

            results[framework] = compliance

        return results

    async def generate_privacy_policy(self, company_info: Dict[str, Any]) -> str:
        """Generate privacy policy"""

        print("Generating privacy policy...")

        # policy = await self.engine.generate_document(
        #     DocumentType.PRIVACY_POLICY,
        #     parameters=company_info
        # )

        policy = f"""
PRIVACY POLICY

Last Updated: {datetime.now().strftime('%B %d, %Y')}

1. INFORMATION WE COLLECT
{company_info['company_name']} collects the following information:
- Personal identification information
- Usage data and analytics
- Device and browser information

2. HOW WE USE YOUR INFORMATION
We use your information to:
- Provide and improve our services
- Communicate with you
- Ensure security and prevent fraud

3. DATA SHARING
We do not sell your personal information. We may share data with:
- Service providers and partners
- Legal authorities when required by law

4. YOUR RIGHTS
Under GDPR and CCPA, you have the right to:
- Access your personal data
- Request deletion of your data
- Opt-out of data sale
- Data portability

5. SECURITY
We implement industry-standard security measures including:
- Encryption in transit and at rest
- Regular security audits
- Access controls and authentication

6. CONTACT US
For privacy questions, contact:
{company_info['contact_email']}
{company_info['address']}

This policy is compliant with GDPR, CCPA, and other applicable regulations.
"""

        return policy

    async def assess_risk(self, scenario: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal and compliance risks"""

        print(f"Assessing risk for: {scenario}")

        # assessment = await self.engine.assess_risk(scenario, context)

        assessment = {
            "scenario": scenario,
            "overall_risk_level": "medium",
            "risk_score": 60,
            "risk_factors": [
                {
                    "factor": "Data Privacy",
                    "severity": "high",
                    "probability": "medium",
                    "impact": "Potential GDPR violation and fines",
                    "mitigation": "Implement data processing agreements and consent management"
                },
                {
                    "factor": "Contractual Liability",
                    "severity": "medium",
                    "probability": "low",
                    "impact": "Contract breach claims",
                    "mitigation": "Review and update service level agreements"
                },
                {
                    "factor": "Intellectual Property",
                    "severity": "low",
                    "probability": "low",
                    "impact": "IP ownership disputes",
                    "mitigation": "Clear IP assignment clauses in contracts"
                }
            ],
            "recommendations": [
                "Conduct full legal review before proceeding",
                "Implement recommended mitigations",
                "Obtain appropriate insurance coverage",
                "Regular compliance audits"
            ],
            "estimated_cost_of_non_compliance": "$50,000 - $500,000",
            "assessed_at": datetime.now().isoformat()
        }

        return assessment


# Example usage
async def main():
    system = LegalComplianceSystem(jurisdiction="US")

    print("=" * 60)
    print("Echo Legal & Compliance Examples")
    print("=" * 60)

    # Example 1: Contract Analysis
    print("\n1. Analyzing Contract...")
    sample_contract = """
    This Service Agreement is entered into between Company A and Company B.
    Payment terms: Net 30 days. Either party may terminate with 30 days notice.
    Liability is limited to fees paid in the prior 12 months.
    """

    analysis = await system.analyze_contract(sample_contract)
    print(f"✓ Risk Score: {analysis['overall_risk_score']}/100")
    print(f"✓ Key Terms: {len(analysis['key_terms'])}")
    print(f"✓ Risks Identified: {len(analysis['risks'])}")
    print(f"✓ Recommendation: {analysis['recommendation']}")

    # Example 2: Compliance Check
    print("\n2. Checking Compliance...")
    compliance_results = await system.check_compliance(
        content="Sample privacy policy content...",
        frameworks=["GDPR", "CCPA", "HIPAA"]
    )
    for framework, result in compliance_results.items():
        print(f"✓ {framework}: {result['status']} (Score: {result['score']})")

    # Example 3: Generate Privacy Policy
    print("\n3. Generating Privacy Policy...")
    policy = await system.generate_privacy_policy({
        "company_name": "Echo Technologies Inc.",
        "contact_email": "privacy@echo.ai",
        "address": "123 Tech Street, San Francisco, CA 94102"
    })
    print(f"✓ Privacy policy generated ({len(policy)} characters)")

    # Example 4: Risk Assessment
    print("\n4. Assessing Risk...")
    risk = await system.assess_risk(
        scenario="Storing customer health data in cloud",
        context={
            "data_type": "health_records",
            "storage": "cloud",
            "users": 10000
        }
    )
    print(f"✓ Risk Level: {risk['overall_risk_level']}")
    print(f"✓ Risk Score: {risk['risk_score']}/100")
    print(f"✓ Risk Factors: {len(risk['risk_factors'])}")

    print("\n" + "=" * 60)
    print("Legal & compliance analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
