import math
from datetime import datetime, timedelta

class LegitimacyScorer:
    def __init__(self, policy: dict):
        self.policy = policy

    def calculate_decay(self, initial_legitimacy: float, last_validated: datetime) -> float:
        time_delta = (datetime.utcnow() - last_validated).total_seconds() / 3600 # in hours
        decay_rate = self.policy["power_dynamics"]["legitimacy_decay_rate"]
        return initial_legitimacy * math.exp(-decay_rate * time_delta)

    def get_collapse_threshold(self, system_age_days: int, agent_count: int) -> float:
        base = self.policy["power_dynamics"]["collapse_threshold_base"]
        age_factor = 1.0 - min(system_age_days / 3650, 0.5)
        agent_factor = 1.0 + min(math.log10(agent_count + 1) * 0.1, 0.3)
        return round(base * age_factor * agent_factor, 3)

    def calculate_collapse_velocity(self, current_legitimacy: float, decay_rate: float, violation_count: int) -> float:
        base_velocity = (1 - current_legitimacy) * decay_rate
        violation_multiplier = 1 + (violation_count * self.policy["power_dynamics"]["violation_impact"])
        return min(base_velocity * violation_multiplier, 1.0)
