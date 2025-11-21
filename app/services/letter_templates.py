"""
Credit Dispute Letter Templates
These templates are used as base structures for GPT to personalize
"""

def get_dispute_letter_prompt(user_data, bureau):
    """Generate a prompt for GPT to create a personalized dispute letter"""

    prompt = f"""You are a professional credit dispute letter writer. Generate a formal, legally-compliant credit dispute letter based on the following information:

SENDER INFORMATION:
- Name: {user_data['firstName']} {user_data['lastName']}
- Address: {user_data['address']}, {user_data['city']}, {user_data['state']} {user_data['zip']}
- Date of Birth: {user_data['dob']}
- Last 4 of SSN: {user_data['ssn']}

CREDIT BUREAU:
- {bureau}

DISPUTE DETAILS:
- Type of Error: {user_data['disputeType']}
- Creditor/Company: {user_data['creditorName']}
- Account Number (last 4): {user_data.get('accountNumber', 'N/A')}
- Error Description: {user_data['errorDetails']}

INSTRUCTIONS:
1. Write a professional, formal letter that follows FCRA (Fair Credit Reporting Act) guidelines
2. Be assertive but respectful
3. Clearly identify the error and request investigation and correction
4. Reference the consumer's rights under federal law
5. Request written confirmation of the investigation results
6. Include a statement requesting deletion if the information cannot be verified
7. Use professional business letter format with proper date and bureau address
8. Keep the tone factual and focused on the specific error
9. Do NOT include threats or emotional language
10. Do NOT make up facts not provided in the user data

The letter should be ready to print and mail. Include the proper bureau address at the top.

CREDIT BUREAU ADDRESSES:
- Equifax: Equifax Information Services LLC, P.O. Box 740256, Atlanta, GA 30374
- Experian: Experian, P.O. Box 4500, Allen, TX 75013
- TransUnion: TransUnion LLC, Consumer Dispute Center, P.O. Box 2000, Chester, PA 19016

Generate the complete letter now:"""

    return prompt


def get_followup_letter_prompt(user_data, bureau, original_dispute_date):
    """Generate a follow-up letter if no response after 30 days"""

    prompt = f"""You are a professional credit dispute letter writer. Generate a FOLLOW-UP credit dispute letter for a case where the credit bureau did not respond to the original dispute within 30 days.

SENDER INFORMATION:
- Name: {user_data['firstName']} {user_data['lastName']}
- Address: {user_data['address']}, {user_data['city']}, {user_data['state']} {user_data['zip']}
- Date of Birth: {user_data['dob']}
- Last 4 of SSN: {user_data['ssn']}

CREDIT BUREAU:
- {bureau}

ORIGINAL DISPUTE:
- Sent on: {original_dispute_date}
- Creditor/Company: {user_data['creditorName']}
- Error Description: {user_data['errorDetails']}

INSTRUCTIONS:
1. Reference the original letter sent 30+ days ago
2. Note that under FCRA, bureaus must respond within 30 days
3. Firmly request immediate investigation and response
4. Cite specific FCRA violations (15 U.S.C. § 1681i)
5. Request deletion of the disputed information due to failure to verify within required timeframe
6. Mention potential complaint to CFPB (Consumer Financial Protection Bureau) if not resolved
7. Maintain professional tone but be more assertive than the first letter
8. Request written confirmation within 15 days

Generate the complete follow-up letter now:"""

    return prompt


def get_bureau_address(bureau):
    """Get the mailing address for each credit bureau"""
    addresses = {
        'Equifax': {
            'name': 'Equifax Information Services LLC',
            'street': 'P.O. Box 740256',
            'city': 'Atlanta',
            'state': 'GA',
            'zip': '30374'
        },
        'Experian': {
            'name': 'Experian',
            'street': 'P.O. Box 4500',
            'city': 'Allen',
            'state': 'TX',
            'zip': '75013'
        },
        'TransUnion': {
            'name': 'TransUnion LLC',
            'street': 'Consumer Dispute Center',
            'street2': 'P.O. Box 2000',
            'city': 'Chester',
            'state': 'PA',
            'zip': '19016'
        }
    }
    return addresses.get(bureau, {})


