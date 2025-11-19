"""
Savings Optimizer - Financial optimization suggestions

Analyzes spending patterns and provides optimization recommendations.
"""

from typing import Any, Dict, List


class SavingsOptimizer:
    """
    Analyzes financial data and provides optimization suggestions.
    """

    def __init__(self):
        # Budget guidelines (percentage of income)
        self._guidelines = {
            'housing': {'max': 30, 'target': 25},
            'transportation': {'max': 15, 'target': 10},
            'food': {'max': 15, 'target': 12},
            'utilities': {'max': 10, 'target': 7},
            'insurance': {'max': 15, 'target': 10},
            'healthcare': {'max': 10, 'target': 5},
            'savings': {'min': 20, 'target': 25},
            'entertainment': {'max': 10, 'target': 5},
            'shopping': {'max': 5, 'target': 3}
        }

        # Common optimization strategies
        self._strategies = [
            {
                'category': 'subscriptions',
                'name': 'Subscription Audit',
                'description': 'Review and cancel unused subscriptions',
                'typical_savings': 50,  # per month
                'effort': 'low'
            },
            {
                'category': 'food',
                'name': 'Meal Planning',
                'description': 'Plan meals weekly to reduce food waste and impulse purchases',
                'typical_savings': 150,
                'effort': 'medium'
            },
            {
                'category': 'utilities',
                'name': 'Energy Efficiency',
                'description': 'Optimize heating/cooling, switch to LED, unplug devices',
                'typical_savings': 30,
                'effort': 'low'
            },
            {
                'category': 'transportation',
                'name': 'Commute Optimization',
                'description': 'Carpool, use public transit, or combine trips',
                'typical_savings': 100,
                'effort': 'medium'
            },
            {
                'category': 'shopping',
                'name': 'Waiting Period',
                'description': 'Wait 48 hours before non-essential purchases over $50',
                'typical_savings': 75,
                'effort': 'low'
            },
            {
                'category': 'insurance',
                'name': 'Insurance Review',
                'description': 'Shop around for better rates annually',
                'typical_savings': 50,
                'effort': 'medium'
            }
        ]

    def analyze(self, monthly_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze monthly financial data and provide suggestions.

        Args:
            monthly_summary: Monthly financial summary

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        total_income = monthly_summary.get('total_income', 0)

        if total_income == 0:
            return suggestions

        by_category = monthly_summary.get('by_category', {})

        # Check each category against guidelines
        for category, amounts in by_category.items():
            if category not in self._guidelines:
                continue

            guideline = self._guidelines[category]
            percent = (amounts / total_income) * 100

            if 'max' in guideline and percent > guideline['max']:
                over_amount = amounts - (total_income * guideline['target'] / 100)
                suggestions.append({
                    'type': 'overspend',
                    'priority': 'high',
                    'category': category,
                    'description': f'{category.title()} at {percent:.1f}% exceeds {guideline["max"]}% guideline',
                    'target_percent': guideline['target'],
                    'potential_savings': over_amount,
                    'action': f'Reduce {category} by ${over_amount:.2f}/month to reach target'
                })

        # Suggest relevant strategies
        for strategy in self._strategies:
            cat = strategy['category']
            if cat in by_category or cat == 'subscriptions':
                # Check if category is overspent or could use optimization
                spent = by_category.get(cat, 0)
                if spent > 0 or cat == 'subscriptions':
                    suggestions.append({
                        'type': 'strategy',
                        'priority': 'medium',
                        'name': strategy['name'],
                        'description': strategy['description'],
                        'potential_savings': strategy['typical_savings'],
                        'effort': strategy['effort'],
                        'category': cat
                    })

        # Sort by potential savings
        suggestions.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)

        return suggestions

    def calculate_potential_savings(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate total potential savings from suggestions.

        Args:
            suggestions: List of optimization suggestions

        Returns:
            Savings summary
        """
        total_monthly = sum(s.get('potential_savings', 0) for s in suggestions)

        return {
            'monthly': total_monthly,
            'quarterly': total_monthly * 3,
            'annual': total_monthly * 12,
            'suggestion_count': len(suggestions)
        }

    def get_quick_wins(self, monthly_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get low-effort optimization suggestions.

        Args:
            monthly_summary: Monthly financial summary

        Returns:
            List of quick win suggestions
        """
        all_suggestions = self.analyze(monthly_summary)

        return [
            s for s in all_suggestions
            if s.get('effort') == 'low' or s.get('priority') == 'high'
        ][:5]  # Top 5 quick wins

    def project_savings(self, current_savings_rate: float, target_rate: float,
                        monthly_income: float, months: int = 12) -> Dict[str, Any]:
        """
        Project savings with different scenarios.

        Args:
            current_savings_rate: Current savings rate (0-100)
            target_rate: Target savings rate (0-100)
            monthly_income: Monthly income
            months: Projection period

        Returns:
            Savings projections
        """
        current_monthly = monthly_income * (current_savings_rate / 100)
        target_monthly = monthly_income * (target_rate / 100)

        return {
            'current_scenario': {
                'monthly_savings': current_monthly,
                'total_savings': current_monthly * months
            },
            'target_scenario': {
                'monthly_savings': target_monthly,
                'total_savings': target_monthly * months
            },
            'improvement': {
                'additional_monthly': target_monthly - current_monthly,
                'additional_total': (target_monthly - current_monthly) * months,
                'percent_increase': ((target_rate - current_savings_rate) / current_savings_rate * 100)
                                   if current_savings_rate > 0 else 0
            }
        }
