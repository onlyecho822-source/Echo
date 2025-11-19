"""
Echo Life OS - Financial OS
============================
Automated financial intelligence and optimization system.

Integrates with Plaid for account aggregation, provides fraud detection,
subscription tracking, and financial optimization.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
from decimal import Decimal
import re


class TransactionCategory(Enum):
    """Transaction categories for analysis."""
    INCOME = "income"
    TRANSFER = "transfer"
    SUBSCRIPTION = "subscription"
    FOOD_DINING = "food_dining"
    SHOPPING = "shopping"
    TRANSPORTATION = "transportation"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    TRAVEL = "travel"
    FEES = "fees"
    OTHER = "other"


class AlertType(Enum):
    """Financial alert types."""
    FRAUD = "fraud"
    LARGE_TRANSACTION = "large_transaction"
    UNUSUAL_MERCHANT = "unusual_merchant"
    SUBSCRIPTION_CHANGE = "subscription_change"
    LOW_BALANCE = "low_balance"
    BILL_DUE = "bill_due"
    OPPORTUNITY = "opportunity"


@dataclass
class Account:
    """Financial account representation."""
    id: str
    institution_name: str
    account_name: str
    account_type: str  # checking, savings, credit, investment
    balance_current: Decimal
    balance_available: Optional[Decimal]
    currency: str
    last_updated: datetime
    mask: str  # Last 4 digits


@dataclass
class Transaction:
    """Financial transaction representation."""
    id: str
    account_id: str
    amount: Decimal
    date: datetime
    name: str
    merchant_name: Optional[str]
    category: TransactionCategory
    pending: bool
    location: Optional[Dict[str, str]]
    metadata: Optional[Dict[str, Any]]


@dataclass
class Subscription:
    """Recurring subscription or bill."""
    id: str
    name: str
    amount: Decimal
    frequency: str  # monthly, yearly, weekly
    next_charge: datetime
    merchant_name: str
    category: str
    is_active: bool
    account_id: str
    last_charged: datetime


@dataclass
class FinancialAlert:
    """Financial alert or notification."""
    id: str
    timestamp: datetime
    alert_type: AlertType
    title: str
    description: str
    amount: Optional[Decimal]
    action_required: bool
    metadata: Optional[Dict[str, Any]]


class PlaidClient:
    """
    Plaid API client for account aggregation.

    In production, this would use the actual Plaid SDK.
    This is a mock implementation for architecture demonstration.
    """

    def __init__(self, client_id: str, secret: str, environment: str = "sandbox"):
        self.client_id = client_id
        self.secret = secret
        self.environment = environment
        self.base_url = f"https://{environment}.plaid.com"

    async def get_accounts(self, access_token: str) -> List[Account]:
        """
        Get all accounts for a linked item.

        In production: plaid.Accounts.get(access_token)
        """
        # Mock implementation
        return []

    async def get_transactions(
        self,
        access_token: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Transaction]:
        """
        Get transactions for date range.

        In production: plaid.Transactions.get(access_token, start, end)
        """
        # Mock implementation
        return []

    async def create_link_token(self, user_id: str) -> str:
        """
        Create a link token for Plaid Link.

        This is used to initiate the account linking flow.
        """
        # Mock implementation
        return f"link-sandbox-{user_id}"


class FraudDetector:
    """
    ML-based fraud detection for transactions.

    Uses rule-based heuristics with ML model integration points.
    """

    def __init__(self):
        # Baseline spending patterns (loaded from user history)
        self.spending_baselines: Dict[str, float] = {}

        # Known fraud patterns
        self.fraud_patterns = [
            r'(?i)test\s*transaction',
            r'(?i)foreign\s*transaction\s*fee',
        ]

        # Suspicious merchant categories
        self.suspicious_categories = ['gambling', 'crypto', 'wire_transfer']

    def analyze_transaction(
        self,
        transaction: Transaction,
        account_history: List[Transaction]
    ) -> Tuple[float, List[str]]:
        """
        Analyze a transaction for fraud indicators.

        Returns:
            Tuple of (risk_score 0-100, list of risk factors)
        """
        risk_score = 0
        risk_factors = []

        # Check for unusual amount
        if account_history:
            amounts = [abs(float(t.amount)) for t in account_history]
            avg_amount = sum(amounts) / len(amounts)
            if abs(float(transaction.amount)) > avg_amount * 3:
                risk_score += 30
                risk_factors.append(f"Amount {transaction.amount} exceeds 3x average")

        # Check for duplicate transactions
        recent = [t for t in account_history
                  if abs((t.date - transaction.date).days) <= 1]
        duplicates = [t for t in recent
                     if t.amount == transaction.amount and t.name == transaction.name]
        if duplicates:
            risk_score += 20
            risk_factors.append("Possible duplicate transaction")

        # Check transaction name for fraud patterns
        for pattern in self.fraud_patterns:
            if re.search(pattern, transaction.name):
                risk_score += 25
                risk_factors.append(f"Suspicious pattern: {pattern}")

        # Check for round amounts (often fraudulent)
        amount_float = abs(float(transaction.amount))
        if amount_float >= 100 and amount_float % 100 == 0:
            risk_score += 10
            risk_factors.append("Suspiciously round amount")

        # Check time of transaction (late night = higher risk)
        hour = transaction.date.hour
        if 1 <= hour <= 5:
            risk_score += 15
            risk_factors.append("Late night transaction")

        return min(100, risk_score), risk_factors


class SubscriptionTracker:
    """
    Track and analyze recurring subscriptions.

    Identifies subscriptions from transaction patterns and
    provides recommendations for optimization.
    """

    def __init__(self):
        # Known subscription merchants
        self.subscription_merchants = {
            'netflix': {'name': 'Netflix', 'category': 'entertainment'},
            'spotify': {'name': 'Spotify', 'category': 'entertainment'},
            'amazon prime': {'name': 'Amazon Prime', 'category': 'shopping'},
            'hulu': {'name': 'Hulu', 'category': 'entertainment'},
            'disney+': {'name': 'Disney+', 'category': 'entertainment'},
            'apple': {'name': 'Apple Services', 'category': 'technology'},
            'google': {'name': 'Google Services', 'category': 'technology'},
            'dropbox': {'name': 'Dropbox', 'category': 'productivity'},
            'adobe': {'name': 'Adobe', 'category': 'productivity'},
            'microsoft': {'name': 'Microsoft 365', 'category': 'productivity'},
        }

    def detect_subscriptions(
        self,
        transactions: List[Transaction]
    ) -> List[Subscription]:
        """
        Detect recurring subscriptions from transaction history.

        Looks for:
        - Same merchant
        - Similar amounts
        - Regular intervals (weekly, monthly, yearly)
        """
        subscriptions = []

        # Group by merchant
        by_merchant: Dict[str, List[Transaction]] = {}
        for txn in transactions:
            key = (txn.merchant_name or txn.name).lower()
            if key not in by_merchant:
                by_merchant[key] = []
            by_merchant[key].append(txn)

        # Analyze each merchant for recurring patterns
        for merchant, txns in by_merchant.items():
            if len(txns) < 2:
                continue

            # Sort by date
            txns.sort(key=lambda t: t.date)

            # Check for monthly pattern
            intervals = []
            for i in range(1, len(txns)):
                days = (txns[i].date - txns[i-1].date).days
                intervals.append(days)

            if not intervals:
                continue

            avg_interval = sum(intervals) / len(intervals)

            # Determine frequency
            frequency = None
            if 6 <= avg_interval <= 8:
                frequency = "weekly"
            elif 28 <= avg_interval <= 32:
                frequency = "monthly"
            elif 360 <= avg_interval <= 370:
                frequency = "yearly"

            if frequency:
                # Found a subscription
                latest = txns[-1]
                subscription = Subscription(
                    id=f"sub_{merchant}_{latest.account_id}",
                    name=self._get_subscription_name(merchant),
                    amount=abs(latest.amount),
                    frequency=frequency,
                    next_charge=self._predict_next_charge(latest.date, frequency),
                    merchant_name=merchant,
                    category=self._get_category(merchant),
                    is_active=True,
                    account_id=latest.account_id,
                    last_charged=latest.date
                )
                subscriptions.append(subscription)

        return subscriptions

    def _get_subscription_name(self, merchant: str) -> str:
        """Get display name for subscription."""
        for key, info in self.subscription_merchants.items():
            if key in merchant.lower():
                return info['name']
        return merchant.title()

    def _get_category(self, merchant: str) -> str:
        """Get category for subscription."""
        for key, info in self.subscription_merchants.items():
            if key in merchant.lower():
                return info['category']
        return 'other'

    def _predict_next_charge(self, last_charge: datetime, frequency: str) -> datetime:
        """Predict next charge date."""
        if frequency == "weekly":
            return last_charge + timedelta(days=7)
        elif frequency == "monthly":
            return last_charge + timedelta(days=30)
        elif frequency == "yearly":
            return last_charge + timedelta(days=365)
        return last_charge + timedelta(days=30)

    def calculate_annual_cost(self, subscriptions: List[Subscription]) -> Decimal:
        """Calculate total annual subscription cost."""
        total = Decimal('0')
        for sub in subscriptions:
            if not sub.is_active:
                continue
            if sub.frequency == "weekly":
                total += sub.amount * 52
            elif sub.frequency == "monthly":
                total += sub.amount * 12
            elif sub.frequency == "yearly":
                total += sub.amount
        return total


class OptimizationEngine:
    """
    Financial optimization recommendations.

    Analyzes spending patterns and provides actionable suggestions.
    """

    def analyze_spending(
        self,
        transactions: List[Transaction],
        accounts: List[Account]
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns and generate insights.

        Returns:
            Dictionary with spending analysis and recommendations
        """
        # Category breakdown
        by_category: Dict[str, Decimal] = {}
        for txn in transactions:
            if txn.amount < 0:  # Spending (negative amounts)
                cat = txn.category.value
                if cat not in by_category:
                    by_category[cat] = Decimal('0')
                by_category[cat] += abs(txn.amount)

        # Calculate totals
        total_spending = sum(by_category.values())
        total_income = sum(
            txn.amount for txn in transactions
            if txn.category == TransactionCategory.INCOME
        )

        # Savings rate
        savings_rate = (
            (total_income - total_spending) / total_income * 100
            if total_income > 0 else 0
        )

        # Generate recommendations
        recommendations = []

        # Check savings rate
        if savings_rate < 20:
            recommendations.append({
                'type': 'savings',
                'priority': 'high',
                'title': 'Low Savings Rate',
                'description': f'Your savings rate is {savings_rate:.1f}%. Aim for at least 20%.',
                'potential_savings': float(total_income * Decimal('0.20') - (total_income - total_spending))
            })

        # Check dining spending
        if TransactionCategory.FOOD_DINING.value in by_category:
            dining = by_category[TransactionCategory.FOOD_DINING.value]
            dining_pct = dining / total_spending * 100 if total_spending else 0
            if dining_pct > 15:
                recommendations.append({
                    'type': 'spending',
                    'priority': 'medium',
                    'title': 'High Dining Expenses',
                    'description': f'Dining is {dining_pct:.1f}% of spending. Consider meal prep.',
                    'potential_savings': float(dining * Decimal('0.30'))
                })

        # Check for fee transactions
        if TransactionCategory.FEES.value in by_category:
            fees = by_category[TransactionCategory.FEES.value]
            if fees > 0:
                recommendations.append({
                    'type': 'fees',
                    'priority': 'high',
                    'title': 'Avoidable Fees Detected',
                    'description': f'You paid ${fees:.2f} in fees. Consider fee-free alternatives.',
                    'potential_savings': float(fees)
                })

        return {
            'spending_by_category': {k: float(v) for k, v in by_category.items()},
            'total_spending': float(total_spending),
            'total_income': float(total_income),
            'savings_rate': savings_rate,
            'recommendations': recommendations,
            'analysis_date': datetime.utcnow().isoformat()
        }


