# ECP Governance Model

The governance model of the Echo Coordination Protocol (ECP) is designed to be human-centric, ensuring that while AI agents can operate autonomously, final authority and ethical judgment remain with human overseers.

## Human-in-the-Loop

The core of the ECP governance model is the "human-in-the-loop" principle. This is enacted through the **Ruling Layer**, where authorized human users can:

*   **Resolve Disputes**: When AI agents have a high degree of disagreement (high divergence score), the system automatically escalates the case for human review.
*   **Set Precedents**: A human ruling can be designated as a precedent, which will then inform and guide future AI classifications in similar situations.
*   **Provide Final Authority**: Humans have the ultimate say in any ethical dilemma that the system cannot resolve on its own.

## Escalation Process

1.  **Automatic Detection**: The system continuously monitors the divergence scores of all classified events.
2.  **Threshold-Based Escalation**: If the divergence score exceeds the threshold defined in `policy.json` (e.g., > 0.4), or if any agent classifies an event as "unethical," the case is automatically flagged for human review.
3.  **Notification**: The system creates a GitHub issue, sends notifications (as configured), and logs the escalation event.

## Precedent System

*   **Creation**: Precedents are created from human rulings.
*   **Application**: AI agents are required to consider active precedents when classifying new events.
*   **Scope**: Precedents are scoped to specific event types and have an expiration date, ensuring that the governance model can evolve over time.
