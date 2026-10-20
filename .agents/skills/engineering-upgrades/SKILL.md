---
name: engineering-upgrades
description: Use when a coding task involves ambiguous project terminology, a cumbersome module interface, or code review against both requirements and project standards. Adds domain modeling, interface design, and evidence-based review checks to the existing development workflow.
---

# Engineering Upgrades

Supplement the current engineering stage with the relevant check below. Keep the existing workflow for planning, TDD, debugging and verification; when Superpowers is available, use its corresponding skills. This skill adds checks inside those stages, not a second implementation process. Existing user authorization and project instructions continue to apply.

Read only the matching reference:

| Current task | Additional check |
|---|---|
| Requirements or names have conflicting business meanings | [Domain language](references/domain-language.md): check existing terminology against code; record resolved concepts sparingly. |
| Callers coordinate too many steps, or a refactor needs a clear interface | [Module design](references/module-design.md): hide orchestration behind a small interface and test observable behavior. |
| Reviewing a change or preparing completion evidence | [Review](references/review.md): assess requirements and documented standards separately, using the same concrete change scope. |

Use the user's language for explanations and the repository's established names in code. Read existing artifacts before asking the user to repeat information. Ask a focused question only when an unresolved meaning affects behavior or scope; otherwise proceed using the existing agreement.

Documentation follows the work: reuse established locations and create a glossary entry or decision record only when there is a concrete resolved concept or durable decision to preserve. A cosmetic edit does not need domain documents or a new architecture exercise.

For reviews, extend the existing reviewer brief with both check dimensions. Use available review tools or agents according to the active workflow and authorization; the two dimensions do not require two additional reviewers. Report actual findings and verification limits concisely.

Adapted from selected Matt Pocock skills; see [provenance](references/provenance.md) and [LICENSE](LICENSE).
