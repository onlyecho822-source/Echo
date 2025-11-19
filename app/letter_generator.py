"""Dispute letter generator with legal templates."""

from datetime import datetime
from typing import Optional
from .legal_knowledge import LegalKnowledgeBase


class DisputeLetterGenerator:
    """Generate professional dispute letters with proper legal citations."""

    def __init__(self):
        self.legal_kb = LegalKnowledgeBase()
        self.bureau_addresses = {
            "Experian": {
                "name": "Experian",
                "address": "P.O. Box 4500",
                "city": "Allen, TX 75013",
                "phone": "1-888-397-3742"
            },
            "Equifax": {
                "name": "Equifax Information Services LLC",
                "address": "P.O. Box 740256",
                "city": "Atlanta, GA 30374",
                "phone": "1-800-864-2978"
            },
            "TransUnion": {
                "name": "TransUnion LLC",
                "address": "P.O. Box 2000",
                "city": "Chester, PA 19016",
                "phone": "1-800-916-8800"
            }
        }

    def generate_letter(
        self,
        letter_type: str,
        user_info: dict,
        dispute_info: dict,
        target: str = "bureau"
    ) -> dict:
        """Generate a dispute letter based on type."""
        generators = {
            "debt_validation": self._generate_debt_validation,
            "bureau_dispute": self._generate_bureau_dispute,
            "furnisher_dispute": self._generate_furnisher_dispute,
            "cease_desist": self._generate_cease_desist,
            "goodwill_deletion": self._generate_goodwill_deletion,
            "pay_for_delete": self._generate_pay_for_delete,
            "method_of_verification": self._generate_mov_request,
            "intent_to_sue": self._generate_intent_to_sue,
            "identity_theft": self._generate_identity_theft,
            "late_payment_removal": self._generate_late_payment_removal,
        }

        generator = generators.get(letter_type, self._generate_bureau_dispute)
        return generator(user_info, dispute_info, target)

    def _generate_debt_validation(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate debt validation letter under FDCPA Section 809."""
        date = datetime.now().strftime("%B %d, %Y")

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{dispute_info.get('collector_name', '[COLLECTION AGENCY NAME]')}
{dispute_info.get('collector_address', '[COLLECTION AGENCY ADDRESS]')}
{dispute_info.get('collector_city_state_zip', '[CITY, STATE ZIP]')}

Re: Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}
    Alleged Amount: ${dispute_info.get('amount', '[AMOUNT]')}

To Whom It May Concern:

I am writing in response to your communication regarding the above-referenced account. This letter is being sent within thirty (30) days of my receipt of your initial communication, as required by law.

Pursuant to my rights under the Fair Debt Collection Practices Act, 15 U.S.C. § 1692g (Section 809), I hereby demand validation of this alleged debt.

Please provide the following:

1. The amount of the debt and how it was calculated, including all fees, interest, and charges
2. The name and address of the original creditor
3. A copy of any judgment (if applicable)
4. Proof that the Statute of Limitations has not expired
5. Proof that you are licensed to collect debt in my state
6. A copy of the original signed agreement or contract
7. Complete payment history from the original creditor
8. Proof that you own this debt or are authorized to collect it

Under the FDCPA, 15 U.S.C. § 1692g(b), you must cease collection activities until you provide the requested validation. Any attempt to collect this debt without providing proper validation will be considered a violation of federal law.

Additionally, be advised that I am aware of my rights under the Fair Credit Reporting Act, 15 U.S.C. § 1681. If you report this alleged debt to any credit reporting agency without proper validation, I will consider this a willful violation of the FCRA.

I request that you do not contact me by telephone. All communications must be in writing and sent to the address above.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Debt Validation",
            "content": letter,
            "legal_basis": {
                "primary_law": "FDCPA",
                "sections": ["Section 809 - Validation of Debts", "15 U.S.C. § 1692g"],
                "additional": ["FCRA Section 623 - Furnisher Responsibilities"]
            },
            "instructions": [
                "Send via Certified Mail with Return Receipt Requested",
                "Keep a copy for your records",
                "Send within 30 days of first contact for maximum protection",
                "If they cannot validate, request deletion from credit reports"
            ]
        }

    def _generate_bureau_dispute(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate credit bureau dispute letter under FCRA Section 611."""
        date = datetime.now().strftime("%B %d, %Y")
        bureau = dispute_info.get('bureau', 'Experian')
        bureau_info = self.bureau_addresses.get(bureau, self.bureau_addresses['Experian'])

        # Build dispute reasons
        dispute_reasons = dispute_info.get('reasons', ['Information is inaccurate'])
        reasons_text = "\n".join([f"• {reason}" for reason in dispute_reasons])

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}
SSN: XXX-XX-{user_info.get('ssn_last4', 'XXXX')}
DOB: {user_info.get('dob', '[DATE OF BIRTH]')}

