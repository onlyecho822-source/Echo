"""Financial calculators for wealth building and position analysis."""

from datetime import datetime, timedelta
from typing import Optional
import math


class FinancialCalculators:
    """Comprehensive financial calculators for wealth building."""

    def __init__(self):
        pass

    # ========== Financial Position Calculator ==========

    def calculate_net_worth(self, assets: dict, liabilities: dict) -> dict:
        """Calculate net worth and financial health metrics."""

        # Sum assets
        total_assets = sum([
            assets.get("cash_savings", 0),
            assets.get("checking_accounts", 0),
            assets.get("investments", 0),
            assets.get("retirement_accounts", 0),
            assets.get("real_estate_equity", 0),
            assets.get("vehicle_value", 0),
            assets.get("business_value", 0),
            assets.get("other_assets", 0)
        ])

        # Sum liabilities
        total_liabilities = sum([
            liabilities.get("mortgage", 0),
            liabilities.get("auto_loans", 0),
            liabilities.get("student_loans", 0),
            liabilities.get("credit_card_debt", 0),
            liabilities.get("personal_loans", 0),
            liabilities.get("medical_debt", 0),
            liabilities.get("other_debt", 0)
        ])

        net_worth = total_assets - total_liabilities

        # Calculate liquid net worth (exclude real estate and retirement)
        liquid_assets = sum([
            assets.get("cash_savings", 0),
            assets.get("checking_accounts", 0),
            assets.get("investments", 0)
        ])

        liquid_net_worth = liquid_assets - total_liabilities

        return {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth,
            "liquid_net_worth": liquid_net_worth,
            "asset_breakdown": assets,
            "liability_breakdown": liabilities
        }

    def calculate_financial_ratios(
        self,
        monthly_income: float,
        monthly_expenses: float,
        total_debt: float,
        liquid_assets: float,
        monthly_debt_payments: float
    ) -> dict:
        """Calculate key financial health ratios."""

        # Debt-to-Income Ratio
        annual_income = monthly_income * 12
        dti = (monthly_debt_payments / monthly_income * 100) if monthly_income > 0 else 0

        # Savings Rate
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0

        # Emergency Fund Ratio (months of expenses covered)
        emergency_ratio = (liquid_assets / monthly_expenses) if monthly_expenses > 0 else 0

        # Debt-to-Asset Ratio
        debt_to_asset = (total_debt / liquid_assets * 100) if liquid_assets > 0 else float('inf')

        # Financial Freedom Number (25x annual expenses for 4% rule)
        annual_expenses = monthly_expenses * 12
        fire_number = annual_expenses * 25

        return {
            "debt_to_income": {
                "value": round(dti, 1),
                "rating": self._rate_dti(dti),
                "description": f"{dti:.1f}% of income goes to debt payments"
            },
            "savings_rate": {
                "value": round(savings_rate, 1),
                "rating": self._rate_savings(savings_rate),
                "description": f"Saving {savings_rate:.1f}% of income"
            },
            "emergency_fund": {
                "months": round(emergency_ratio, 1),
                "rating": self._rate_emergency(emergency_ratio),
                "description": f"{emergency_ratio:.1f} months of expenses covered"
            },
            "fire_number": {
                "target": fire_number,
                "description": f"Need ${fire_number:,.0f} to retire (4% rule)"
            },
            "monthly_cash_flow": monthly_savings
        }

    def calculate_wealth_score(self, profile: dict) -> dict:
        """Calculate a comprehensive wealth score (0-100)."""

        score = 0
        breakdown = {}

        # Net worth score (0-25 points)
        net_worth = profile.get("net_worth", 0)
        age = profile.get("age", 30)
        expected_net_worth = profile.get("monthly_income", 5000) * 12 * (age / 10)

        if expected_net_worth > 0:
            nw_ratio = net_worth / expected_net_worth
            nw_score = min(25, nw_ratio * 25)
        else:
            nw_score = 0
        breakdown["net_worth_score"] = round(nw_score, 1)
        score += nw_score

        # Savings rate score (0-20 points)
        savings_rate = profile.get("savings_rate", 0)
        sr_score = min(20, savings_rate)
        breakdown["savings_score"] = round(sr_score, 1)
        score += sr_score

        # Debt score (0-20 points) - lower is better
        dti = profile.get("debt_to_income", 50)
        debt_score = max(0, 20 - (dti / 2))
        breakdown["debt_score"] = round(debt_score, 1)
        score += debt_score

        # Emergency fund score (0-15 points)
        emergency_months = profile.get("emergency_months", 0)
        ef_score = min(15, emergency_months * 2.5)
        breakdown["emergency_score"] = round(ef_score, 1)
        score += ef_score

        # Credit score component (0-10 points)
        credit_score = profile.get("credit_score", 650)
        cs_score = max(0, (credit_score - 500) / 35)
        breakdown["credit_component"] = round(cs_score, 1)
        score += cs_score

        # Investment score (0-10 points)
        has_retirement = profile.get("has_retirement_accounts", False)
        has_investments = profile.get("has_investments", False)
        inv_score = (5 if has_retirement else 0) + (5 if has_investments else 0)
        breakdown["investment_score"] = inv_score
        score += inv_score

        total_score = min(100, score)

        return {
            "wealth_score": round(total_score),
            "breakdown": breakdown,
            "rating": self._get_wealth_rating(total_score),
            "trajectory": self._get_trajectory(profile),
            "percentile": self._estimate_percentile(net_worth, age)
        }

    def _rate_dti(self, dti: float) -> str:
        if dti <= 20:
            return "Excellent"
        elif dti <= 35:
            return "Good"
        elif dti <= 43:
            return "Acceptable"
        elif dti <= 50:
            return "High"
        else:
            return "Critical"

    def _rate_savings(self, rate: float) -> str:
        if rate >= 20:
            return "Excellent"
        elif rate >= 15:
            return "Good"
        elif rate >= 10:
            return "Fair"
        elif rate >= 5:
            return "Low"
        else:
            return "Critical"

    def _rate_emergency(self, months: float) -> str:
        if months >= 6:
            return "Excellent"
        elif months >= 3:
            return "Good"
        elif months >= 1:
            return "Building"
        else:
            return "Critical"

    def _get_wealth_rating(self, score: float) -> str:
        if score >= 80:
            return "Elite"
        elif score >= 65:
            return "Strong"
        elif score >= 50:
            return "Building"
        elif score >= 35:
            return "Developing"
        else:
            return "Foundation"

    def _get_trajectory(self, profile: dict) -> str:
        savings_rate = profile.get("savings_rate", 0)
        dti_trend = profile.get("dti_trend", "stable")  # increasing, decreasing, stable

        if savings_rate >= 20 and dti_trend == "decreasing":
            return "Accelerating"
        elif savings_rate >= 10:
            return "Growing"
        elif savings_rate >= 0:
            return "Stable"
        else:
            return "Declining"

    def _estimate_percentile(self, net_worth: float, age: int) -> int:
        """Estimate net worth percentile for age group (US data approximation)."""
        # Rough approximations based on Federal Reserve data
        percentiles = {
            25: {50: 10000, 75: 50000, 90: 150000, 95: 300000},
            35: {50: 35000, 75: 150000, 90: 400000, 95: 750000},
            45: {50: 100000, 75: 350000, 90: 850000, 95: 1500000},
            55: {50: 180000, 75: 550000, 90: 1300000, 95: 2500000},
            65: {50: 225000, 75: 700000, 90: 1700000, 95: 3000000}
        }

        # Find closest age bracket
        age_bracket = min(percentiles.keys(), key=lambda x: abs(x - age))
        brackets = percentiles[age_bracket]

        if net_worth >= brackets[95]:
            return 95
        elif net_worth >= brackets[90]:
            return 90
        elif net_worth >= brackets[75]:
            return 75
        elif net_worth >= brackets[50]:
            return 50
        else:
            return 25

    # ========== Wealth Building Calculator ==========

    def calculate_compound_growth(
        self,
        initial_amount: float,
        daily_contribution: float,
        annual_return: float,
        years: int
    ) -> dict:
        """Calculate compound growth with daily contributions."""

        # Convert annual return to daily
        daily_return = (1 + annual_return) ** (1/365) - 1

        # Calculate future value with compound interest
        total_days = years * 365
        future_value = initial_amount
        total_contributions = initial_amount

        # Track yearly milestones
        yearly_values = []

        for day in range(total_days):
            future_value = future_value * (1 + daily_return) + daily_contribution
            total_contributions += daily_contribution

            # Record yearly milestone
            if (day + 1) % 365 == 0:
                year = (day + 1) // 365
                yearly_values.append({
                    "year": year,
                    "value": round(future_value, 2),
                    "contributions": round(total_contributions, 2),
                    "earnings": round(future_value - total_contributions, 2)
                })

        total_contributions = initial_amount + (daily_contribution * total_days)
        total_earnings = future_value - total_contributions

        return {
            "initial_amount": initial_amount,
            "daily_contribution": daily_contribution,
            "monthly_contribution": daily_contribution * 30,
            "annual_return": annual_return * 100,
            "years": years,
            "future_value": round(future_value, 2),
            "total_contributions": round(total_contributions, 2),
            "total_earnings": round(total_earnings, 2),
            "earnings_percentage": round((total_earnings / total_contributions) * 100, 1),
            "yearly_breakdown": yearly_values
        }

    def dollar_a_day_projection(self, years: int = 40) -> dict:
        """Show the power of $1/day investing over time."""

        scenarios = {
            "conservative": {
                "return": 0.05,
                "description": "Conservative (5% - Bonds/CDs)"
            },
            "moderate": {
                "return": 0.07,
                "description": "Moderate (7% - Balanced Portfolio)"
            },
            "aggressive": {
                "return": 0.10,
                "description": "Aggressive (10% - Stock Market Historical)"
            }
        }

        results = {}
        for name, scenario in scenarios.items():
            projection = self.calculate_compound_growth(
                initial_amount=0,
                daily_contribution=1.0,
                annual_return=scenario["return"],
                years=years
            )
            results[name] = {
                "description": scenario["description"],
                "future_value": projection["future_value"],
                "total_invested": projection["total_contributions"],
                "earnings": projection["total_earnings"]
            }

        # Key milestones at $1/day, 7% return
        milestones = []
        for milestone_years in [5, 10, 20, 30, 40]:
            if milestone_years <= years:
                proj = self.calculate_compound_growth(0, 1.0, 0.07, milestone_years)
                milestones.append({
                    "years": milestone_years,
                    "invested": proj["total_contributions"],
                    "value": proj["future_value"]
                })

        return {
            "daily_amount": 1.0,
            "years": years,
            "scenarios": results,
            "milestones": milestones,
            "message": self._get_motivation_message(results["moderate"]["future_value"])
        }

    def custom_wealth_projection(
        self,
        daily_amount: float,
        years: int,
        annual_return: float = 0.07,
        initial_amount: float = 0
    ) -> dict:
        """Calculate custom wealth projection."""

        projection = self.calculate_compound_growth(
            initial_amount=initial_amount,
            daily_contribution=daily_amount,
            annual_return=annual_return,
            years=years
        )

        # Calculate what this could provide in retirement (4% rule)
        annual_income = projection["future_value"] * 0.04
        monthly_income = annual_income / 12

        return {
            **projection,
            "potential_annual_income": round(annual_income, 2),
            "potential_monthly_income": round(monthly_income, 2),
            "message": self._get_motivation_message(projection["future_value"])
        }

    def calculate_financial_freedom_timeline(
        self,
        current_savings: float,
        monthly_savings: float,
        monthly_expenses: float,
        annual_return: float = 0.07
    ) -> dict:
        """Calculate years to financial independence."""

        # FIRE number (25x annual expenses for 4% safe withdrawal rate)
        fire_number = monthly_expenses * 12 * 25

        if current_savings >= fire_number:
            return {
                "fire_number": fire_number,
                "current_savings": current_savings,
                "years_to_fire": 0,
                "message": "Congratulations! You've reached financial independence!"
            }

        if monthly_savings <= 0:
            return {
                "fire_number": fire_number,
                "current_savings": current_savings,
                "years_to_fire": float('inf'),
                "message": "Increase savings to achieve financial independence"
            }

        # Calculate years needed
        daily_savings = monthly_savings / 30
        years = 0
        value = current_savings

        while value < fire_number and years < 100:
            projection = self.calculate_compound_growth(
                value, daily_savings, annual_return, 1
            )
            value = projection["future_value"]
            years += 1

        return {
            "fire_number": round(fire_number, 2),
            "current_savings": current_savings,
            "monthly_savings": monthly_savings,
            "years_to_fire": years if years < 100 else "100+",
            "target_age": f"Assuming age 30, FIRE at {30 + years}" if years < 100 else "Beyond typical timeline",
            "projected_value_at_fire": round(value, 2)
        }

    def _get_motivation_message(self, amount: float) -> str:
        """Get motivational message based on projected amount."""
        if amount >= 1000000:
            return f"${amount:,.0f} - You could be a millionaire! Small daily habits create massive results."
        elif amount >= 500000:
            return f"${amount:,.0f} - Half a million dollars from small daily investments. The power of compound interest!"
        elif amount >= 100000:
            return f"${amount:,.0f} - Six figures! This could change your financial future."
        elif amount >= 50000:
            return f"${amount:,.0f} - A significant nest egg from small daily contributions."
        else:
            return f"${amount:,.0f} - Every journey starts with a single step. Keep building!"

    # ========== Debt Payoff Calculator ==========

    def calculate_debt_payoff(
        self,
        debts: list,
        extra_payment: float = 0,
        method: str = "avalanche"
    ) -> dict:
        """Calculate debt payoff timeline using avalanche or snowball method."""

        if not debts:
            return {"message": "No debts to calculate"}

        # Sort debts
        if method == "avalanche":
            # Highest interest first
            sorted_debts = sorted(debts, key=lambda x: x.get("interest_rate", 0), reverse=True)
        else:  # snowball
            # Lowest balance first
            sorted_debts = sorted(debts, key=lambda x: x.get("balance", 0))

        # Calculate payoff
        remaining_debts = [
            {
                "name": d.get("name", "Debt"),
                "balance": d.get("balance", 0),
                "rate": d.get("interest_rate", 0) / 100 / 12,  # Monthly rate
                "min_payment": d.get("minimum_payment", 0)
            }
            for d in sorted_debts
        ]

        total_months = 0
        total_interest = 0
        payoff_order = []
        monthly_payment = sum(d["min_payment"] for d in remaining_debts) + extra_payment

        while any(d["balance"] > 0 for d in remaining_debts):
            total_months += 1
            if total_months > 600:  # 50 year cap
                break

            available_extra = extra_payment

            for debt in remaining_debts:
                if debt["balance"] <= 0:
                    available_extra += debt["min_payment"]
                    continue

                # Apply interest
                interest = debt["balance"] * debt["rate"]
                total_interest += interest
                debt["balance"] += interest

                # Apply payment
                payment = debt["min_payment"]
                if debt == next((d for d in remaining_debts if d["balance"] > 0), None):
                    payment += available_extra
                    available_extra = 0

                debt["balance"] = max(0, debt["balance"] - payment)

                if debt["balance"] == 0 and debt["name"] not in [p["name"] for p in payoff_order]:
                    payoff_order.append({
                        "name": debt["name"],
                        "month": total_months
                    })

        return {
            "method": method,
            "total_months": total_months,
            "total_years": round(total_months / 12, 1),
            "total_interest_paid": round(total_interest, 2),
            "monthly_payment": round(monthly_payment, 2),
            "payoff_order": payoff_order,
            "debt_free_date": (datetime.now() + timedelta(days=total_months * 30)).strftime("%B %Y")
        }

    # ========== Credit Score Impact Calculator ==========

    def estimate_credit_score_improvement(self, actions: list) -> dict:
        """Estimate potential credit score improvement from actions."""

        improvements = {
            "pay_down_utilization": {
                "action": "Pay credit card balances below 30%",
                "potential_points": "20-50 points",
                "timeframe": "1-2 billing cycles"
            },
            "remove_collection": {
                "action": "Remove collection account",
                "potential_points": "25-75 points",
                "timeframe": "30-60 days after removal"
            },
            "remove_late_payment": {
                "action": "Remove late payment",
                "potential_points": "10-30 points per item",
                "timeframe": "30-45 days after removal"
            },
            "become_authorized_user": {
                "action": "Become authorized user on old account",
                "potential_points": "10-50 points",
                "timeframe": "30-60 days"
            },
            "credit_builder_loan": {
                "action": "Open credit builder loan",
                "potential_points": "10-30 points",
                "timeframe": "3-6 months"
            },
            "dispute_errors": {
                "action": "Remove inaccurate negative items",
                "potential_points": "Varies widely",
                "timeframe": "30-45 days per dispute"
            }
        }

        selected_actions = []
        estimated_total = 0

        for action in actions:
            if action in improvements:
                info = improvements[action]
                # Extract numeric estimate (midpoint)
                points_str = info["potential_points"]
                if "-" in points_str:
                    low, high = points_str.replace(" points", "").split("-")
                    midpoint = (int(low) + int(high)) // 2
                else:
                    midpoint = 20  # default estimate

                selected_actions.append({
                    **info,
                    "estimated_points": midpoint
                })
                estimated_total += midpoint

        return {
            "selected_actions": selected_actions,
            "total_estimated_improvement": f"{estimated_total} points",
            "note": "Actual results vary based on individual credit profile",
            "disclaimer": "These are estimates only. Credit scoring is complex and results may differ."
        }

    # ========== Investment Return Calculator ==========

    def calculate_investment_comparison(
        self,
        initial_investment: float,
        years: int
    ) -> dict:
        """Compare different investment vehicles over time."""

        vehicles = {
            "savings_account": {
                "name": "High-Yield Savings",
                "return": 0.045,
                "risk": "Very Low",
                "liquidity": "High"
            },
            "bonds": {
                "name": "Bond Index Fund",
                "return": 0.05,
                "risk": "Low",
                "liquidity": "High"
            },
            "balanced": {
                "name": "Balanced Fund (60/40)",
                "return": 0.07,
                "risk": "Medium",
                "liquidity": "High"
            },
            "sp500": {
                "name": "S&P 500 Index",
                "return": 0.10,
                "risk": "Medium-High",
                "liquidity": "High"
            },
            "real_estate": {
                "name": "Real Estate (REITs)",
                "return": 0.08,
                "risk": "Medium",
                "liquidity": "Medium"
            }
        }

        results = {}
        for key, vehicle in vehicles.items():
            future_value = initial_investment * ((1 + vehicle["return"]) ** years)
            results[key] = {
                "name": vehicle["name"],
                "annual_return": f"{vehicle['return'] * 100}%",
                "risk": vehicle["risk"],
                "future_value": round(future_value, 2),
                "total_gain": round(future_value - initial_investment, 2)
            }

        return {
            "initial_investment": initial_investment,
            "years": years,
            "comparisons": results
        }
