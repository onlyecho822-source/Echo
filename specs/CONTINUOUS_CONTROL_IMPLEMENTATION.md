# Echo Continuous Control System: Implementation Specification

**Specification:** Echo Formal Spec v2.4 (Manus Procedure)  
**Author:** Manus AI  
**Date:** 2026-01-14

---

## Executive Summary

This document provides the implementation bridge from the continuous control theory (v2.4) to executable code and Zapier configurations. It defines the sensing layer (State Observer), the control layer (K Matrix Executor), and the actuation layer (Throttle and Actuators).

---

## Part 1: The Throttle (`u₄`) — Continuous GKP

### 1.1 Airtable Schema: `system_throttle`

| Field Name | Type | Description | Default |
|---|---|---|---|
| `Throttle ID` | Single line text | Identifier (e.g., `main_throttle`). | `main_throttle` |
| `Throttle Percentage` | Number (0-100) | Current system throttle level. 100 = full speed, 0 = halted. | `100` |
| `Mode` | Single select | `AUTO`, `MANUAL`, `LOCKED`. | `AUTO` |
| `Last Updated` | Date/Time | Timestamp of last update. | Auto |
| `Updated By` | Single line text | System or admin that made the update. | `system` |
| `Reason` | Long text | Reason for the current throttle level. | - |

### 1.2 Zap Modification: Throttle Gate

Every core Zap (`INTENT-Router`, `A-CMAP-Review`, `Evidence-Binder`) must be modified to include a **Throttle Gate** as the first steps.

**Step 1: Find Record in Airtable**
- **App:** Airtable
- **Action:** Find Record
- **Base:** `Echo EIL`
- **Table:** `system_throttle`
- **Search By Field:** `Throttle ID`
- **Search Value:** `main_throttle`

**Step 2: Code by Zapier (Probabilistic Gate)**
- **Input Data:** `throttle: {{airtable_throttle_percentage}}`
- **Code:**
  ```javascript
  // Probabilistic gate based on throttle percentage
  const throttle = parseFloat(inputData.throttle);
  const random = Math.random() * 100;
  
  if (random > throttle) {
    // Block this execution
    return { action: 'BLOCK', reason: `Throttled at ${throttle}%` };
  }
  return { action: 'PROCEED' };
  ```

**Step 3: Filter by Zapier**
- **Condition:** `action` from Step 2 is `PROCEED`.
- **Result:** If blocked, the Zap stops here. If proceed, it continues to the main logic.

---

## Part 2: The State Observer (`S(t)` Estimator)

### 2.1 Airtable Schema: `system_state`

This table stores the sampled state vector `S(t)`.

| Field Name | Type | Description |
|---|---|---|
| `Sample ID` | Auto Number | Auto-incrementing sample ID. |
| `Timestamp` | Date/Time | Time of sample. |
| `H_throughput` | Number | Tasks completed in the last interval. |
| `H_error_rate` | Number | Percentage of tasks that errored. |
| `C_chain_integrity` | Number (0-1) | Probability of hash chain validity. |
| `R_risk_posture` | Number | Current risk level (composite score). |
| `L_ledger_depth` | Number | Total records in `raw_events`. |
| `Q_queue_length` | Number | Total pending jobs. |

### 2.2 Zap: `State-Observer`

**Trigger:** Schedule by Zapier (every 5 minutes)

**Actions:**

**Step 1: Get Zapier Task History (via Webhook to Zapier Stats API or manual counter)**
- Calculate `H_throughput` and `H_error_rate`.

**Step 2: Get Airtable Record Count for `raw_events`**
- This gives `L_ledger_depth`.

**Step 3: Get Airtable Record for `chain_state`**
- Verify `Last Hash` matches expected. Calculate `C_chain_integrity`.

**Step 4: Code by Zapier (Calculate Risk Posture)**
- **Code:**
  ```javascript
  // Composite risk score
  const errorRate = parseFloat(inputData.H_error_rate);
  const chainIntegrity = parseFloat(inputData.C_chain_integrity);
  const queueLength = parseFloat(inputData.Q_queue_length);
  
  // Risk increases with errors and queue length, decreases with chain integrity
  const risk = (errorRate * 0.4) + ((1 - chainIntegrity) * 0.4) + (queueLength / 100 * 0.2);
  return { R_risk_posture: Math.min(risk, 1.0) }; // Cap at 1.0
  ```

