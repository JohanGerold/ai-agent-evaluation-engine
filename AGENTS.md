# Project Rules - AI Agent Evaluation and Reliability Engine (AAP)

The following rules are mandatory and govern all work within this workspace:

## 1. Product Status and Claims
- **Do not** describe the current product as "enterprise-grade" or "production-ready".
- The correct status is: **production-oriented architecture / production-capable design, NOT IMPLEMENTED and NOT PRODUCTION-READY**.
- Production claims require passing the formal release gates specified in `docs/PRODUCTION_READINESS_CHECKLIST.md`.

## 2. Implementation Plan and Task Ordering
- Revision 2 retains T-001–T-045 historical/top-level numbering, but because several tasks were split, there are **62 executable dependency-ordered task rows**.
- Always follow the actual task rows and dependencies in `docs/IMPLEMENTATION_PLAN.md`.
- **Do not** infer implementation order merely from task numbers.

## 3. Architecture Approval and Decision Gate
- **T-001** is the architecture and product approval task.
- Decisions **D-01 through D-13** are resolved and recorded as part of T-001 according to their decision deadlines in `docs/PROJECT_BRIEF.md`.
- Application implementation starts with **T-002 only after T-001 is explicitly approved**.

## 4. Worker Execution Terminology
- **Do not** simplify worker execution terminology (e.g., casual references like "process/thread").
- Adhere strictly to the exact process, heartbeat, fencing, lease, and concurrency contracts defined in `docs/EXECUTION_MODEL.md`.

## 5. Specification and Design Intent vs. Verified Evidence
- Everything in `docs/` describing security, reliability, capacity, or recovery is currently **specification and design intent**.
- **Do not** state or imply that a control works until its required test and release evidence exists.

## 6. Scope of `creation/` Prototype
- `creation/` is a visual and design prototype.
- It is not production application code and does not override any architecture specifications in `docs/`.

## 7. Architecture Integrity During Implementation
- **Do not** modify architecture decisions while implementing a task.
- If an implementation detail conflicts with an architecture document: **STOP, identify the conflict, and ask the user for a decision**.

## 8. Single-Task Implementation Discipline
- Implement **one** `IMPLEMENTATION_PLAN` task at a time.
- For every task:
  1. Read its dependencies.
  2. Read its referenced acceptance criteria (in `docs/REQUIREMENTS.md`).
  3. Read relevant architecture contracts across `docs/`.
  4. Implement only that specific task.
  5. Run its required tests.
  6. Report files changed and test evidence.
  7. **Stop before proceeding to the next task**.
