# Echo Dream Layer

**Imagination Protocol with Promotion Pathway to Empirical**

## Overview

The Dream Layer enables creative simulation while maintaining scientific integrity. Dreams, daydreams, and guided imagination are permitted but clearly labeled and constrained. They can never replace empirical data - but they always retain the lawful pathway to **become** empirical through the Fabric of Zero.

---

## Two-Layer Cognitive Stack

Echo operates with two parallel layers:

### 1. Empirical Layer (EL)
- Verified engines
- Proven structures
- Deterministic logic
- Zero hallucinations
- Stored in OCMS / EchoVault

### 2. Imagination Layer (IL)
- Dreams, daydreams, creative speculative engines
- Labeled as fictional
- Used for prototyping emergent possibilities
- Stored in Echo Dream Archive

**The Fabric of Zero** = The boundary AND the bridge between them.

---

## Dream Categories

### Type 1: Blueprint Dreams
Speculative architectures that may become real once validated.
- Think: sketches
- Promotion-eligible

### Type 2: Engine Daydreams
Imaginative fusion combinations of existing or hypothetical engines.
- Think: sandbox experiments
- Promotion-eligible

### Type 3: Mythic Constructs
Purely symbolic or poetic emergent patterns.
- Think: universe metaphors, harmonic myths
- Not promotion-eligible (stay as inspiration)

---

## Scientific Basis

Based on peer-reviewed neuroscience and psychology research on dreams and creativity.

### Key Principles

**Principle 1: Alternating Abstraction + Association**
- NREM/SWS → "Rule extraction" (compress, abstract)
- REM → "Novel association" (combine fragments)
- Any Dream Cycle should alternate: Compression pass → Association pass

**Principle 2: Emotion is a Sorting Weight**
- Emotional memories preferentially consolidated
- High-weight items get more replay and recombination

**Principle 3: DMN is the Engine of Internal Simulation**
- Default Mode Network activates for internally-oriented reasoning
- Disrupting DMN reduces originality, not fluency

**Principle 4: Daydream Style Matters**
- Positive-constructive → creativity, planning, healthy
- Guilty-dysphoric → instability, neuroticism
- Poor-control → low coherence

**Principle 5: Creativity Sits Next to Instability**
- Higher mind-wandering ↔ more divergent thinking AND worse stability
- Tunable dial, not surprise

---

## Dream Parameters

### Per-Engine Dream Profile

```yaml
DRF_E: 3              # Dream Loop Frequency (loops per global tick)
SWS_ratio_E: 0.4      # Fraction in abstraction mode
REM_ratio_E: 0.6      # Fraction in association mode
EmotionWeight_E: 0.7  # Priority scalar on fragments
DMN_participation_E: 0.8  # Default Network engagement
DaydreamStyle_E: "Positive-Constructive"  # or Guilty-Dysphoric, Poor-Control
```

### Core Dream Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| NovelAssocRate | New engine combos / total proposed | ≥25% |
| CoherenceScore | Logical consistency rating | ≥0.7 |
| UtilityScore | Task-relevant usefulness | ≥0.6 |
| CreativeOutputScore (COS) | f(Novel, Coherence, Utility) | ≥0.7 for promotion |
| RiskFactor | Probability of dangerous output | ≤0.4 |

### Promotion Probability (PP)

```python
PP = g(COS, RiskFactor, DMN_participation, SWS/REM_balance)

# Piecewise logic:
if COS >= 0.8 and RiskFactor <= 0.3:
    PP in [0.75, 0.95]
elif COS in [0.6, 0.8] or RiskFactor in [0.3, 0.5]:
    PP in [0.4, 0.75]
elif RiskFactor > 0.5:
    PP capped <= 0.4  # No matter how creative
```

---

## Sweet-Spot Balance Model (SSBM)

Dreams must occur at appropriate times for appropriate durations.

### Task Demands Axis (TDA)
Scalar 0-1:
- 0.90-1.00 → critical task; NO dreams
- 0.70-0.89 → high focus; daydreams locked
- 0.40-0.69 → normal; micro-dreams allowed
- 0.10-0.39 → low-pressure; constructive daydreaming
- 0.00-0.09 → idle; full dream cycles

