"""Database models for the wealth guide application."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User profile and financial data."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credit_reports = relationship("CreditReport", back_populates="user")
    financial_profiles = relationship("FinancialProfile", back_populates="user")
    dispute_letters = relationship("DisputeLetter", back_populates="user")
    trust_funds = relationship("TrustFund", back_populates="user")


class CreditReport(Base):
    """Uploaded credit report data."""

    __tablename__ = "credit_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    upload_date = Column(DateTime, default=datetime.utcnow)
    bureau = Column(String(50))  # Experian, Equifax, TransUnion

    # Parsed scores
    credit_score = Column(Integer, nullable=True)
    score_factors = Column(JSON, nullable=True)

    # Account summary
    total_accounts = Column(Integer, default=0)
    open_accounts = Column(Integer, default=0)
    closed_accounts = Column(Integer, default=0)
    delinquent_accounts = Column(Integer, default=0)
    derogatory_accounts = Column(Integer, default=0)

    # Balances
    total_balance = Column(Float, default=0.0)
    total_credit_limit = Column(Float, default=0.0)
    credit_utilization = Column(Float, default=0.0)

    # Payment history
    on_time_payments = Column(Integer, default=0)
    late_payments = Column(Integer, default=0)
    collections = Column(Integer, default=0)

    # Raw parsed data
    parsed_data = Column(JSON, nullable=True)
    negative_items = Column(JSON, nullable=True)
    improvement_opportunities = Column(JSON, nullable=True)

    user = relationship("User", back_populates="credit_reports")
    credit_items = relationship("CreditItem", back_populates="credit_report")


class CreditItem(Base):
    """Individual credit report line items."""

    __tablename__ = "credit_items"

    id = Column(Integer, primary_key=True, index=True)
    credit_report_id = Column(Integer, ForeignKey("credit_reports.id"))

    # Account info
    creditor_name = Column(String(255))
    account_number = Column(String(50))
    account_type = Column(String(50))  # Credit Card, Mortgage, Auto, etc.

    # Status
    status = Column(String(50))  # Open, Closed, Collection, etc.
    payment_status = Column(String(50))  # Current, Late, Charge-off, etc.

    # Financials
    balance = Column(Float, default=0.0)
    credit_limit = Column(Float, default=0.0)
    high_balance = Column(Float, default=0.0)
    monthly_payment = Column(Float, default=0.0)

    # Dates
    date_opened = Column(DateTime, nullable=True)
    date_reported = Column(DateTime, nullable=True)

    # Dispute info
    is_negative = Column(Boolean, default=False)
    is_disputable = Column(Boolean, default=False)
    dispute_reason = Column(Text, nullable=True)
    impact_score = Column(Integer, default=0)  # 1-10 impact on credit score

    credit_report = relationship("CreditReport", back_populates="credit_items")


class DisputeLetter(Base):
    """Generated dispute letters."""

    __tablename__ = "dispute_letters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    letter_type = Column(String(100))  # Validation, Dispute, Cease & Desist, etc.
    target_bureau = Column(String(50))  # Experian, Equifax, TransUnion
    target_creditor = Column(String(255), nullable=True)

    subject = Column(String(255))
    content = Column(Text)

    # Legal basis
    legal_citations = Column(JSON)  # FCRA, FDCPA sections

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    response_received = Column(Boolean, default=False)

    user = relationship("User", back_populates="dispute_letters")


class FinancialProfile(Base):
    """User's financial position snapshot."""

    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Income
    monthly_income = Column(Float, default=0.0)
    additional_income = Column(Float, default=0.0)

    # Assets
    cash_savings = Column(Float, default=0.0)
    investments = Column(Float, default=0.0)
    retirement_accounts = Column(Float, default=0.0)
    real_estate_equity = Column(Float, default=0.0)
    other_assets = Column(Float, default=0.0)

    # Liabilities
    mortgage_balance = Column(Float, default=0.0)
    auto_loans = Column(Float, default=0.0)
    student_loans = Column(Float, default=0.0)
    credit_card_debt = Column(Float, default=0.0)
    other_debt = Column(Float, default=0.0)

    # Monthly expenses
    housing_expense = Column(Float, default=0.0)
    utilities = Column(Float, default=0.0)
    food = Column(Float, default=0.0)
    transportation = Column(Float, default=0.0)
    insurance = Column(Float, default=0.0)
    other_expenses = Column(Float, default=0.0)

    # Calculated fields
    net_worth = Column(Float, default=0.0)
    monthly_cash_flow = Column(Float, default=0.0)
    debt_to_income = Column(Float, default=0.0)
    savings_rate = Column(Float, default=0.0)

    # Wealth score (custom metric)
    wealth_score = Column(Integer, default=0)  # 0-100
    wealth_trajectory = Column(String(50))  # Declining, Stable, Growing, Accelerating

    user = relationship("User", back_populates="financial_profiles")


class TrustFund(Base):
    """Trust fund planning records."""

    __tablename__ = "trust_funds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    trust_type = Column(String(100))  # Revocable, Irrevocable, Living, etc.
    trust_name = Column(String(255))
    purpose = Column(Text)

    # Parties
    grantor_info = Column(JSON)
    trustee_info = Column(JSON)
    beneficiaries = Column(JSON)

    # Assets
    initial_funding = Column(Float, default=0.0)
    asset_types = Column(JSON)  # Cash, Securities, Real Estate, etc.

    # Terms
    distribution_rules = Column(Text)
    special_provisions = Column(Text)

    # Status
    status = Column(String(50))  # Planning, Draft, Established
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trust_funds")


class WealthGoal(Base):
    """Wealth building goals and tracking."""

    __tablename__ = "wealth_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    goal_name = Column(String(255))
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)

    # Investment plan
    daily_contribution = Column(Float, default=1.0)
    expected_return = Column(Float, default=0.07)  # 7% annual

    # Timeline
    start_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime)

    # Progress
    progress_percentage = Column(Float, default=0.0)
    on_track = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