{date}

{bureau_info['name']}
{bureau_info['address']}
{bureau_info['city']}

Re: Dispute of Inaccurate Credit Information

To Whom It May Concern:

I am writing to dispute the following inaccurate information on my credit report. I have reviewed my credit report and found the following item(s) to be inaccurate:

DISPUTED ACCOUNT:
Creditor Name: {dispute_info.get('creditor_name', '[CREDITOR NAME]')}
Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}
Reason for Dispute: {dispute_info.get('dispute_reason', '[REASON]')}

The information is inaccurate because:
{reasons_text}

Pursuant to the Fair Credit Reporting Act, 15 U.S.C. § 1681i (Section 611), I am requesting that you investigate this matter and correct the inaccurate information on my credit report.

Under the FCRA, you have 30 days to investigate my dispute and provide me with the results. If you cannot verify the accuracy of this information, you must delete it from my credit file.

I am also requesting, pursuant to FCRA Section 611(a)(7), that you provide me with the method of verification used if you determine the information is accurate.

Please send me written confirmation of the results of your investigation and an updated copy of my credit report reflecting any corrections made.

Enclosed please find:
• Copy of my driver's license
• Copy of my Social Security card
• Copy of a recent utility bill

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Enclosures: As stated

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Bureau Dispute",
            "content": letter,
            "target_bureau": bureau,
            "legal_basis": {
                "primary_law": "FCRA",
                "sections": [
                    "Section 611 - Dispute Procedures",
                    "15 U.S.C. § 1681i"
                ]
            },
            "instructions": [
                "Send via Certified Mail with Return Receipt Requested",
                "Include copies (not originals) of ID documents",
                "Keep detailed records of all correspondence",
                "Follow up if no response within 30 days",
                "Request method of verification if dispute is denied"
            ]
        }

    def _generate_furnisher_dispute(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate direct dispute letter to furnisher under FCRA Section 623."""
        date = datetime.now().strftime("%B %d, %Y")

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{dispute_info.get('creditor_name', '[CREDITOR NAME]')}
{dispute_info.get('creditor_address', '[CREDITOR ADDRESS]')}
{dispute_info.get('creditor_city_state_zip', '[CITY, STATE ZIP]')}

Re: Direct Dispute Pursuant to FCRA Section 623
    Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}

To Whom It May Concern:

I am writing to dispute information you are furnishing to the credit reporting agencies regarding the above-referenced account. This dispute is made directly to you as the furnisher of this information pursuant to the Fair Credit Reporting Act, 15 U.S.C. § 1681s-2 (Section 623).

DISPUTED INFORMATION:
{dispute_info.get('disputed_info', '[DESCRIPTION OF INACCURATE INFORMATION]')}

REASON FOR DISPUTE:
{dispute_info.get('dispute_reason', '[REASON THE INFORMATION IS INACCURATE]')}

Under FCRA Section 623(b), upon receiving notice of a dispute from a consumer, you must:

1. Conduct an investigation with respect to the disputed information
2. Review all relevant information provided by the consumer
3. Report the results of the investigation to the consumer
4. If the investigation reveals inaccuracy, report those results to all credit reporting agencies

I have enclosed documentation supporting my dispute. Please investigate this matter and correct any inaccurate information you are reporting.

Additionally, please cease reporting any inaccurate information while your investigation is pending, as continued reporting of information you know to be disputed without notation would violate FCRA Section 623(a)(3).

If you are unable to verify the accuracy of the disputed information, please:
1. Delete the information from your records
2. Report the deletion to all credit reporting agencies

Please provide written confirmation of your investigation results within 30 days.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Enclosures: [List supporting documents]

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Furnisher Dispute",
            "content": letter,
            "legal_basis": {
                "primary_law": "FCRA",
                "sections": [
                    "Section 623 - Responsibilities of Furnishers",
                    "15 U.S.C. § 1681s-2"
                ]
            },
            "instructions": [
                "Send after first disputing with credit bureau",
                "Include any supporting documentation",
                "This creates additional legal liability for the furnisher",
                "Keep copies of everything"
            ]
        }

    def _generate_cease_desist(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate cease and desist letter under FDCPA Section 805."""
        date = datetime.now().strftime("%B %d, %Y")

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{dispute_info.get('collector_name', '[COLLECTION AGENCY NAME]')}
{dispute_info.get('collector_address', '[COLLECTION AGENCY ADDRESS]')}
{dispute_info.get('collector_city_state_zip', '[CITY, STATE ZIP]')}

Re: CEASE AND DESIST - Account #{dispute_info.get('account_number', '[ACCOUNT NUMBER]')}

To Whom It May Concern:

Pursuant to my rights under the Fair Debt Collection Practices Act, 15 U.S.C. § 1692c(c) (Section 805(c)), I hereby demand that you cease all communication with me regarding the above-referenced account.

This is not a refusal to pay, nor is it an acknowledgment that I owe this alleged debt. This is a formal notice that you must stop all collection communications.

Under the FDCPA, after receiving this notice, you may only contact me to:
1. Advise me that collection efforts are being terminated
2. Notify me of specific legal action you intend to take
3. Notify me that you are actually taking specific legal action

Any communication beyond these limited purposes will be considered a violation of federal law. I am aware of my rights and will document any violations for potential legal action.

If you have previously contacted my employer, family members, or third parties, be advised that such contact was a violation of FDCPA Section 805(b), 15 U.S.C. § 1692c(b), which prohibits communication with third parties.

This letter is being sent via certified mail, and I am keeping a copy for my records. Any violation of this cease and desist demand will be used as evidence of willful noncompliance with federal law.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Cease and Desist",
            "content": letter,
            "legal_basis": {
                "primary_law": "FDCPA",
                "sections": [
                    "Section 805(c) - Ceasing Communication",
                    "15 U.S.C. § 1692c(c)"
                ]
            },
            "instructions": [
                "Send via Certified Mail with Return Receipt Requested",
                "Document all contact after sending this letter",
                "Note: This does not eliminate the debt",
                "Creditor may still sue to collect",
                "Best used for very old debts near statute of limitations"
            ],
            "warnings": [
                "May result in lawsuit if creditor decides to pursue legal action",
                "Consider negotiating before sending if you can afford to pay"
            ]
        }

    def _generate_goodwill_deletion(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate goodwill deletion request letter."""
        date = datetime.now().strftime("%B %d, %Y")

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{dispute_info.get('creditor_name', '[CREDITOR NAME]')}
Customer Service Department
{dispute_info.get('creditor_address', '[CREDITOR ADDRESS]')}
{dispute_info.get('creditor_city_state_zip', '[CITY, STATE ZIP]')}

Re: Goodwill Adjustment Request
    Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}

Dear Customer Service Manager,

I am writing to request a goodwill adjustment to remove a late payment entry from my credit report. I have been a loyal customer of {dispute_info.get('creditor_name', '[CREDITOR NAME]')} and value our business relationship.

ACCOUNT DETAILS:
Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}
Late Payment Date: {dispute_info.get('late_date', '[DATE OF LATE PAYMENT]')}

EXPLANATION:
{dispute_info.get('explanation', '''[EXPLAIN THE CIRCUMSTANCES THAT LED TO THE LATE PAYMENT - be honest and take responsibility while explaining any extenuating circumstances such as:
- Job loss or reduction in income
- Medical emergency or illness
- Family emergency
- Billing error or technical issue
- Natural disaster
- Military deployment]''')}

Since this incident, I have:
- Made all payments on time
- Set up automatic payments to prevent future issues
- Maintained a positive account history

I understand that you are under no obligation to make this adjustment, and that the late payment was ultimately my responsibility. However, I am respectfully asking for your consideration given my overall positive history with your company.

This late payment entry is significantly impacting my credit score and my ability to {dispute_info.get('goal', '[obtain favorable mortgage rates, refinance, etc.]')}. A goodwill removal would greatly help me achieve my financial goals.

I would be deeply grateful for your consideration of this request. Please let me know if you need any additional information.

Thank you for your time and for your excellent service over the years.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}
Phone: {user_info.get('phone', '[YOUR PHONE]')}
Email: {user_info.get('email', '[YOUR EMAIL]')}
"""

        return {
            "type": "Goodwill Deletion Request",
            "content": letter,
            "legal_basis": {
                "primary_law": "None - This is a courtesy request",
                "notes": "There is no legal requirement for creditors to honor goodwill requests"
            },
            "instructions": [
                "Only send after the account is current or paid",
                "Be polite and take responsibility",
                "Explain your circumstances honestly",
                "Mention your positive history with the company",
                "May need to send multiple times or try different departments",
                "Consider calling first to build rapport"
            ],
            "tips": [
                "Executive email carpet bomb - send to multiple executives",
                "Be persistent but polite",
                "Try calling customer retention department",
                "Success rate is higher with credit unions and smaller banks"
            ]
        }

    def _generate_pay_for_delete(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate pay for delete negotiation letter."""
        date = datetime.now().strftime("%B %d, %Y")

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{dispute_info.get('collector_name', '[COLLECTION AGENCY NAME]')}
{dispute_info.get('collector_address', '[COLLECTION AGENCY ADDRESS]')}
{dispute_info.get('collector_city_state_zip', '[CITY, STATE ZIP]')}

Re: Settlement Offer - Account #{dispute_info.get('account_number', '[ACCOUNT NUMBER]')}
    Alleged Balance: ${dispute_info.get('amount', '[AMOUNT]')}

CONFIDENTIAL SETTLEMENT COMMUNICATION

To Whom It May Concern:

This letter is an attempt to resolve the above-referenced account. This is not an acknowledgment that I owe this debt, nor is it a promise to pay without a proper agreement.

SETTLEMENT OFFER:
I am prepared to pay ${dispute_info.get('offer_amount', '[SETTLEMENT AMOUNT]')} as payment in full to resolve this account, contingent upon the following conditions:

1. DELETION FROM CREDIT REPORTS: Upon receipt of payment, you agree to request deletion of this account from all three credit bureaus (Experian, Equifax, and TransUnion) within 30 days.

2. WRITTEN AGREEMENT: Before I submit payment, you must provide written agreement to these terms on your company letterhead.

3. PAYMENT METHOD: Payment will be made via {dispute_info.get('payment_method', 'certified check/money order')} only after receipt of the written agreement.

4. RELEASE OF LIABILITY: Upon payment, you agree to release me from any further obligation on this account.

If you agree to these terms, please send a written agreement signed by an authorized representative. The agreement must include:
- The settlement amount
- Confirmation of credit bureau deletion
- Statement that this is payment in full
- Your commitment not to sell or transfer this debt

This offer is valid for 15 days from the date of this letter. If I do not receive a written acceptance by then, this offer is withdrawn.

Please note that this letter may not be used as evidence of acknowledgment of the debt or as a promise to pay without the requested written agreement.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Pay for Delete",
            "content": letter,
            "legal_basis": {
                "notes": "Pay for delete is not illegal but collectors are not required to agree"
            },
            "instructions": [
                "Only send if you have the settlement amount available",
                "ALWAYS get written agreement BEFORE paying",
                "Never pay via methods that can't be traced",
                "Keep all correspondence",
                "Follow up to ensure deletion occurs"
            ],
            "warnings": [
                "Some collectors will not agree to deletion",
                "Paying may reset statute of limitations in some states",
                "Settling for less may result in 1099-C for forgiven debt"
            ]
        }

    def _generate_mov_request(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate method of verification request under FCRA Section 611(a)(7)."""
        date = datetime.now().strftime("%B %d, %Y")
        bureau = dispute_info.get('bureau', 'Experian')
        bureau_info = self.bureau_addresses.get(bureau, self.bureau_addresses['Experian'])

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{bureau_info['name']}
{bureau_info['address']}
{bureau_info['city']}

Re: Method of Verification Request - Previous Dispute
    Your Reference Number: {dispute_info.get('dispute_reference', '[DISPUTE REFERENCE NUMBER]')}

To Whom It May Concern:

On {dispute_info.get('original_dispute_date', '[DATE]')}, I submitted a dispute regarding inaccurate information on my credit report. You have responded that the disputed information was verified as accurate.

Pursuant to the Fair Credit Reporting Act, 15 U.S.C. § 1681i(a)(7) (Section 611(a)(7)), I hereby request that you provide me with the method of verification used to determine that the disputed information is accurate.

DISPUTED ACCOUNT:
Creditor Name: {dispute_info.get('creditor_name', '[CREDITOR NAME]')}
Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}
Your Investigation Reference: {dispute_info.get('dispute_reference', '[REFERENCE NUMBER]')}

Specifically, I request:
1. The name, address, and telephone number of any person contacted in connection with this investigation
2. The method used to verify the information
3. All documentation obtained during the investigation
4. The specific evidence that led to your conclusion

Under Section 611(a)(7), you are required to provide this information upon request. Failure to provide the method of verification is a violation of the FCRA.

Please respond within 15 days of receipt of this letter.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Method of Verification Request",
            "content": letter,
            "target_bureau": bureau,
            "legal_basis": {
                "primary_law": "FCRA",
                "sections": [
                    "Section 611(a)(7) - Method of Verification",
                    "15 U.S.C. § 1681i(a)(7)"
                ]
            },
            "instructions": [
                "Send after receiving dispute results that verify the information",
                "This often reveals that only automated verification was used",
                "Useful for building a case if further action is needed",
                "Many bureaus fail to properly respond, creating FCRA violations"
            ]
        }

    def _generate_intent_to_sue(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate intent to sue letter for FCRA/FDCPA violations."""
        date = datetime.now().strftime("%B %d, %Y")

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

VIA CERTIFIED MAIL

{dispute_info.get('defendant_name', '[COMPANY NAME]')}
{dispute_info.get('defendant_address', '[COMPANY ADDRESS]')}
{dispute_info.get('defendant_city_state_zip', '[CITY, STATE ZIP]')}

Re: Notice of Intent to File Lawsuit
    Account Reference: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}

FINAL DEMAND BEFORE LITIGATION

To Whom It May Concern:

This letter serves as formal notice of my intent to file a lawsuit against your company for violations of federal consumer protection laws.

BACKGROUND:
{dispute_info.get('background', '[BRIEF DESCRIPTION OF THE SITUATION AND YOUR PREVIOUS ATTEMPTS TO RESOLVE]')}

VIOLATIONS:
{dispute_info.get('violations', '''[LIST SPECIFIC VIOLATIONS, FOR EXAMPLE:
- Failure to conduct reasonable investigation under FCRA § 1681i
- Reporting information known to be inaccurate under FCRA § 1681s-2
- Failure to validate debt under FDCPA § 1692g
- Continued collection on disputed debt under FDCPA § 1692g(b)]''')}

DAMAGES SOUGHT:
Under the Fair Credit Reporting Act, 15 U.S.C. § 1681n (willful noncompliance), I am entitled to:
- Actual damages
- Statutory damages of $100 to $1,000 per violation
- Punitive damages
- Attorney's fees and costs

Under the Fair Debt Collection Practices Act, 15 U.S.C. § 1692k, I am entitled to:
- Actual damages
- Statutory damages up to $1,000
- Attorney's fees and costs

DEMAND:
To resolve this matter without litigation, I demand:
{dispute_info.get('demands', '''[YOUR DEMANDS, FOR EXAMPLE:
1. Immediate deletion of the inaccurate information from all credit reports
2. Written confirmation of deletion within 10 days
3. Monetary compensation of $X for damages suffered]''')}

DEADLINE:
If I do not receive a satisfactory response within 15 days of your receipt of this letter, I will proceed with filing a lawsuit in [federal/state] court and will seek all available damages, including attorney's fees.

I am consulting with a consumer protection attorney and am fully prepared to pursue this matter through litigation. This is your final opportunity to resolve this matter before I incur significant legal fees, which I will seek to recover from you.

Govern yourself accordingly.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Intent to Sue",
            "content": letter,
            "legal_basis": {
                "primary_laws": ["FCRA", "FDCPA"],
                "sections": [
                    "FCRA Section 616-617 - Civil Liability",
                    "15 U.S.C. § 1681n, § 1681o",
                    "FDCPA Section 813 - Civil Liability",
                    "15 U.S.C. § 1692k"
                ]
            },
            "instructions": [
                "Only send if you have documented violations",
                "Consult with a consumer protection attorney before sending",
                "Be prepared to follow through with lawsuit",
                "Many companies settle after receiving this letter",
                "Keep all documentation of violations"
            ],
            "next_steps": [
                "If no response, file complaint with CFPB",
                "Consider small claims court for smaller amounts",
                "Consult NACA (National Association of Consumer Advocates) for attorney referral",
                "Many consumer attorneys work on contingency"
            ]
        }

    def _generate_identity_theft(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate identity theft dispute letter."""
        date = datetime.now().strftime("%B %d, %Y")
        bureau = dispute_info.get('bureau', 'Experian')
        bureau_info = self.bureau_addresses.get(bureau, self.bureau_addresses['Experian'])

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}

