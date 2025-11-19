"""
Financial Engine - Core financial management system

Coordinates all financial tracking, analysis, and optimization.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from decimal import Decimal

from .tracker import TransactionTracker
from .optimizer import SavingsOptimizer


class FinancialEngine:
    """
    Core financial management engine for Echo Life OS.

    Coordinates:
    - Transaction tracking
    - Budget management
    - Savings optimization
    - Financial health monitoring
    - Opportunity detection
    """

    def __init__(self, memory_kernel=None):
        """
        Initialize Financial Engine.

        Args:
            memory_kernel: Optional MemoryKernel for persistent storage
        """
        self.memory_kernel = memory_kernel
        self.tracker = TransactionTracker()
        self.optimizer = SavingsOptimizer()

        # Financial configuration
        self._config = {
            'currency': 'USD',
            'savings_goal_percent': 20,
            'emergency_fund_months': 6,
            'categories': [
                'income', 'housing', 'utilities', 'food', 'transportation',
                'healthcare', 'insurance', 'savings', 'entertainment',
                'shopping', 'education', 'other'
            ]
        }

        # Financial goals
        self._goals: List[Dict[str, Any]] = []

        # Load from memory if available
        if memory_kernel:
            self._load_state()

    def _load_state(self):
        """Load financial state from memory kernel."""
        if not self.memory_kernel:
            return

        goals = self.memory_kernel.retrieve('financial_goals')
        if goals:
            self._goals = goals

        config = self.memory_kernel.retrieve('financial_config')
        if config:
            self._config.update(config)

    def _save_state(self):
        """Save financial state to memory kernel."""
        if not self.memory_kernel:
            return

        self.memory_kernel.store('financial_goals', self._goals, 'financial')
        self.memory_kernel.store('financial_config', self._config, 'financial')

    def add_transaction(self, amount: float, category: str,
                        description: str, transaction_type: str = 'expense',
                        date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a financial transaction.

        Args:
            amount: Transaction amount
            category: Category (from config categories)
            description: Transaction description
            transaction_type: 'income' or 'expense'
            date: Optional date string (ISO format)

        Returns:
            Transaction record with analysis
        """
        transaction = self.tracker.add_transaction(
            amount=amount,
            category=category,
            description=description,
            transaction_type=transaction_type,
            date=date
        )

        # Analyze transaction
        analysis = self._analyze_transaction(transaction)
        transaction['analysis'] = analysis

        # Log to memory kernel
        if self.memory_kernel:
            self.memory_kernel.log_event(
                'financial_transaction',
                transaction,
                agent='financial_engine'
            )

        return transaction

    def _analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a transaction for patterns and concerns."""
        analysis = {
            'flags': [],
            'suggestions': [],
            'category_percent': 0
        }

        amount = transaction['amount']
        category = transaction['category']

        # Get monthly totals for context
        monthly = self.get_monthly_summary()

        # Check if expense is unusually large for category
        if transaction['type'] == 'expense':
            category_avg = monthly.get('category_averages', {}).get(category, 0)
            if category_avg > 0 and amount > category_avg * 2:
                analysis['flags'].append(f'Transaction 2x above category average')

            # Calculate category percentage of total expenses
            total_expenses = monthly.get('total_expenses', 1)
            analysis['category_percent'] = (amount / total_expenses * 100) if total_expenses else 0

        # Check impact on savings rate
        if transaction['type'] == 'expense':
            projected_savings = self._calculate_projected_savings(amount)
            if projected_savings < self._config['savings_goal_percent']:
                analysis['suggestions'].append(
                    f'This expense reduces savings rate below {self._config["savings_goal_percent"]}% goal'
                )

        return analysis

    def _calculate_projected_savings(self, additional_expense: float) -> float:
        """Calculate projected savings rate with additional expense."""
        monthly = self.get_monthly_summary()
        income = monthly.get('total_income', 0)
        expenses = monthly.get('total_expenses', 0) + additional_expense

        if income == 0:
            return 0

        return ((income - expenses) / income) * 100

    def get_monthly_summary(self, month: Optional[str] = None) -> Dict[str, Any]:
        """
        Get financial summary for a month.

        Args:
            month: Month in YYYY-MM format (default: current month)

        Returns:
            Dictionary with financial summary
        """
        if month is None:
            month = datetime.utcnow().strftime('%Y-%m')

        transactions = self.tracker.get_transactions(month=month)

        summary = {
            'month': month,
            'total_income': 0,
            'total_expenses': 0,
            'net': 0,
            'savings_rate': 0,
            'by_category': {},
            'category_averages': {},
            'transaction_count': len(transactions)
        }

        for t in transactions:
            amount = t['amount']
            category = t['category']

            if t['type'] == 'income':
                summary['total_income'] += amount
            else:
                summary['total_expenses'] += amount
                summary['by_category'][category] = \
                    summary['by_category'].get(category, 0) + amount

        summary['net'] = summary['total_income'] - summary['total_expenses']

        if summary['total_income'] > 0:
            summary['savings_rate'] = (summary['net'] / summary['total_income']) * 100

        # Calculate category averages
        if transactions:
            for cat, total in summary['by_category'].items():
                count = sum(1 for t in transactions if t['category'] == cat)
                summary['category_averages'][cat] = total / count if count else 0

        return summary

    def set_goal(self, name: str, target_amount: float, deadline: str,
                 category: str = 'savings') -> Dict[str, Any]:
        """
        Set a financial goal.

        Args:
            name: Goal name
            target_amount: Target amount
            deadline: Deadline (ISO date)
            category: Goal category

        Returns:
            Goal record
        """
        goal = {
            'id': len(self._goals) + 1,
            'name': name,
            'target_amount': target_amount,
            'current_amount': 0,
            'deadline': deadline,
            'category': category,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }

        self._goals.append(goal)
        self._save_state()

        return goal

    def update_goal_progress(self, goal_id: int, amount: float) -> Optional[Dict[str, Any]]:
        """
        Update progress toward a goal.

        Args:
            goal_id: Goal ID
            amount: Amount to add to current progress

        Returns:
            Updated goal or None if not found
        """
        for goal in self._goals:
            if goal['id'] == goal_id:
                goal['current_amount'] += amount

                # Check if goal reached
                if goal['current_amount'] >= goal['target_amount']:
                    goal['status'] = 'completed'
                    goal['completed_at'] = datetime.utcnow().isoformat()

                self._save_state()
                return goal

        return None

    def get_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get financial goals.

        Args:
            status: Optional status filter ('active', 'completed')

        Returns:
            List of goals
        """
        if status:
            return [g for g in self._goals if g['status'] == status]
        return self._goals.copy()

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get suggestions for financial optimization.

        Returns:
            List of suggestions with potential savings
        """
        suggestions = []

        # Get recent data
        monthly = self.get_monthly_summary()
        optimizer_suggestions = self.optimizer.analyze(monthly)

        suggestions.extend(optimizer_suggestions)

        # Check savings rate
        if monthly['savings_rate'] < self._config['savings_goal_percent']:
            gap = self._config['savings_goal_percent'] - monthly['savings_rate']
            suggestions.append({
                'type': 'savings_rate',
                'priority': 'high',
                'description': f"Savings rate {monthly['savings_rate']:.1f}% below {self._config['savings_goal_percent']}% goal",
                'action': f'Reduce expenses by ${monthly["total_income"] * gap / 100:.2f}/month'
            })

        # Check category spending
        budget_guidelines = {
            'housing': 30,
            'food': 15,
            'transportation': 10,
            'entertainment': 5
        }

        for category, guideline in budget_guidelines.items():
            spent = monthly['by_category'].get(category, 0)
            percent = (spent / monthly['total_income'] * 100) if monthly['total_income'] else 0

            if percent > guideline * 1.2:  # 20% over guideline
                suggestions.append({
                    'type': 'category_overspend',
                    'priority': 'medium',
                    'category': category,
                    'description': f'{category.title()} spending at {percent:.1f}% (guideline: {guideline}%)',
                    'action': f'Consider reducing {category} expenses'
                })

        return suggestions

    def get_financial_health(self) -> Dict[str, Any]:
        """
        Get overall financial health assessment.

        Returns:
            Health assessment with scores and recommendations
        """
        monthly = self.get_monthly_summary()

        health = {
            'overall_score': 0,
            'components': {
                'savings_rate': {'score': 0, 'status': 'unknown'},
                'emergency_fund': {'score': 0, 'status': 'unknown'},
                'debt_ratio': {'score': 0, 'status': 'unknown'},
                'budget_adherence': {'score': 0, 'status': 'unknown'}
            },
            'recommendations': []
        }

        # Savings rate score (0-100)
        savings_score = min(monthly['savings_rate'] / self._config['savings_goal_percent'] * 100, 100)
        health['components']['savings_rate'] = {
            'score': savings_score,
            'status': 'good' if savings_score >= 80 else 'fair' if savings_score >= 50 else 'poor',
            'value': f"{monthly['savings_rate']:.1f}%"
        }

        # Budget adherence score
        over_budget_categories = sum(
            1 for cat, amount in monthly['by_category'].items()
            if amount > monthly['total_income'] * 0.3  # Simplified check
        )
        budget_score = max(0, 100 - over_budget_categories * 20)
        health['components']['budget_adherence'] = {
            'score': budget_score,
            'status': 'good' if budget_score >= 80 else 'fair' if budget_score >= 50 else 'poor'
        }

        # Calculate overall score
        scores = [c['score'] for c in health['components'].values()]
        health['overall_score'] = sum(scores) / len(scores)

        # Generate recommendations
        if health['overall_score'] < 50:
            health['recommendations'].append('Consider consulting a financial advisor')
        elif health['overall_score'] < 80:
            health['recommendations'].append('Focus on improving savings rate')

        return health

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalies in financial activity.

        Returns:
            List of detected anomalies
        """
        return self.tracker.detect_anomalies()

    def close(self):
        """Save state and clean up."""
        self._save_state()