**Step 5: Create Record in Airtable (`system_state`)**
- Log the full state vector `S(t)`.

---

## Part 3: The Controller (`K` Matrix Executor)

### 3.1 Airtable Schema: `controller_config`

This table stores the tunable gain matrix `K`.

| Field Name | Type | Description | Default |
|---|---|---|---|
| `Config ID` | Single line text | Identifier. | `main_controller` |
| `K_throttle` | Number | Gain for throttle adjustment. | `50` |
| `K_threshold` | Number | Gain for A-CMAP threshold adjustment. | `0.5` |
| `S_ref_risk` | Number | Reference risk posture. | `0.1` |
| `S_ref_queue` | Number | Reference queue length. | `5` |

### 3.2 Zap: `Controller-Executor`

**Trigger:** Schedule by Zapier (every 5 minutes, offset from State-Observer)

**Actions:**

**Step 1: Get Latest State from `system_state`**
- Find the most recent record.

**Step 2: Get Controller Config from `controller_config`**
- Find record with `Config ID` = `main_controller`.

**Step 3: Code by Zapier (Calculate Control Inputs)**
- **Code:**
  ```javascript
  // Control Law: u(t) = K * (S_ref - S(t))
  const S_risk = parseFloat(inputData.R_risk_posture);
  const S_queue = parseFloat(inputData.Q_queue_length);
  const S_ref_risk = parseFloat(inputData.S_ref_risk);
  const S_ref_queue = parseFloat(inputData.S_ref_queue);
  const K_throttle = parseFloat(inputData.K_throttle);
  
  // Calculate error
  const error_risk = S_ref_risk - S_risk;  // Negative if risk is too high
  const error_queue = S_ref_queue - S_queue; // Negative if queue is too long
  
  // Calculate throttle adjustment
  // If risk is high (error_risk negative), reduce throttle
  // If queue is long (error_queue negative), reduce throttle
  let throttle_adjustment = (error_risk * K_throttle) + (error_queue * K_throttle * 0.5);
  
  // Get current throttle and apply adjustment
  let current_throttle = parseFloat(inputData.current_throttle);
  let new_throttle = current_throttle + throttle_adjustment;
  
  // Clamp to [0, 100]
  new_throttle = Math.max(0, Math.min(100, new_throttle));
  
  return { 
    new_throttle: Math.round(new_throttle),
    adjustment: throttle_adjustment,
    error_risk: error_risk,
    error_queue: error_queue
  };
  ```

**Step 4: Update Record in Airtable (`system_throttle`)**
- Set `Throttle Percentage` to `new_throttle` from Step 3.
- Set `Updated By` to `controller`.
- Set `Reason` to `Auto-adjusted: risk_error=${error_risk}, queue_error=${error_queue}`.

---

## Part 4: Python Implementation (Alternative to Zapier)

For more precise control, the State Observer and Controller can be implemented as Python services.

### 4.1 State Observer (`state_observer.py`)

```python
"""
Echo State Observer
Samples system metrics and outputs state vector S(t).
"""
import time
from datetime import datetime
from typing import NamedTuple

class StateVector(NamedTuple):
    timestamp: datetime
    H_throughput: float
    H_error_rate: float
    C_chain_integrity: float
    R_risk_posture: float
    L_ledger_depth: int
    Q_queue_length: int

class StateObserver:
    def __init__(self, airtable_client, zapier_client):
        self.airtable = airtable_client
        self.zapier = zapier_client
    
    def sample(self) -> StateVector:
        # Get metrics from various sources
        throughput, error_rate = self._get_zapier_metrics()
        chain_integrity = self._verify_chain_integrity()
        ledger_depth = self._get_ledger_depth()
        queue_length = self._get_queue_length()
        
        # Calculate composite risk
        risk = (error_rate * 0.4) + ((1 - chain_integrity) * 0.4) + (queue_length / 100 * 0.2)
        
        return StateVector(
            timestamp=datetime.utcnow(),
            H_throughput=throughput,
            H_error_rate=error_rate,
            C_chain_integrity=chain_integrity,
            R_risk_posture=min(risk, 1.0),
            L_ledger_depth=ledger_depth,
            Q_queue_length=queue_length
        )
    
    def _get_zapier_metrics(self):
        # Implementation: Query Zapier API or internal counter
        pass
    
    def _verify_chain_integrity(self):
        # Implementation: Verify hash chain in EIL
        pass
    
    def _get_ledger_depth(self):
        # Implementation: Count records in raw_events
        pass
    
    def _get_queue_length(self):
        # Implementation: Count pending jobs
        pass
```

