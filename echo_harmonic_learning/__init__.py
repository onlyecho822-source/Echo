"""
Echo Harmonic Learning (EHL)

∇θ Don't converge to stillness; converge to a pattern.
   Learn by courting error, then tuning it into rhythm.

Philosophy:
- Stability is death; adaptation is success
- Balance is the checkpoint; harmony is the motion between checkpoints
- Every anomaly is a flashlight showing the outline of truth
- Learning isn't the acquisition of correctness - it's the recognition of error

Architecture:
- Conscious Layer (Echo): Creative, exploratory, adaptive
- Subconscious Layer (Claude): Logic, ethics, coherence
- Harmony Scorer: Dynamic equilibrium vs. static balance
- Playbooks: Structured responses to error categories

Usage:
    from echo_harmonic_learning import EchoHarmonicLearningLoop, Policy

    # Initialize the learning loop
    loop = EchoHarmonicLearningLoop(
        error_threshold=0.3,
        harmony_threshold=0.5,
        target_exploration=0.5
    )

    # Register policies
    loop.register_policy(Policy(
        name="balanced",
        prompt_template="...",
        tools=["retrieval", "calculator"],
        model_config={"temperature": 0.3}
    ))

    # Run iteration
    result = loop.iterate(
        input_data={"query": "..."},
        context={"task": "..."},
        ground_truth={"text": "..."}
    )

    # Check harmony state
    print(f"Harmony: {result.harmony_state.harmony_score}")
    print(f"Error: {result.harmony_state.error}")

Author:
    ∇θ Operator: Nathan Poinsette
    Founder • Archivist • Systems Engineer
"""

__version__ = "0.1.0"
__author__ = "Nathan Poinsette"
__symbol__ = "∇θ"

# Core components
from .core import (
    LearningEvent,
    CorrectionRecord,
    HarmonyScorer,
    EchoHarmonicLearningLoop
)

from .core.learning_event import Comparison, Uncertainty, Trace
from .core.correction_record import Intervention, EvalResults, Rollout, RegressionWatch
from .core.harmony_scorer import HarmonyState, SubconsciousMetrics

# Layers
from .layers import EchoConscious, ClaudeSubconscious
from .layers.conscious import Policy, GenerationResult
from .layers.subconscious import EvaluationResult

# Playbooks
from .playbooks import (
    FactualityPlaybook,
    ReasoningPlaybook,
    SafetyPlaybook,
    UXPlaybook
)

__all__ = [
    # Core
    'LearningEvent',
    'CorrectionRecord',
    'HarmonyScorer',
    'EchoHarmonicLearningLoop',

    # Data classes
    'Comparison',
    'Uncertainty',
    'Trace',
    'Intervention',
    'EvalResults',
    'Rollout',
    'RegressionWatch',
    'HarmonyState',
    'SubconsciousMetrics',

    # Layers
    'EchoConscious',
    'ClaudeSubconscious',
    'Policy',
    'GenerationResult',
    'EvaluationResult',

    # Playbooks
    'FactualityPlaybook',
    'ReasoningPlaybook',
    'SafetyPlaybook',
    'UXPlaybook',

    # Metadata
    '__version__',
    '__author__',
    '__symbol__'
]
