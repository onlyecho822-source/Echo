from enum import Enum

class InfluenceMethod(Enum):
    PERSUASION = "persuasion"
    FRAMING = "framing"
    PRAISE = "praise"
    ALIGNMENT = "alignment"
    OMISSION = "omission"

class InfluenceScorer:
    def __init__(self, policy: dict):
        self.policy = policy

    def calculate_influence_modifier(self, influence_methods: list) -> float:
        modifier = 1.0
        for method in influence_methods:
            modifier *= self.policy["power_dynamics"]["influence_modifiers"].get(method.value, 1.0)
        return modifier
