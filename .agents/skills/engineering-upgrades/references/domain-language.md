# Domain language during requirements and design

Read the relevant existing `GLOSSARY.md`, domain documentation and representative code. If a `GLOSSARY-MAP.md` exists, follow it into the current context. Existing repository structure takes priority over a new convention.

When a term changes the requested behavior, distinguish the concepts before designing a change. For example, an event registration can be cancelled without refunding its payment or deleting the member's account. Verify which entity and state the user means against the current schema or behavior. Surface material conflicts; do not silently choose a new domain rule.

When a meaning has been resolved and will recur across the project, record one concise definition in the existing glossary. If none exists, create a root `GLOSSARY.md` only when a resolved project-specific concept merits it. Keep implementation details and generic programming vocabulary out. Preserve externally visible names and contracts unless a rename is within the authorized task.

Suggested entry:

```markdown
**Registration / 행사 신청**: One member's application to one event.
Cancellation changes the application state; payment refund is a separate operation.
```

Use a concrete edge case when it helps settle an important ambiguity. Do not turn every ordinary word into a terminology interview.

Record an architectural decision only when it is costly to reverse, surprising without context, and the outcome of a real trade-off. Prefer an existing decision-log location; otherwise a brief `docs/adr/NNNN-slug.md` entry can state the context, decision and reason. Reversible implementation choices remain in normal task notes.
