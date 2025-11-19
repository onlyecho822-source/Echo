"""
Guide to Being Wealthy - Main Application
==========================================
Credit Repair & Financial Advancement Platform
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .credit_parser import CreditReportParser
from .letter_generator import DisputeLetterGenerator
from .legal_knowledge import LegalKnowledgeBase
from .trust_fund import TrustFundGuide
from .calculators import FinancialCalculators

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Credit Repair & Financial Advancement Platform - Your Guide to Being Wealthy",
    version=settings.APP_VERSION
)

# Create directories
Path("uploads").mkdir(exist_ok=True)
Path("app/templates").mkdir(exist_ok=True)
Path("app/static").mkdir(exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services
credit_parser = CreditReportParser()
letter_generator = DisputeLetterGenerator()
legal_kb = LegalKnowledgeBase()
trust_guide = TrustFundGuide()
calculators = FinancialCalculators()


# ========== Web Routes ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": settings.APP_NAME
    })


@app.get("/credit-analysis", response_class=HTMLResponse)
async def credit_analysis_page(request: Request):
    """Credit report analysis page."""
    return templates.TemplateResponse("credit_analysis.html", {
        "request": request,
        "title": "Credit Report Analysis"
    })


@app.get("/dispute-letters", response_class=HTMLResponse)
async def dispute_letters_page(request: Request):
    """Dispute letter generator page."""
    letter_types = letter_generator.get_all_letter_types()
    return templates.TemplateResponse("dispute_letters.html", {
        "request": request,
        "title": "Dispute Letter Generator",
        "letter_types": letter_types
    })


@app.get("/legal-guide", response_class=HTMLResponse)
async def legal_guide_page(request: Request):
    """Legal knowledge base page."""
    return templates.TemplateResponse("legal_guide.html", {
        "request": request,
        "title": "Credit Law Guide",
        "us_laws": legal_kb.us_laws,
        "international_laws": legal_kb.international_laws,
        "consumer_rights": legal_kb.get_consumer_rights_summary()
    })


@app.get("/trust-funds", response_class=HTMLResponse)
async def trust_funds_page(request: Request):
    """Trust fund guidance page."""
    return templates.TemplateResponse("trust_funds.html", {
        "request": request,
        "title": "Trust Fund Planning",
        "trust_types": trust_guide.trust_types
    })


@app.get("/wealth-calculator", response_class=HTMLResponse)
async def wealth_calculator_page(request: Request):
    """Wealth building calculator page."""
    return templates.TemplateResponse("wealth_calculator.html", {
        "request": request,
        "title": "Wealth Building Calculator"
    })


@app.get("/financial-position", response_class=HTMLResponse)
async def financial_position_page(request: Request):
    """Financial position assessment page."""
    return templates.TemplateResponse("financial_position.html", {
        "request": request,
        "title": "Financial Position Assessment"
    })


# ========== API Routes ==========

@app.post("/api/upload-credit-report")
async def upload_credit_report(file: UploadFile = File(...)):
    """Upload and analyze a credit report."""
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}")

    # Save file
    file_path = settings.UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Parse credit report
        result = credit_parser.parse_file(str(file_path))

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "analysis": result
        })
    except Exception as e:
        raise HTTPException(500, f"Error analyzing report: {str(e)}")
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()


@app.post("/api/generate-letter")
async def generate_letter(
    letter_type: str = Form(...),
    user_name: str = Form(...),
    user_address: str = Form(...),
    user_city_state_zip: str = Form(...),
    creditor_name: str = Form(None),
    account_number: str = Form(None),
    dispute_reason: str = Form(None),
    bureau: str = Form("Experian"),
    additional_info: str = Form(None)
):
    """Generate a dispute letter."""
    user_info = {
        "name": user_name,
        "address": user_address,
        "city_state_zip": user_city_state_zip
    }

    dispute_info = {
        "creditor_name": creditor_name,
        "account_number": account_number,
        "dispute_reason": dispute_reason,
        "bureau": bureau,
        "reasons": [dispute_reason] if dispute_reason else []
    }

    if additional_info:
        dispute_info["additional_info"] = additional_info

    letter = letter_generator.generate_letter(letter_type, user_info, dispute_info)

    return JSONResponse({
        "success": True,
        "letter": letter
    })


@app.get("/api/legal-info/{law_code}")
async def get_legal_info(law_code: str):
    """Get information about a specific law."""
    law_info = legal_kb.get_law(law_code)
    if not law_info:
        raise HTTPException(404, f"Law not found: {law_code}")

    return JSONResponse({
        "success": True,
        "law": law_info
    })


@app.get("/api/consumer-rights")
async def get_consumer_rights():
    """Get summary of consumer rights."""
    return JSONResponse({
        "success": True,
        "rights": legal_kb.get_consumer_rights_summary()
    })


@app.get("/api/statute-of-limitations")
async def get_statute_of_limitations(state: Optional[str] = None):
    """Get statute of limitations information."""
    return JSONResponse({
        "success": True,
        "limitations": legal_kb.get_statute_of_limitations(state)
    })


@app.post("/api/trust-recommendation")
async def get_trust_recommendation(
    net_worth: float = Form(...),
    has_minor_children: bool = Form(False),
    has_disabled_dependent: bool = Form(False),
    owns_business: bool = Form(False),
    owns_real_estate: bool = Form(False),
    charitable_intent: bool = Form(False),
    asset_protection_needed: bool = Form(False)
):
    """Get trust fund recommendations based on profile."""
    profile = {
        "net_worth": net_worth,
        "has_minor_children": has_minor_children,
        "has_disabled_dependent": has_disabled_dependent,
        "owns_business": owns_business,
        "owns_real_estate": owns_real_estate,
        "charitable_intent": charitable_intent,
        "asset_protection_needed": asset_protection_needed
    }

    recommendations = trust_guide.get_trust_recommendation(profile)

    return JSONResponse({
        "success": True,
        "recommendations": recommendations
    })


@app.get("/api/trust-checklist/{trust_type}")
async def get_trust_checklist(trust_type: str):
    """Get creation checklist for a trust type."""
    checklist = trust_guide.get_trust_creation_checklist(trust_type)
    return JSONResponse({
        "success": True,
        "checklist": checklist
    })


@app.post("/api/calculate-wealth-projection")
async def calculate_wealth_projection(
    daily_amount: float = Form(...),
    years: int = Form(...),
    annual_return: float = Form(0.07),
    initial_amount: float = Form(0)
):
    """Calculate wealth projection with compound growth."""
    projection = calculators.custom_wealth_projection(
        daily_amount=daily_amount,
        years=years,
        annual_return=annual_return,
        initial_amount=initial_amount
    )

    return JSONResponse({
        "success": True,
        "projection": projection
    })


@app.get("/api/dollar-a-day/{years}")
async def dollar_a_day_projection(years: int = 40):
    """Show the power of $1/day investing."""
    projection = calculators.dollar_a_day_projection(years)
    return JSONResponse({
        "success": True,
        "projection": projection
    })


@app.post("/api/calculate-net-worth")
async def calculate_net_worth(
    # Assets
    cash_savings: float = Form(0),
    checking_accounts: float = Form(0),
    investments: float = Form(0),
    retirement_accounts: float = Form(0),
    real_estate_equity: float = Form(0),
    vehicle_value: float = Form(0),
    other_assets: float = Form(0),
    # Liabilities
    mortgage: float = Form(0),
    auto_loans: float = Form(0),
    student_loans: float = Form(0),
    credit_card_debt: float = Form(0),
    personal_loans: float = Form(0),
    other_debt: float = Form(0)
):
    """Calculate net worth and financial position."""
    assets = {
        "cash_savings": cash_savings,
        "checking_accounts": checking_accounts,
        "investments": investments,
        "retirement_accounts": retirement_accounts,
        "real_estate_equity": real_estate_equity,
        "vehicle_value": vehicle_value,
        "other_assets": other_assets
    }

    liabilities = {
        "mortgage": mortgage,
        "auto_loans": auto_loans,
        "student_loans": student_loans,
        "credit_card_debt": credit_card_debt,
        "personal_loans": personal_loans,
        "other_debt": other_debt
    }

    result = calculators.calculate_net_worth(assets, liabilities)

    return JSONResponse({
        "success": True,
        "result": result
    })


@app.post("/api/calculate-wealth-score")
async def calculate_wealth_score(
    net_worth: float = Form(...),
    monthly_income: float = Form(...),
    age: int = Form(30),
    savings_rate: float = Form(0),
    debt_to_income: float = Form(0),
    emergency_months: float = Form(0),
    credit_score: int = Form(650),
    has_retirement_accounts: bool = Form(False),
    has_investments: bool = Form(False)
):
    """Calculate comprehensive wealth score."""
    profile = {
        "net_worth": net_worth,
        "monthly_income": monthly_income,
        "age": age,
        "savings_rate": savings_rate,
        "debt_to_income": debt_to_income,
        "emergency_months": emergency_months,
        "credit_score": credit_score,
        "has_retirement_accounts": has_retirement_accounts,
        "has_investments": has_investments
    }

    result = calculators.calculate_wealth_score(profile)

    return JSONResponse({
        "success": True,
        "result": result
    })


@app.post("/api/calculate-fire-timeline")
async def calculate_fire_timeline(
    current_savings: float = Form(...),
    monthly_savings: float = Form(...),
    monthly_expenses: float = Form(...),
    annual_return: float = Form(0.07)
):
    """Calculate financial independence timeline."""
    result = calculators.calculate_financial_freedom_timeline(
        current_savings=current_savings,
        monthly_savings=monthly_savings,
        monthly_expenses=monthly_expenses,
        annual_return=annual_return
    )

    return JSONResponse({
        "success": True,
        "result": result
    })


@app.post("/api/calculate-debt-payoff")
async def calculate_debt_payoff(
    debts: str = Form(...),  # JSON string of debts
    extra_payment: float = Form(0),
    method: str = Form("avalanche")
):
    """Calculate debt payoff timeline."""
    import json

    try:
        debts_list = json.loads(debts)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid debts format")

    result = calculators.calculate_debt_payoff(
        debts=debts_list,
        extra_payment=extra_payment,
        method=method
    )

    return JSONResponse({
        "success": True,
        "result": result
    })


@app.get("/api/credit-improvement-estimate")
async def estimate_credit_improvement(actions: str):
    """Estimate credit score improvement from actions."""
    action_list = actions.split(",")
    result = calculators.estimate_credit_score_improvement(action_list)

    return JSONResponse({
        "success": True,
        "result": result
    })


# ========== Health Check ==========

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
