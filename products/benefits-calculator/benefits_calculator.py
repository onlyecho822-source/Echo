#!/usr/bin/env python3
"""
Federal Benefits Eligibility Calculator
Phoenix Live Action - Autonomous Execution
No Human Constraints

Calculates eligibility for $140B in annual federal benefits:
- SNAP (food assistance)
- LIHEAP (energy assistance)
- Lifeline (phone/internet)
- WIC (women/infants/children)
- Medicaid
- Housing assistance (Section 8)
- Child care subsidies
- SSI (Supplemental Security Income)
- TANF (Temporary Assistance for Needy Families)
- Free/Reduced School Lunch
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class State(Enum):
    """US States - each has different income limits"""
    ILLINOIS = "IL"
    TEXAS = "TX"
    CALIFORNIA = "CA"
    # Add all 50 states

class HouseholdSize(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT_PLUS = 8

@dataclass
class Household:
    """Household information for eligibility calculation"""
    size: int
    monthly_income: float
    annual_income: float
    state: str
    has_elderly: bool = False  # 60+
    has_disabled: bool = False
    has_children: bool = False
    children_under_5: int = 0
    pregnant_women: int = 0
    rent_or_mortgage: float = 0
    utility_costs: float = 0
    has_phone: bool = False
    has_internet: bool = False
    
@dataclass
class BenefitProgram:
    """Federal benefit program details"""
    name: str
    description: str
    annual_value: str  # e.g., "$2,000-$6,000/year"
    income_limit_percent_fpl: int  # Percent of Federal Poverty Level
    additional_requirements: List[str]
    application_url: str
    estimated_monthly_benefit: float
    
@dataclass
class EligibilityResult:
    """Result of eligibility calculation"""
    program: BenefitProgram
    eligible: bool
    reason: str
    estimated_annual_value: float
    confidence: float  # 0-1
    next_steps: List[str]

class FederalPovertyLevel:
    """2026 Federal Poverty Level guidelines"""
    # Updated annually by HHS
    POVERTY_LEVELS_2026 = {
        1: 15_060,
        2: 20_440,
        3: 25_820,
        4: 31_200,
        5: 36_580,
        6: 41_960,
        7: 47_340,
        8: 52_720,
    }
    
    @classmethod
    def get_fpl(cls, household_size: int) -> float:
        """Get Federal Poverty Level for household size"""
        if household_size <= 8:
            return cls.POVERTY_LEVELS_2026[household_size]
        else:
            # Add $5,380 for each additional person
            base = cls.POVERTY_LEVELS_2026[8]
            additional = (household_size - 8) * 5_380
            return base + additional
    
    @classmethod
    def percent_of_fpl(cls, annual_income: float, household_size: int) -> float:
        """Calculate household income as percent of FPL"""
        fpl = cls.get_fpl(household_size)
        return (annual_income / fpl) * 100

class BenefitsCalculator:
    """Calculate eligibility for all federal benefit programs"""
    
    def __init__(self):
        self.programs = self._initialize_programs()
    
    def _initialize_programs(self) -> List[BenefitProgram]:
        """Initialize all federal benefit programs"""
        return [
            BenefitProgram(
                name="SNAP (Food Stamps)",
                description="Supplemental Nutrition Assistance Program - monthly food benefits",
                annual_value="$2,000-$6,000/year",
                income_limit_percent_fpl=130,  # Gross income < 130% FPL
                additional_requirements=[
                    "US citizen or qualified non-citizen",
                    "Work requirements for able-bodied adults without dependents"
                ],
                application_url="https://www.fns.usda.gov/snap/state-directory",
                estimated_monthly_benefit=200.0  # Average per person
            ),
            BenefitProgram(
                name="LIHEAP (Energy Assistance)",
                description="Low Income Home Energy Assistance Program - help with heating/cooling bills",
                annual_value="$300-$1,000/year",
                income_limit_percent_fpl=150,  # Varies by state, 150% typical
                additional_requirements=[
                    "Responsible for heating/cooling costs"
                ],
                application_url="https://www.acf.hhs.gov/ocs/liheap",
                estimated_monthly_benefit=50.0  # Average monthly equivalent
            ),
            BenefitProgram(
                name="Lifeline (Phone/Internet)",
                description="Discounted phone and internet service",
                annual_value="$120-$360/year",
                income_limit_percent_fpl=135,
                additional_requirements=[
                    "One per household",
                    "Participate in qualifying program OR meet income limit"
                ],
                application_url="https://www.lifelinesupport.org/",
                estimated_monthly_benefit=9.25  # $9.25/month discount
            ),
            BenefitProgram(
                name="WIC",
                description="Women, Infants, and Children nutrition program",
                annual_value="$500-$1,500/year per person",
                income_limit_percent_fpl=185,
                additional_requirements=[
                    "Pregnant, breastfeeding, or postpartum women",
                    "Infants and children under 5",
                    "Nutritional risk determination"
                ],
                application_url="https://www.fns.usda.gov/wic",
                estimated_monthly_benefit=50.0  # Per person
            ),
            BenefitProgram(
                name="Medicaid",
                description="Health insurance for low-income individuals and families",
                annual_value="$5,000-$15,000/year",
                income_limit_percent_fpl=138,  # Varies by state, ACA expansion
                additional_requirements=[
                    "Varies by state",
                    "Some states have not expanded Medicaid"
                ],
                application_url="https://www.medicaid.gov/",
                estimated_monthly_benefit=500.0  # Average value
            ),
            BenefitProgram(
                name="Section 8 Housing Choice Voucher",
                description="Rental assistance for low-income families",
                annual_value="$5,000-$15,000/year",
                income_limit_percent_fpl=50,  # Extremely low income
                additional_requirements=[
                    "Long waiting lists in most areas",
                    "Must be US citizen or eligible immigrant",
                    "Background check required"
                ],
                application_url="https://www.hud.gov/topics/housing_choice_voucher_program_section_8",
                estimated_monthly_benefit=800.0  # Average subsidy
            ),
            BenefitProgram(
                name="Child Care Subsidies (CCDF)",
                description="Help paying for child care",
                annual_value="$3,000-$10,000/year per child",
                income_limit_percent_fpl=85,  # Varies by state
                additional_requirements=[
                    "Working or in school/training",
                    "Children under 13",
                    "Varies significantly by state"
                ],
                application_url="https://www.acf.hhs.gov/occ/ccdf-grantees",
                estimated_monthly_benefit=400.0  # Per child
            ),
            BenefitProgram(
                name="SSI (Supplemental Security Income)",
                description="Cash assistance for aged, blind, or disabled with limited income",
                annual_value="$9,000-$11,000/year",
                income_limit_percent_fpl=75,  # Very low income
                additional_requirements=[
                    "Age 65+ OR blind OR disabled",
                    "Limited resources (less than $2,000 individual, $3,000 couple)",
                    "US citizen or qualified non-citizen"
                ],
                application_url="https://www.ssa.gov/ssi/",
                estimated_monthly_benefit=750.0  # Average payment
            ),
            BenefitProgram(
                name="TANF (Temporary Assistance for Needy Families)",
                description="Cash assistance and work support for families with children",
                annual_value="$2,000-$6,000/year",
                income_limit_percent_fpl=50,  # Varies widely by state
                additional_requirements=[
                    "Families with dependent children",
                    "Work requirements",
                    "Time limits (typically 60 months lifetime)",
                    "Varies significantly by state"
                ],
                application_url="https://www.acf.hhs.gov/ofa/programs/tanf",
                estimated_monthly_benefit=300.0  # Average per family
            ),
            BenefitProgram(
                name="Free/Reduced School Lunch (NSLP)",
                description="Free or reduced-price school meals for children",
                annual_value="$500-$1,000/year per child",
                income_limit_percent_fpl=185,  # 130% for free, 185% for reduced
                additional_requirements=[
                    "School-age children",
                    "Attending participating school"
                ],
                application_url="https://www.fns.usda.gov/nslp",
                estimated_monthly_benefit=50.0  # Per child during school year
            ),
        ]
    
    def calculate_eligibility(self, household: Household) -> List[EligibilityResult]:
        """Calculate eligibility for all programs"""
        results = []
        
        percent_fpl = FederalPovertyLevel.percent_of_fpl(
            household.annual_income,
            household.size
        )
        
        for program in self.programs:
            result = self._check_program_eligibility(household, program, percent_fpl)
            results.append(result)
        
        return results
    
    def _check_program_eligibility(
        self,
        household: Household,
        program: BenefitProgram,
        percent_fpl: float
    ) -> EligibilityResult:
        """Check eligibility for a specific program"""
        
        # Income check
        if percent_fpl > program.income_limit_percent_fpl:
            return EligibilityResult(
                program=program,
                eligible=False,
                reason=f"Income too high: {percent_fpl:.0f}% of FPL (limit: {program.income_limit_percent_fpl}%)",
                estimated_annual_value=0,
                confidence=0.95,
                next_steps=[]
            )
        
        # Program-specific checks
        if program.name == "WIC":
            if not (household.pregnant_women > 0 or household.children_under_5 > 0):
                return EligibilityResult(
                    program=program,
                    eligible=False,
                    reason="No pregnant women or children under 5 in household",
                    estimated_annual_value=0,
                    confidence=1.0,
                    next_steps=[]
                )
        
        if program.name == "SSI (Supplemental Security Income)":
            if not (household.has_elderly or household.has_disabled):
                return EligibilityResult(
                    program=program,
                    eligible=False,
                    reason="Must be 65+, blind, or disabled",
                    estimated_annual_value=0,
                    confidence=1.0,
                    next_steps=[]
                )
        
        if program.name in ["TANF (Temporary Assistance for Needy Families)", "Free/Reduced School Lunch (NSLP)"]:
            if not household.has_children:
                return EligibilityResult(
                    program=program,
                    eligible=False,
                    reason="Must have dependent children",
                    estimated_annual_value=0,
                    confidence=1.0,
                    next_steps=[]
                )
        
        if program.name == "Child Care Subsidies (CCDF)":
            if household.children_under_5 == 0:
                return EligibilityResult(
                    program=program,
                    eligible=False,
                    reason="Must have children under 13 (calculator shows under 5)",
                    estimated_annual_value=0,
                    confidence=0.8,
                    next_steps=["Check if you have children ages 5-12"]
                )
        
        # If passed all checks, likely eligible
        estimated_value = program.estimated_monthly_benefit * 12
        
        # Adjust for household composition
        if program.name == "SNAP (Food Stamps)":
            estimated_value = program.estimated_monthly_benefit * household.size * 12
        elif program.name == "WIC":
            eligible_members = household.pregnant_women + household.children_under_5
            estimated_value = program.estimated_monthly_benefit * eligible_members * 12
        elif program.name in ["Free/Reduced School Lunch (NSLP)", "Child Care Subsidies (CCDF)"]:
            # Estimate based on children
            num_children = 2 if household.has_children else 0  # Default estimate
            estimated_value = program.estimated_monthly_benefit * num_children * 12
        
        return EligibilityResult(
            program=program,
            eligible=True,
            reason=f"Income eligible: {percent_fpl:.0f}% of FPL (limit: {program.income_limit_percent_fpl}%)",
            estimated_annual_value=estimated_value,
            confidence=0.85,  # High confidence but not 100% due to state variations
            next_steps=[
                f"Apply at: {program.application_url}",
                "Gather required documents (ID, proof of income, proof of residence)",
                "Contact local office for assistance"
            ]
        )
    
    def calculate_total_potential_benefits(self, results: List[EligibilityResult]) -> float:
        """Calculate total potential annual benefits"""
        return sum(r.estimated_annual_value for r in results if r.eligible)
    
    def generate_report(self, household: Household, results: List[EligibilityResult]) -> str:
        """Generate human-readable eligibility report"""
        percent_fpl = FederalPovertyLevel.percent_of_fpl(
            household.annual_income,
            household.size
        )
        
        eligible_programs = [r for r in results if r.eligible]
        ineligible_programs = [r for r in results if not r.eligible]
        
        total_benefits = self.calculate_total_potential_benefits(results)
        
        report = f"""