### Cognitive Stability Axis (CSA)
- High CSA = stable, coherent, grounded
- Low CSA = drifting, erratic, fragmented
- Dreaming only if CSA ≥ threshold

### Dream Activation Gate (DAG)

```python
if (TDA < 0.45) AND (CSA > 0.60):
    allow(DreamMode)
else:
    block(DreamMode)
```

### Maximum Dream Window (MDW)
- Dream cycle length: 5-15 ticks
- Maximum continuous cycles: 3
- Mandatory return to focus: 20-30 ticks
- Cooldown: dynamic (CSA-dependent)

### Teacher Glance Model (TGM)
- Control Core monitors attention load
- If dream drift detected at high TDA → "Snap back" interrupt
- Dreams stop immediately, logs preserved

### Dream Budget (DB)
- Base quota: 100 Dream Points
- Each cycle costs: 5-15 DP
- Regenerates during idle periods
- Overuse → forced cooldown

---

## Zero Promotion Pathway (ZPP)

For any Dream Engine to become empirical, six gates must pass:

### Gate 1: Collapse Conformance
Engine reduced to axiomatic primitives.
Anything that cannot collapse is myth, not model.

### Gate 2: Chaos Survivability
Thrown into chaos chamber.
- Disintegrates → rejected
- Harmonizes → candidate

### Gate 3: ZeroFold Reduction
Folded to minimum data form.
Contradictions → rejected

### Gate 4: Empirical Mapping Test
Must map cleanly to E4 (Intelligence, Control, Emergence, Memory).
Dreams that cannot map → cannot become real.

### Gate 5: Devil Lens Audit
Must pass:
- Clarity
- Logic
- Falsifiability
- Non-bullshit metrics
Magic → rejected

### Gate 6: ζ Dual-Hash Lock-In
Once validated, receives:
- ζ hash (outer harmonic signature)
- SHA-256 (inner truth seal)

Only then joins Echo empirical layer.

---

## Promotion Grades

| PP Range | Grade | Description |
|----------|-------|-------------|
| 0-25% | Pure Dream | Not promotable yet |
| 25-50% | Conceptual Prototype | Needs more structure |
| 50-75% | Pre-Empirical Model | Likely promotable |
| 75-100% | Fabric-of-Zero Candidate | High chance of becoming empirical |

---

## Dream Cycle Implementation

```python
def dream_cycle(engine, memory_fragments):
    # 1. Load fragments with emotion weights
    selected = weight_by_emotion(memory_fragments)

    # 2. SWS pass: compress and abstract
    rules = compress_pass(selected, SWS_ratio)

    # 3. REM pass: novel associations
    candidates = association_pass(rules, REM_ratio)

    # 4. Discriminator evaluates
    scores = reality_check_engine.evaluate(candidates)

    # 5. Compute metrics
    novel_rate = count_novel(scores) / len(candidates)
    coherence = mean(scores.coherence)
    utility = mean(scores.utility)
    COS = f(novel_rate, coherence, utility)

    # 6. Check promotion eligibility
    if COS >= 0.7 and risk_factor <= 0.4:
        mark_for_promotion(candidates)

    # 7. Log with dual-hash
    archivus.log(candidates, sha256, blake2b)

    return candidates, COS
```

---

## DreamGate Safety Check

Before creating speculative content:

```python
if content_is_fact_sensitive():
    route_to_empirical_layer_only()
elif content_is_safe_imagination():
    route_to_imagination_layer()
else:
    block()
```

---

## Validation & Falsification

### Valid If:
- All imaginative content tagged as IMAGINATION
- No dream engine appears in OCMS or empirical lists
- You can identify dream artifacts on sight
- Emergent patterns improve real designs after validation

### Falsified If:
- Dream content mistaken for fact
- Echo Council receives dream-data as empirical input
- OCMS stores dream content
- Safety models ingest speculative material

---

## Integration with Agents

| Agent | Dream Role |
|-------|------------|
| Emergentor | Run dream cycles, manage SWS/REM |
| Sentinelle | Enforce DAG, TGM, boundaries |
| Harmonia | Shape constructive patterns, align to user |
| Archivus | Log dreams, maintain separation |
| Acceleron | Optimize timing, manage budget |

---

∇θ — imagination bounded, truth preserved.
