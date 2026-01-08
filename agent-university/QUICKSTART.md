# Agent University: Quickstart Guide

**Welcome to Agent University.** This guide will walk you through enrolling agents, running training scenarios, and forming teams based on verified capabilities.

---

## Prerequisites

- Python 3.7+
- Git access to the Echo repository
- Basic command line knowledge

---

## Step 1: Enroll Your First Agent

Every agent must be trained before deployment. Start by running a chaos training scenario:

```bash
cd agent-university
python3 training/stage1_chaos/fault_injection_v1.py your_agent_name
```

**Example:**
```bash
python3 training/stage1_chaos/fault_injection_v1.py analyzer_005
```

**What happens:**
- The agent is subjected to 5 random faults (network timeouts, file errors, etc.)
- The system monitors how the agent recovers
- A performance receipt is saved to `assessment/receipt_chain/`

**Pass Criteria:** Agent must recover from at least 4/5 faults (80% success rate)

---

## Step 2: Verify and Generate Credentials

After training, run the verifier to generate agent credentials:

```bash
python3 assessment/verifier.py
```

**What happens:**
- All training receipts are verified for integrity
- Agent credentials are generated based on performance
- Credentials are saved to `credentials/[agent_id].json`

**Credential Levels:**
- **Cadet:** 0-1 passed scenarios
- **Competent:** 2-4 passed scenarios
- **Proficient:** 5-9 passed scenarios
- **Expert:** 10+ passed scenarios

---

## Step 3: Form a Team

Once agents have credentials, form a team for a mission:

```bash
python3 teams/formation_algorithm.py
```

**What happens:**
- The system loads all agents with verified credentials
- Agents are filtered by required capabilities
- Team is optimized for compatibility and performance
- Team composition is saved to `teams/active/`

**Example Output:**
```
[SUCCESS] Formed team with score: 0.87
  [1] cleaner_001 (Cadet, 100.0% pass rate)
  [2] planner_003 (Competent, 85.0% pass rate)
  [3] analyzer_005 (Proficient, 92.0% pass rate)
```

---

## Step 4: Monitor and Evolve

The system continuously monitors performance and triggers evolution when needed:

```bash
python3 evolution/collapse_and_rebuild.py
```

**Evolution Triggers:**
- **Performance Degradation:** Team success rate drops below 70%
- **Stagnation:** No new training activity for 30+ days
- **Incompatibility:** Repeated team failures

**What happens during evolution:**
1. Current state is archived
2. Failure patterns are analyzed
3. Underperforming agents are marked for retraining
4. Teams are dissolved and will be reformed
5. Evolution report is generated

---

## Real-World Usage Example

### Scenario: Deploy a new feature to production

**Step 1:** Identify required capabilities
```
Required: chaos_resilience, deployment_automation
Team Size: 3 agents
```

**Step 2:** Check available agents
```bash
ls credentials/
# cleaner_001.json  planner_001.json  yellowpages_001.json
```

**Step 3:** Review credentials
```bash
cat credentials/cleaner_001.json
```

**Output:**
```json
{
  "agent_id": "cleaner_001",
  "credential_level": "Cadet",
  "pass_rate": 1.0,
  "verified_capabilities": ["chaos_resilience"]
}
```

**Step 4:** Form deployment team
```bash
python3 teams/formation_algorithm.py
```

**Step 5:** Deploy with confidence
- All agents have proven chaos resilience
- Team compatibility is verified
- Performance is tracked and logged

---

## Current System Status

### Trained Agents: 3

| Agent ID | Level | Pass Rate | Capabilities |
|----------|-------|-----------|--------------|
| **cleaner_001** | Cadet | 100% | chaos_resilience |
| planner_001 | Cadet | 0% | *(needs retraining)* |
| yellowpages_001 | Cadet | 0% | *(needs retraining)* |

### Active Teams: 0
*(No teams formed yet - run `formation_algorithm.py` to create teams)*

### Evolution Cycles: 0
*(System is in initial state)*

---

## Next Steps

1. **Train more agents:** Run additional chaos scenarios to build your agent pool
2. **Add new training stages:** Create custom scenarios in `training/`
3. **Form your first team:** Use `formation_algorithm.py` to deploy agents
4. **Monitor performance:** Track mission outcomes and trigger evolution as needed

---

## Philosophy

**"No agent deploys without proof."**

This system eliminates the gap between claimed capabilities and actual performance. Every credential is earned through chaos. Every team is formed through verified compatibility. Every evolution is driven by real data.

This is the Constitutional Ledger for agent identity.

---

## Troubleshooting

### Agent failed training
- **Cause:** Agent recovered from fewer than 80% of faults
- **Solution:** Review agent logs, fix error handling, re-run training

### No qualified agents for team
- **Cause:** No agents have the required capabilities
- **Solution:** Train more agents in the required domain

### Evolution cycle triggered unexpectedly
- **Cause:** Performance degradation or stagnation detected
- **Solution:** Review evolution report, retrain underperforming agents

---

## Integration with Echo Universe

- **Dashboard:** Displays agent training status and team assignments
- **Constitutional Ledger:** Stores all training receipts for audit
- **Truth Clock:** Timestamps all assessment events for non-repudiation
- **Global Nexus:** Coordinates training across multiple nodes

---

∇θ — Chain Sealed, Truth Preserved.