def get_mailing_instructions():
    """Return instructions for mailing the letters"""
    return """
MAILING INSTRUCTIONS FOR YOUR CREDIT DISPUTE LETTERS

1. PRINT YOUR LETTERS
   - Print on white 8.5" x 11" paper
   - Use a quality printer (no faded ink)
   - Print in black ink for professionalism

2. GATHER REQUIRED DOCUMENTS
   - Copy of your driver's license or state ID
   - Copy of a recent utility bill (shows your address)
   - Copy of Social Security card (optional but helpful)
   - Any supporting documents that prove your claim (bank statements, payment receipts, etc.)

3. PREPARE YOUR MAIL
   - Use white business envelopes (standard #10 size)
   - Write the bureau address clearly or print labels
   - Include your return address

4. SEND VIA CERTIFIED MAIL
   ⚠️ IMPORTANT: Send via USPS Certified Mail with Return Receipt Requested
   - This provides proof of delivery
   - Costs about $7-8 per letter
   - Keep the receipt and tracking number
   - Wait for the green return receipt card

5. KEEP RECORDS
   - Make copies of EVERYTHING before mailing
   - Keep certified mail receipts
   - Keep return receipt cards
   - Track the date you mailed each letter
   - Set a calendar reminder for 30 days out

6. WHAT TO EXPECT
   - Bureaus have 30 days to investigate (from date they receive your letter)
   - They will mail you their investigation results
   - If they remove the error, request a free updated credit report
   - If they don't respond in 30 days, use the follow-up letter included

7. IF YOU DON'T GET A RESPONSE
   - Wait 35 days from mailing (allows for mail time)
   - Send the follow-up letter (included in your package)
   - File a complaint with the CFPB: https://www.consumerfinance.gov/complaint/

TIPS FOR SUCCESS:
✓ Mail all letters on the same day
✓ Take photos of everything before mailing
✓ Be patient - the process takes time
✓ Don't dispute too many items at once
✓ Keep detailed records of all communications

NEED HELP?
Email us at support@echodispute.com with questions.
"""


def get_faq_document():
    """Return a helpful FAQ document to include with the package"""
    return """
FREQUENTLY ASKED QUESTIONS

Q: How long does the dispute process take?
A: Credit bureaus must investigate within 30 days of receiving your letter. Total time is typically 30-45 days including mail time.

Q: What happens after I mail my letters?
A: The credit bureaus will investigate your dispute by contacting the creditor. They will mail you their findings. If they can't verify the information, they must delete it.

Q: Do I need to mail to all three bureaus?
A: Yes, if the error appears on all three reports. Each bureau operates independently.

Q: What if the error isn't removed?
A: You can:
   1. Submit additional documentation
   2. Dispute directly with the creditor
   3. Request a statement of dispute be added to your report
   4. File a complaint with the CFPB

Q: Can I dispute multiple errors at once?
A: Yes, but it's more effective to focus on one error per letter. If you have multiple errors, consider purchasing additional packages.

Q: Will disputing hurt my credit score?
A: No. The dispute process itself does not affect your credit score. However, if an error is removed, your score may improve.

Q: What if the bureau asks for more information?
A: Respond promptly with any requested documentation. The 30-day clock may restart.

Q: Can I dispute the same item twice?
A: Yes, if you have new information or if the bureau's investigation was inadequate.

Q: Is this legal?
A: Absolutely. Disputing credit report errors is your right under the Fair Credit Reporting Act (FCRA).

Q: What should I do if my dispute is rejected?
A: 1. Request the method of verification
   2. Contact the creditor directly
   3. Escalate to CFPB
   4. Consider consulting with a consumer attorney

ADDITIONAL RESOURCES:
- Consumer Financial Protection Bureau: www.consumerfinance.gov
- Annual Credit Report: www.annualcreditreport.com (free reports)
- FTC Credit Repair: www.consumer.ftc.gov/articles/0225-credit-repair-how-help-yourself

Remember: Patience and documentation are key to successful disputes.
"""
