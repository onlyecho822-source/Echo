"""
Financial OS - Personal Finance Automation

The Financial OS provides:
- Income tracking
- Expense categorization
- Savings optimization
- Fraud detection
- Financial modeling
- Opportunity identification
"""

from .engine import FinancialEngine
from .tracker import TransactionTracker
from .optimizer import SavingsOptimizer

__all__ = ['FinancialEngine', 'TransactionTracker', 'SavingsOptimizer']
