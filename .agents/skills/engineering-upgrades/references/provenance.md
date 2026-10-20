# Sources and integration choices

Derived from Matt Pocock's MIT-licensed skills at commit `5beb35b040e3de97e54fa9e386d7e42d15c295c2`, inspected on 2026-10-20:

- [Domain modeling](https://github.com/mattpocock/skills/tree/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/domain-modeling): glossary consistency, concrete semantic scenarios, sparse decision records.
- [Codebase design](https://github.com/mattpocock/skills/tree/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/codebase-design): small useful interfaces, hidden orchestration and tests through meaningful behavior.
- [Code review](https://github.com/mattpocock/skills/tree/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/code-review): separate requirements and project-standards conclusions.

This is a personal adaptation, not the upstream plugin. Existing Superpowers skills remain responsible for the overall development workflow. The adaptation omits duplicate TDD/debugging/implementation orchestration, mandatory tracker setup, mandatory extra reviewers and agent-wide English vocabulary rules. It preserves regression coverage during refactors and reuses existing authorization and artifacts.

The installed skill is a stable local copy. Upstream changes require review before a deliberate update; the managed Superpowers cache and global AGENTS.md are not modified.

Version 0.2.0 of the personal toolkit adds newly written request-brief guidance informed by `skills/prompt-enhancer` and `skills/meta-prompt-generator` in `dydrl2001-source/my-skills`. It retains project inspection and observable completion criteria, and omits their fixed host paths, mandatory confirmation rounds, model choices and agent counts. The original Matt Pocock MIT notice remains included.
