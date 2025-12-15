# ECP Architecture

The Echo Coordination Protocol (ECP) is built upon a layered architecture designed to ensure transparency, auditability, and human oversight. This "physics-first" model separates the recording of objective events from their subjective interpretation, creating a robust framework for multi-agent coordination.

## Architectural Layers

| Layer                 | Directory             | Purpose                                                                                                     |
| --------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------- |
| 1. Event Layer        | `events/`             | Captures the immutable, factual ground truth of what occurred.                                              |
| 2. Classification Layer | `classifications/`    | Allows multiple AIs to provide their independent ethical assessments of an event.                           |
| 3. Consensus Layer    | `consensus/`          | Quantifies the degree of disagreement (divergence) between AI classifications without forcing a resolution. |
| 4. Case Layer         | `cases/`              | Tracks events that require governance and escalates them based on divergence scores or ethical flags.       |
| 5. Ruling Layer       | `rulings/`            | Enables authorized humans to make final judgments on escalated cases and establish binding precedents.      |
| 6. Governance Layer   | `ethics/`, `config/`  | Defines the core ethical principles, operational policies, and configurable parameters of the system.       |

## Data Flow

1.  An **Event** is recorded in the `events/` directory.
2.  Each AI agent creates a **Classification** in the `classifications/` directory.
3.  A **Consensus** score is calculated and stored in the `consensus/` directory.
4.  If the divergence is high, a **Case** is created in the `cases/` directory.
5.  A human provides a **Ruling**, which is stored in the `rulings/` directory.
6.  The ruling may create a **Precedent** that influences future classifications.
