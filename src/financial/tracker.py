"""
Transaction Tracker - Financial transaction management

Tracks income and expenses with categorization and analysis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import statistics


class TransactionTracker:
    """
    Tracks financial transactions with categorization and pattern detection.
    """

    def __init__(self):
        self._transactions: List[Dict[str, Any]] = []
        self._next_id = 1

    def add_transaction(self, amount: float, category: str,
                        description: str, transaction_type: str = 'expense',
                        date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a transaction.

        Args:
            amount: Transaction amount (positive)
            category: Category name
            description: Transaction description
            transaction_type: 'income' or 'expense'
            date: Optional ISO date string

        Returns:
            Transaction record
        """
        if date is None:
            date = datetime.utcnow().isoformat()

        transaction = {
            'id': self._next_id,
            'amount': abs(amount),
            'category': category.lower(),
            'description': description,
            'type': transaction_type,
            'date': date,
            'created_at': datetime.utcnow().isoformat()
        }

        self._transactions.append(transaction)
        self._next_id += 1

        return transaction

    def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a transaction by ID."""
        for t in self._transactions:
            if t['id'] == transaction_id:
                return t.copy()
        return None

    def get_transactions(self, month: Optional[str] = None,
                         category: Optional[str] = None,
                         transaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get transactions with optional filters.

        Args:
            month: Filter by month (YYYY-MM format)
            category: Filter by category
            transaction_type: Filter by type ('income' or 'expense')

        Returns:
            List of matching transactions
        """
        result = self._transactions.copy()

        if month:
            result = [t for t in result if t['date'].startswith(month)]

        if category:
            result = [t for t in result if t['category'] == category.lower()]

        if transaction_type:
            result = [t for t in result if t['type'] == transaction_type]

        return result

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction."""
        for i, t in enumerate(self._transactions):
            if t['id'] == transaction_id:
                del self._transactions[i]
                return True
        return False

    def get_category_totals(self, month: Optional[str] = None) -> Dict[str, float]:
        """Get totals by category for a period."""
        transactions = self.get_transactions(month=month, transaction_type='expense')

        totals = {}
        for t in transactions:
            category = t['category']
            totals[category] = totals.get(category, 0) + t['amount']

        return totals

    def get_trend(self, category: str, months: int = 6) -> List[Dict[str, Any]]:
        """
        Get spending trend for a category.

        Args:
            category: Category to analyze
            months: Number of months to include

        Returns:
            List of monthly totals
        """
        now = datetime.utcnow()
        trend = []

        for i in range(months):
            # Calculate month
            month_date = now.replace(day=1)
            for _ in range(i):
                month_date = (month_date - timedelta(days=1)).replace(day=1)

            month_str = month_date.strftime('%Y-%m')
            transactions = self.get_transactions(
                month=month_str,
                category=category,
                transaction_type='expense'
            )

            total = sum(t['amount'] for t in transactions)
            trend.append({
                'month': month_str,
                'total': total,
                'count': len(transactions)
            })

        return list(reversed(trend))

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalous transactions.

        Returns:
            List of anomalous transactions with explanations
        """
        anomalies = []

        # Group by category
        categories = {}
        for t in self._transactions:
            if t['type'] == 'expense':
                cat = t['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(t)

        # Find anomalies per category
        for category, transactions in categories.items():
            if len(transactions) < 3:
                continue

            amounts = [t['amount'] for t in transactions]
            mean = statistics.mean(amounts)
            std = statistics.stdev(amounts) if len(amounts) > 1 else 0

            if std == 0:
                continue

            for t in transactions:
                z_score = abs(t['amount'] - mean) / std
                if z_score > 2.5:  # 2.5 standard deviations
                    anomalies.append({
                        'transaction': t,
                        'reason': f'Amount ${t["amount"]:.2f} is {z_score:.1f}σ from category mean ${mean:.2f}',
                        'severity': 'high' if z_score > 3.5 else 'medium'
                    })

        # Check for duplicate transactions
        seen = {}
        for t in self._transactions:
            key = (t['amount'], t['category'], t['date'][:10])
            if key in seen:
                anomalies.append({
                    'transaction': t,
                    'reason': 'Possible duplicate transaction',
                    'severity': 'medium',
                    'duplicate_of': seen[key]['id']
                })
            else:
                seen[key] = t

        return anomalies

    def get_recurring_patterns(self) -> List[Dict[str, Any]]:
        """
        Identify recurring transaction patterns.

        Returns:
            List of detected recurring patterns
        """
        patterns = []

        # Group by description similarity and amount
        groups = {}
        for t in self._transactions:
            # Create simple key (could use fuzzy matching)
            key = (t['description'].lower()[:20], round(t['amount'], 0))
            if key not in groups:
                groups[key] = []
            groups[key].append(t)

        # Find patterns with multiple occurrences
        for key, transactions in groups.items():
            if len(transactions) >= 2:
                patterns.append({
                    'description': transactions[0]['description'],
                    'amount': transactions[0]['amount'],
                    'category': transactions[0]['category'],
                    'occurrences': len(transactions),
                    'frequency': 'monthly' if len(transactions) >= 3 else 'recurring'
                })

        return patterns


# Import timedelta for get_trend
from datetime import timedelta
