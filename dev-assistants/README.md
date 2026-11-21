# dev-assistants/

AI development assistants (concept C12) — **tool-agnostic**: one or more assistants, including any provider-offered agents and skills, may be used.

## Operating rules (draft for task DEV-02)
- Assistants run with **restricted permissions**.
- Creating cloud resources requires **explicit human confirmation**.
- Generated code passes review and tests before it is merged.
- Assistants **never take part in runtime emergency decisions**; the rescue orchestrator is a separate, auditable system.
- Assisted work is logged as it happens (task, outcome, reviewed diff, test result) as evidence.

Skill and workflow definitions live in [`skills/`](skills/README.md).
