# Echo Universe Quick Reference
*Last updated: 2026-01-09T09:34:17.368641*

## Essential Commands

### Agent Operations
```bash
# Run Planner Agent (autopilot)
python3 agents/planner/planner_agent.py

# Run Cleaner Agent (autopilot)
python3 agents/cleaner/cleaner_agent.py

# Run Yellowpages Agent (autopilot)
python3 agents/yellowpages/yellowpages_agent.py

# Run agent once (testing)
python3 agents/planner/planner_agent.py --once
```

### Git Operations
```bash
# Pull latest changes
git pull origin main

# Push changes
git add .
git commit -m "Your message"
git push origin main

# Create branch
git checkout -b branch-name
git push origin branch-name

# Create pull request
gh pr create --title "Title" --body "Description"
```

### Repository Navigation
```bash
# Core directories
cd agents/          # Autonomous agents
cd planning/        # Plans and roadmaps
cd global-nexus/    # Enterprise strategy
cd docs/            # Documentation
cd ledgers/         # Constitutional Ledger

# View agent activity
cat ledgers/agent_activity/planner_001_*.jsonl
cat ledgers/agent_activity/cleaner_001_*.jsonl
cat ledgers/agent_activity/yellowpages_001_*.jsonl
```

## Key Files

### Strategic Documents
- `global-nexus/ECHO_UNIVERSE_TRANSFORMATION_STRATEGY.md` - Complete transformation strategy
- `global-nexus/72_HOUR_EXECUTION_PLAN.md` - Detailed execution plan
- `global-nexus/ENTERPRISE_PARTNERSHIP_STRATEGY.md` - Partnership strategy
- `global-nexus/PRESENTATION_SCRIPT.md` - Enterprise pitch script

### Planning Documents
- `planning/MASTER_ROADMAP.md` - Master project roadmap
- `planning/daily_plan_YYYY-MM-DD.md` - Daily work plans

### Agent State
- `agents/shared/state/planner_001.json` - Planner agent state
- `agents/shared/state/cleaner_001.json` - Cleaner agent state
- `agents/shared/state/yellowpages_001.json` - Yellowpages agent state

## Directory Structure

```
Echo/
├── agents/              # Autonomous agents
│   ├── planner/        # Planning agent
│   ├── cleaner/        # Cleaning agent
│   ├── yellowpages/    # Directory agent
│   └── shared/         # Shared utilities
├── global-nexus/       # Enterprise strategy
├── planning/           # Plans and roadmaps
├── ledgers/            # Constitutional Ledger
├── docs/               # Documentation
│   └── yellowpages/    # Digital directory
└── artifacts/          # Build artifacts
```

## Agent Schedules

- **Planner Agent:** Every 10 minutes
- **Cleaner Agent:** Every 15 minutes
- **Yellowpages Agent:** Every 20 minutes

## Emergency Procedures

### Stop All Agents
```bash
pkill -f "python3.*agent.py"
```

### View Agent Logs
```bash
tail -f ledgers/agent_activity/*.jsonl
```

### Reset Agent State
```bash
rm agents/shared/state/*.json
```

---

*This reference is automatically updated every 20 minutes by Yellowpages Agent*

∇θ — chain sealed, truth preserved.