{date}

{bureau_info['name']}
{bureau_info['address']}
{bureau_info['city']}

Re: Identity Theft Dispute - Block of Information
    FTC Identity Theft Report Number: {dispute_info.get('ftc_report', '[FTC REPORT NUMBER]')}

To Whom It May Concern:

I am a victim of identity theft and am writing to dispute fraudulent information on my credit report. Pursuant to the Fair Credit Reporting Act, 15 U.S.C. § 1681c-2 (FCRA Section 605B), I request that you block the following fraudulent information resulting from identity theft:

FRAUDULENT ACCOUNTS:
{dispute_info.get('fraudulent_accounts', '''[LIST EACH FRAUDULENT ACCOUNT:
1. Creditor: [NAME], Account #: [NUMBER]
2. Creditor: [NAME], Account #: [NUMBER]]''')}

I have enclosed:
1. A copy of my FTC Identity Theft Report
2. A copy of my government-issued photo ID
3. Proof of my address
4. My Identity Theft Affidavit

Under FCRA Section 605B, you must:
1. Block this information from appearing on my credit report within 4 business days
2. Notify the furnisher of the block
3. Not allow the blocked information to reappear

Additionally, I request that you place an extended fraud alert on my file pursuant to FCRA Section 605A(b), which will remain for 7 years.

