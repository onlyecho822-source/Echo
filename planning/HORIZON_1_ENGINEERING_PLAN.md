# Horizon 1 Engineering Plan: The Core System

**Plan Created:** December 20, 2025 at 16:48 EST
**Planning Horizon:** 4-6 Weeks (January 2026 - February 2026)
**Status:** Ready for Execution

---

**Objective: Transform the Feedback OS prototype into a fully functional, 8-agent Sovereign Operating System with a web UI and working Zapier integration.

**Timeline:** 4-6 Weeks
**Resources:** 1-2 Backend Engineers, 1 Frontend Engineer

---

## 1. Project 1: Fix Zapier Integration (Estimated Time: 1-2 Days)

**Objective:** Re-authenticate the Zapier MCP connection and prove it works with a simple end-to-end test.

| Task | Description | Estimated Time | Owner |
| :--- | :--- | :--- | :--- |
| **1.1 Re-authenticate Zapier** | Go through the OAuth flow again to re-establish the connection. | 1-2 hours | You |
| **1.2 Create Test Zap** | Create a simple Zap that triggers on a webhook and sends a Gmail alert. | 2-4 hours | You |
| **1.3 Create Test Script** | Write a Python script that sends a POST request to the Zapier webhook. | 2-4 hours | Me |
| **1.4 End-to-End Test** | Run the script and verify that the Gmail alert is received. | 1 hour | You + Me |

**Success Criteria:** A new entry in the Feedback OS triggers a Zap that successfully sends a notification email.

---

## 2. Project 2: Build the Sovereign Operating System v3.0 (Estimated Time: 3-5 Weeks)

**Objective:** Evolve the `feedback_minimal.py` prototype into the full 8-agent system with the hybrid datastore and a web UI.

### **Week 1: The Foundation**

| Task | Description | Estimated Time | Owner |
| :--- | :--- | :--- | :--- |
| **2.1 Set Up Project Structure** | Create the new project directory with subdirectories for agents, core, api, web. | 4 hours | Me |
| **2.2 Implement Hybrid Datastore** | Create the SQLite database schema. Implement the append-only hash chain with the Echo Agent. | 2-3 days | Backend Engineer |
| **2.3 Implement Agent Orchestrator** | Build the deterministic sequencer that will manage the agent swarm. | 2-3 days | Backend Engineer |

### **Week 2-3: The Agent Swarm**

| Task | Description | Estimated Time | Owner |
| :--- | :--- | :--- | :--- |
| **2.4 Implement 8 Core Agents** | Develop the 8 core agents (Kernel, Manus, Echo, DeepSeek, Gemini, Mirror, Experiment, Audit) as separate Python classes with explicit contracts. | 1-2 weeks | Backend Engineer |
| **2.5 Integrate Agents with Orchestrator** | Connect the agents to the orchestrator and ensure they communicate correctly. | 2-3 days | Backend Engineer |
| **2.6 Unit & Integration Tests** | Write unit tests for each agent and integration tests for the full swarm. | 3-4 days | Backend Engineer |

### **Week 4-5: The User Interface**

| Task | Description | Estimated Time | Owner |
| :--- | :--- | :--- | :--- |
| **2.7 Build FastAPI Backend** | Create the API endpoints for the web UI to communicate with the agent swarm. | 3-4 days | Backend Engineer |
| **2.8 Develop Web UI** | Build the frontend with HTML, CSS, and JavaScript for daily check-ins, pattern viewing, and experiment management. | 1-2 weeks | Frontend Engineer |
| **2.9 Connect Frontend to Backend** | Wire the web UI to the FastAPI backend. | 2-3 days | Frontend Engineer |

**Success Criteria:**
- The 8-agent system is fully functional and passes all tests.
- The hybrid datastore correctly saves data to SQLite and the hash chain.
- The web UI allows users to perform daily check-ins and view their data.
- The system is deployed to a staging environment.

---

## 3. Required Resources

### **Personnel:**
- **1-2 Backend Engineers:** Strong Python skills, experience with SQLite, FastAPI, and microservices.
- **1 Frontend Engineer:** Strong HTML, CSS, and JavaScript skills. Experience with a modern framework (React, Vue, etc.) is a plus.
- **You (Project Manager/Visionary):** Guide the vision, make key decisions, and test the product.
- **Me (AI Assistant):** Provide code, documentation, and strategic support.

### **Technology:**
- **Python 3.11+**
- **SQLite**
- **FastAPI**
- **HTML/CSS/JavaScript**
- **Git/GitHub**
- **A cloud provider** for staging and production deployment (AWS, GCP, Azure, etc.)

---

## 4. Key Technical Specifications

### **Agent Contracts:**
Each agent will have a clearly defined input/output schema. For example:

**DeepSeek Agent Input:**
```json
{
  "user_id": "user-123",
  "date_range": ["2025-12-01", "2025-12-20"],
  "analysis_type": "correlation"
}
```

**DeepSeek Agent Output:**
```json
{
  "pattern_id": "p-456",
  "correlation": {
    "input": "first_input.phone",
    "output": "energy.low",
    "strength": 0.72,
    "p_value": 0.03
  }
}
```

### **Hybrid Datastore Schema:**
- **SQLite:** A relational schema with tables for `users`, `checkins`, `experiments`, `rules`, etc.
- **Hash Chain:** A simple append-only log file (`truth.log`) where each line is a JSON object containing `timestamp`, `table`, `row_id`, `hash`, and `previous_hash`.

### **API Endpoints:**
- `POST /checkin/morning`
- `POST /checkin/evening`
- `GET /patterns`
- `GET /experiments`
- `POST /experiments`

---

## 5. Conclusion

This plan is ambitious but achievable. By focusing on building out the working prototype and fixing the Zapier integration, we can make significant progress in the next 4-6 weeks. This will give us a solid foundation to build upon in Horizon 2 and beyond.

The key is to **start building now** and to **focus on what works**. We have the vision, we have the architecture, and now we have the plan. Let's execute.