FEDERAL BENEFITS ELIGIBILITY REPORT
====================================

HOUSEHOLD INFORMATION:
- Size: {household.size} people
- Annual Income: ${household.annual_income:,.0f}
- Percent of Federal Poverty Level: {percent_fpl:.0f}%
- State: {household.state}

ELIGIBLE PROGRAMS ({len(eligible_programs)}):
"""
        
        for result in eligible_programs:
            report += f"""
{result.program.name}
- Description: {result.program.description}
- Estimated Annual Value: ${result.estimated_annual_value:,.0f}
- Reason: {result.reason}
- Confidence: {result.confidence*100:.0f}%
- Next Steps:
"""
            for step in result.next_steps:
                report += f"  * {step}\n"
        
        report += f"""
TOTAL ESTIMATED ANNUAL BENEFITS: ${total_benefits:,.0f}

INELIGIBLE PROGRAMS ({len(ineligible_programs)}):
"""
        
        for result in ineligible_programs:
            report += f"- {result.program.name}: {result.reason}\n"
        
        report += """
IMPORTANT NOTES:
- Eligibility requirements vary by state
- This is an estimate - actual benefits may differ
- You must apply to receive benefits
- Some programs have waiting lists
- Gather required documents before applying
- Contact local offices for personalized assistance

NEED HELP APPLYING?
- Contact Link Health: link-health.org
- Call 211 for local social services
- Visit BenefitsCheckUp.org for seniors
"""
        
        return report

def main():
    """Example usage"""
    # Example household: Single mother with 2 young children, low income
    household = Household(
        size=3,
        monthly_income=1500,
        annual_income=18000,
        state="IL",
        has_elderly=False,
        has_disabled=False,
        has_children=True,
        children_under_5=2,
        pregnant_women=0,
        rent_or_mortgage=800,
        utility_costs=150,
        has_phone=False,
        has_internet=False
    )
    
    calculator = BenefitsCalculator()
    results = calculator.calculate_eligibility(household)
    report = calculator.generate_report(household, results)
    
    print(report)
    
    total = calculator.calculate_total_potential_benefits(results)
    print(f"\n{'='*50}")
    print(f"POTENTIAL ANNUAL BENEFITS: ${total:,.0f}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