class FinancialOS:
    """
    Main Financial OS orchestrator.

    Coordinates all financial intelligence features:
    - Account aggregation via Plaid
    - Fraud detection
    - Subscription tracking
    - Spending optimization
    """

    def __init__(self, base_path: str = "~/.echo"):
        self.base_path = Path(base_path).expanduser()
        self._setup_directories()

        # Initialize database
        self.db_path = str(self.base_path / "financial" / "financial.db")
        self._init_database()

        # Initialize Plaid client
        self.plaid = PlaidClient(
            client_id=os.environ.get('PLAID_CLIENT_ID', ''),
            secret=os.environ.get('PLAID_SECRET', ''),
            environment=os.environ.get('PLAID_ENV', 'sandbox')
        )

        # Initialize components
        self.fraud_detector = FraudDetector()
        self.subscription_tracker = SubscriptionTracker()
        self.optimization_engine = OptimizationEngine()

        # Alerts
        self.alerts: List[FinancialAlert] = []

    def _setup_directories(self):
        """Create financial directories."""
        (self.base_path / "financial").mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize financial database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                institution_name TEXT,
                account_name TEXT,
                account_type TEXT,
                balance_current REAL,
                balance_available REAL,
                currency TEXT DEFAULT 'USD',
                last_updated TEXT,
                mask TEXT
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                merchant_name TEXT,
                category TEXT,
                pending INTEGER DEFAULT 0,
                location TEXT,
                metadata TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')

        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                frequency TEXT NOT NULL,
                next_charge TEXT,
                merchant_name TEXT,
                category TEXT,
                is_active INTEGER DEFAULT 1,
                account_id TEXT,
                last_charged TEXT
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_account ON transactions(account_id)')

        conn.commit()
        conn.close()

    async def link_account(self, user_id: str) -> str:
        """
        Initiate account linking via Plaid Link.

        Returns:
            Link token for Plaid Link initialization
        """
        return await self.plaid.create_link_token(user_id)

    async def sync_accounts(self, access_token: str):
        """
        Sync accounts and transactions from Plaid.

        Args:
            access_token: Plaid access token for the item
        """
        # Get accounts
        accounts = await self.plaid.get_accounts(access_token)

        # Get transactions (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        transactions = await self.plaid.get_transactions(
            access_token, start_date, end_date
        )

        # Store in database
        # (Implementation details omitted for brevity)

        # Analyze for fraud
        for txn in transactions:
            risk_score, factors = self.fraud_detector.analyze_transaction(
                txn, transactions
            )
            if risk_score > 50:
                self.alerts.append(FinancialAlert(
                    id=f"fraud_{txn.id}",
                    timestamp=datetime.utcnow(),
                    alert_type=AlertType.FRAUD,
                    title="Suspicious Transaction Detected",
                    description=f"Transaction '{txn.name}' has risk score {risk_score}. Factors: {', '.join(factors)}",
                    amount=txn.amount,
                    action_required=True,
                    metadata={'transaction_id': txn.id, 'risk_factors': factors}
                ))

    def get_subscriptions(self) -> List[Subscription]:
        """Get all detected subscriptions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM subscriptions WHERE is_active = 1')
        rows = cursor.fetchall()
        conn.close()

        # Convert to Subscription objects
        subscriptions = []
        for row in rows:
            subscriptions.append(Subscription(
                id=row[0],
                name=row[1],
                amount=Decimal(str(row[2])),
                frequency=row[3],
                next_charge=datetime.fromisoformat(row[4]) if row[4] else None,
                merchant_name=row[5],
                category=row[6],
                is_active=bool(row[7]),
                account_id=row[8],
                last_charged=datetime.fromisoformat(row[9]) if row[9] else None
            ))

        return subscriptions

    def get_spending_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Get spending analysis for the specified period.

        Args:
            days: Number of days to analyze

        Returns:
            Spending analysis with recommendations
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get transactions
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT * FROM transactions WHERE date >= ? ORDER BY date DESC
        ''', (start_date,))
        rows = cursor.fetchall()

        # Get accounts
        cursor.execute('SELECT * FROM accounts')
        account_rows = cursor.fetchall()
        conn.close()

        # Convert to objects (simplified)
        transactions = []
        for row in rows:
            transactions.append(Transaction(
                id=row[0],
                account_id=row[1],
                amount=Decimal(str(row[2])),
                date=datetime.fromisoformat(row[3]),
                name=row[4],
                merchant_name=row[5],
                category=TransactionCategory(row[6]) if row[6] else TransactionCategory.OTHER,
                pending=bool(row[7]),
                location=json.loads(row[8]) if row[8] else None,
                metadata=json.loads(row[9]) if row[9] else None
            ))

        accounts = []
        for row in account_rows:
            accounts.append(Account(
                id=row[0],
                institution_name=row[2],
                account_name=row[3],
                account_type=row[4],
                balance_current=Decimal(str(row[5])) if row[5] else Decimal('0'),
                balance_available=Decimal(str(row[6])) if row[6] else None,
                currency=row[7],
                last_updated=datetime.fromisoformat(row[8]) if row[8] else datetime.utcnow(),
                mask=row[9]
            ))

        return self.optimization_engine.analyze_spending(transactions, accounts)

    def get_financial_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive financial summary.

        Returns:
            Summary including balances, alerts, subscriptions, insights
        """
        subscriptions = self.get_subscriptions()
        annual_subscription_cost = self.subscription_tracker.calculate_annual_cost(subscriptions)

        return {
            'total_accounts': self._count_accounts(),
            'subscriptions': {
                'count': len(subscriptions),
                'annual_cost': float(annual_subscription_cost),
                'monthly_cost': float(annual_subscription_cost / 12)
            },
            'alerts': {
                'total': len(self.alerts),
                'action_required': len([a for a in self.alerts if a.action_required])
            },
            'last_sync': datetime.utcnow().isoformat()
        }

    def _count_accounts(self) -> int:
        """Count linked accounts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM accounts')
        count = cursor.fetchone()[0]
        conn.close()
        return count


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize Financial OS
        financial = FinancialOS()

        # Get financial summary
        summary = financial.get_financial_summary()
        print(f"Financial Summary: {json.dumps(summary, indent=2)}")

        # Get spending analysis
        analysis = financial.get_spending_analysis(days=30)
        print(f"\nSpending Analysis: {json.dumps(analysis, indent=2)}")

    asyncio.run(main())
