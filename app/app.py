"""
EchoDispute - Credit Repair Autopilot
Flask application for generating credit dispute letters
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
import stripe
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import io

from services.letter_templates import (
    get_dispute_letter_prompt,
    get_followup_letter_prompt,
    get_mailing_instructions,
    get_faq_document,
    get_bureau_address
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize APIs
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Configuration
PRICE_AMOUNT = 7500  # $75.00 in cents
DOMAIN = os.environ.get('DOMAIN', 'http://localhost:5000')


@app.route('/')
def index():
    """Serve the landing page"""
    return render_template('index.html')


@app.route('/api/create-checkout', methods=['POST'])
def create_checkout():
    """Create a Stripe Checkout session"""
    try:
        user_data = request.json

        # Store user data temporarily (in production, use database)
        # For MVP, we'll pass it through metadata
        metadata = {
            'user_data': json.dumps(user_data)
        }

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': PRICE_AMOUNT,
                    'product_data': {
                        'name': 'Credit Dispute Letter Package',
                        'description': f'Personalized dispute letters for {len(user_data["bureaus"])} credit bureau(s)',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=DOMAIN + '/?canceled=true',
            customer_email=user_data['email'],
            metadata=metadata,
        )

        return jsonify({'checkout_url': checkout_session.url})

    except Exception as e:
        print(f"Error creating checkout: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/success')
def success():
    """Handle successful payment and generate letters"""
    session_id = request.args.get('session_id')

    if not session_id:
        return "Invalid session", 400

    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == 'paid':
            # Get user data from metadata
            user_data = json.loads(session.metadata['user_data'])

            # Generate letters
            letters = generate_all_letters(user_data)

            # Generate PDF
            pdf_buffer = create_pdf_package(user_data, letters)

            # Send email with PDF (TODO: implement email sending)
            # For now, return success page with download link

            # Store PDF temporarily (in production, use S3 or similar)
            pdf_filename = f"dispute_letters_{session_id}.pdf"
            pdf_path = f"/tmp/{pdf_filename}"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())

            return render_template('success.html',
                                 email=user_data['email'],
                                 download_url=f'/download/{session_id}')
        else:
            return "Payment not completed", 400

    except Exception as e:
        print(f"Error processing success: {e}")
        return f"Error: {str(e)}", 500


@app.route('/download/<session_id>')
def download(session_id):
    """Download the generated PDF"""
    try:
        # Retrieve session to verify payment
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status != 'paid':
            return "Unauthorized", 403

        # Get the PDF file
        pdf_path = f"/tmp/dispute_letters_{session_id}.pdf"

        if not os.path.exists(pdf_path):
            # Regenerate if needed
            user_data = json.loads(session.metadata['user_data'])
            letters = generate_all_letters(user_data)
            pdf_buffer = create_pdf_package(user_data, letters)

            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())

        return send_file(pdf_path,
                        as_attachment=True,
                        download_name=f'credit_dispute_letters_{datetime.now().strftime("%Y%m%d")}.pdf',
                        mimetype='application/pdf')

    except Exception as e:
        print(f"Error downloading file: {e}")
        return f"Error: {str(e)}", 500


def generate_all_letters(user_data):
    """Generate personalized letters for all selected bureaus"""
    letters = {}

    for bureau in user_data['bureaus']:
        # Generate dispute letter using GPT
        prompt = get_dispute_letter_prompt(user_data, bureau)

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional credit dispute letter writer with expertise in FCRA compliance."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        letter_content = response.choices[0].message.content

        # Generate follow-up letter
        original_date = datetime.now().strftime("%B %d, %Y")
        followup_prompt = get_followup_letter_prompt(user_data, bureau, original_date)

        followup_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional credit dispute letter writer with expertise in FCRA compliance."},
                {"role": "user", "content": followup_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        followup_content = followup_response.choices[0].message.content

        letters[bureau] = {
            'dispute_letter': letter_content,
            'followup_letter': followup_content
        }

    return letters


def create_pdf_package(user_data, letters):
    """Create a PDF package with all letters and instructions"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=inch, leftMargin=inch,
                          topMargin=inch, bottomMargin=inch)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#4F46E5',
        spaceAfter=12,
        alignment=1  # Center
    )

    # Cover page
    elements.append(Paragraph("Credit Dispute Letter Package", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"Prepared for: {user_data['firstName']} {user_data['lastName']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("This package contains:", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    bureau_count = len(user_data['bureaus'])
    checklist = f"""
    ✓ {bureau_count} Personalized Dispute Letter(s)<br/>
    ✓ {bureau_count} Follow-up Letter Template(s)<br/>
    ✓ Mailing Instructions<br/>
    ✓ FAQ and Tips for Success
    """
    elements.append(Paragraph(checklist, styles['Normal']))
    elements.append(PageBreak())

    # Add dispute letters
    for bureau, content in letters.items():
        elements.append(Paragraph(f"Dispute Letter - {bureau}", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        # Split letter content into paragraphs
        for para in content['dispute_letter'].split('\n\n'):
            if para.strip():
                elements.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))

        elements.append(PageBreak())

    # Add follow-up letters
    for bureau, content in letters.items():
        elements.append(Paragraph(f"Follow-Up Letter - {bureau}", styles['Heading1']))
        elements.append(Paragraph("(Use this if no response after 30 days)", styles['Italic']))
        elements.append(Spacer(1, 0.2*inch))

        for para in content['followup_letter'].split('\n\n'):
            if para.strip():
                elements.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))

        elements.append(PageBreak())

    # Add mailing instructions
    elements.append(Paragraph("Mailing Instructions", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))
    instructions = get_mailing_instructions()
    for para in instructions.split('\n\n'):
        if para.strip():
            elements.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

    elements.append(PageBreak())

    # Add FAQ
    elements.append(Paragraph("Frequently Asked Questions", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))
    faq = get_faq_document()
    for para in faq.split('\n\n'):
        if para.strip():
            elements.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # TODO: Send email with PDF
            print(f"Payment completed for {session['customer_email']}")

        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    # For development only
    app.run(debug=True, host='0.0.0.0', port=5000)