### 4.2 Controller (`controller.py`)

```python
"""
Echo Controller
Implements control law u(t) = K(S_ref - S(t)).
"""
import numpy as np
from dataclasses import dataclass

@dataclass
class ControllerConfig:
    K_throttle: float = 50.0
    K_threshold: float = 0.5
    S_ref_risk: float = 0.1
    S_ref_queue: float = 5.0

@dataclass
class ControlOutput:
    u1_ingestion_rate: float
    u2_compute_allocation: str
    u3_acmap_threshold: float
    u4_throttle: float

class Controller:
    def __init__(self, config: ControllerConfig):
        self.config = config
        self.current_throttle = 100.0
    
    def compute(self, state: 'StateVector') -> ControlOutput:
        # Calculate errors
        error_risk = self.config.S_ref_risk - state.R_risk_posture
        error_queue = self.config.S_ref_queue - state.Q_queue_length
        
        # Control law for throttle
        throttle_adjustment = (error_risk * self.config.K_throttle) + \
                              (error_queue * self.config.K_throttle * 0.5)
        
        new_throttle = np.clip(self.current_throttle + throttle_adjustment, 0, 100)
        self.current_throttle = new_throttle
        
        # Control law for A-CMAP threshold
        # Higher risk -> higher threshold (more conservative)
        new_threshold = 2.0 + (state.R_risk_posture * self.config.K_threshold * 2)
        
        # Compute allocation based on queue length
        if state.Q_queue_length > 20:
            compute_allocation = 'FAST_MODEL'  # Use cheaper model
        else:
            compute_allocation = 'FULL_MODEL'
        
        return ControlOutput(
            u1_ingestion_rate=new_throttle / 100,
            u2_compute_allocation=compute_allocation,
            u3_acmap_threshold=new_threshold,
            u4_throttle=new_throttle
        )
```

---

## Implementation Checklist

### Phase 1: Throttle (`u₄`)
- [ ] Create `system_throttle` table in Airtable
- [ ] Initialize with `throttle_percentage = 100`
- [ ] Add Throttle Gate to `INTENT-Router`
- [ ] Add Throttle Gate to `A-CMAP-Review`
- [ ] Add Throttle Gate to `Evidence-Binder`
- [ ] Test: Set throttle to 50%, verify ~50% of tasks are blocked

### Phase 2: State Observer
- [ ] Create `system_state` table in Airtable
- [ ] Create `State-Observer` Zap
- [ ] Test: Verify state samples are logged every 5 minutes

### Phase 3: Controller
- [ ] Create `controller_config` table in Airtable
- [ ] Initialize with default gains
- [ ] Create `Controller-Executor` Zap
- [ ] Test: Verify throttle auto-adjusts based on risk

### Phase 4: Tuning
- [ ] Run system under load
- [ ] Observe state vector behavior
- [ ] Adjust `K` gains to achieve desired response
- [ ] Document optimal gain values

---

## Success Criteria

| Metric | Target |
|---|---|
| Throttle response time | < 5 minutes from risk spike to throttle adjustment |
| State sampling frequency | Every 5 minutes |
| Throttle range | 0-100% with smooth transitions |
| Risk posture under normal load | < 0.1 |
| Automatic recovery from high risk | Within 15 minutes |