Please send written confirmation when the fraudulent information has been blocked.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Enclosures:
- FTC Identity Theft Report
- Copy of driver's license
- Utility bill showing current address
- Identity Theft Affidavit

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Identity Theft Dispute",
            "content": letter,
            "target_bureau": bureau,
            "legal_basis": {
                "primary_law": "FCRA",
                "sections": [
                    "Section 605B - Block of Information Resulting from Identity Theft",
                    "15 U.S.C. § 1681c-2",
                    "Section 605A - Fraud Alerts",
                    "15 U.S.C. § 1681c-1"
                ]
            },
            "instructions": [
                "First file report at IdentityTheft.gov to get FTC report",
                "File police report (may be required by some creditors)",
                "Send to all three bureaus",
                "Also send dispute to each fraudulent creditor",
                "Consider credit freeze for additional protection"
            ]
        }

    def _generate_late_payment_removal(self, user_info: dict, dispute_info: dict, target: str) -> dict:
        """Generate late payment dispute letter."""
        date = datetime.now().strftime("%B %d, %Y")
        bureau = dispute_info.get('bureau', 'Experian')
        bureau_info = self.bureau_addresses.get(bureau, self.bureau_addresses['Experian'])

        letter = f"""{user_info.get('name', '[YOUR NAME]')}
{user_info.get('address', '[YOUR ADDRESS]')}
{user_info.get('city_state_zip', '[CITY, STATE ZIP]')}
SSN: XXX-XX-{user_info.get('ssn_last4', 'XXXX')}

{date}

{bureau_info['name']}
{bureau_info['address']}
{bureau_info['city']}

Re: Dispute of Late Payment - FCRA Section 611

To Whom It May Concern:

I am writing to dispute a late payment entry on my credit report that I believe is inaccurate.

DISPUTED ACCOUNT:
Creditor Name: {dispute_info.get('creditor_name', '[CREDITOR NAME]')}
Account Number: {dispute_info.get('account_number', '[ACCOUNT NUMBER]')}
Date of Alleged Late Payment: {dispute_info.get('late_date', '[DATE]')}

REASON FOR DISPUTE:
{dispute_info.get('reason', '''[SELECT OR CUSTOMIZE REASON:
• Payment was made on time but posted late due to creditor processing error
• Payment was made within the grace period
• I never received a statement/bill for this period
• The payment was applied to wrong account
• This late payment resulted from creditor's billing error
• I have proof of timely payment (bank statement, canceled check, etc.)]''')}

Pursuant to the Fair Credit Reporting Act, 15 U.S.C. § 1681i, please investigate this dispute. I believe a thorough investigation will reveal that this late payment is being reported in error.

If you verify with the furnisher, please require them to provide actual documentation of the late payment, not just automated verification. Under FCRA Section 611(a)(1)(A), you must conduct a reasonable investigation.

{dispute_info.get('enclosed_docs', '[IF YOU HAVE PROOF: I have enclosed copies of bank statements/canceled checks showing timely payment.]')}

Please send me written results of your investigation within 30 days.

Sincerely,


{user_info.get('name', '[YOUR NAME]')}

Sent via Certified Mail, Return Receipt Requested
"""

        return {
            "type": "Late Payment Dispute",
            "content": letter,
            "target_bureau": bureau,
            "legal_basis": {
                "primary_law": "FCRA",
                "sections": [
                    "Section 611 - Dispute Procedures",
                    "15 U.S.C. § 1681i"
                ]
            },
            "instructions": [
                "Gather any proof of timely payment before sending",
                "Check bank statements for payment dates",
                "Late payments within 30 days hurt less than 60-90 day lates",
                "If dispute fails, try goodwill letter to creditor"
            ]
        }

    def get_all_letter_types(self) -> list:
        """Get list of all available letter types."""
        return [
            {"type": "debt_validation", "name": "Debt Validation", "use_for": "Collection accounts"},
            {"type": "bureau_dispute", "name": "Credit Bureau Dispute", "use_for": "Any inaccurate item"},
            {"type": "furnisher_dispute", "name": "Direct Furnisher Dispute", "use_for": "After bureau dispute"},
            {"type": "cease_desist", "name": "Cease and Desist", "use_for": "Stop collector contact"},
            {"type": "goodwill_deletion", "name": "Goodwill Deletion", "use_for": "Paid accounts with late payments"},
            {"type": "pay_for_delete", "name": "Pay for Delete", "use_for": "Negotiate collection removal"},
            {"type": "method_of_verification", "name": "Method of Verification", "use_for": "After dispute verified"},
            {"type": "intent_to_sue", "name": "Intent to Sue", "use_for": "Document violations first"},
            {"type": "identity_theft", "name": "Identity Theft Dispute", "use_for": "Fraudulent accounts"},
            {"type": "late_payment_removal", "name": "Late Payment Dispute", "use_for": "Incorrect late payments"}
        ]
