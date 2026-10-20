# Requirements and standards review

Use the active task's existing review process. Give a reviewer the same concrete change scope, requirements and project standards. If a base revision already exists, reuse it and verify the selected diff includes the actual changes being reviewed; committed, staged and unstaged changes are distinct. For a non-Git artifact, identify the files or before/after snapshots directly.

Establish two independent conclusions:

- **Requirements**: Which requested behaviors are implemented, missing, wrong, or outside scope? Connect each material finding to the requirement, concrete code location and a trigger/consequence. Code can follow every convention and still implement the wrong behavior.
- **Project standards**: Does the change follow the repository's actual rules and constraints? Cite the relevant standard for hard violations. Naming, duplication, pass-through layers and speculative abstractions are design observations with a practical consequence, not universal hard errors. Do not mistake personal preference for a project rule.

Use available tests and inspection as evidence. A passing syntax check does not prove error handling; a missing-file test does not prove valid-file or malformed-file behavior. If no requirement or standard is documented, use the user request and inspected code where sufficient, and mark the remaining uncertainty. Do not invent a spec, tracker requirement or rule, and do not block a useful review just to create those artifacts.

Report the result at the task's scale, for example:

```text
Requirements: [finding or supported conclusion, with evidence]
Project standards: [finding or supported conclusion, with evidence]
Verification: [what ran, what it establishes, what remains unverified]
```

Combine the dimensions in one concise response when there are few findings, while keeping their conclusions distinguishable. Prioritize concrete behavior and scope failures. Review execution, delegation, fixes and final verification remain governed by the existing workflow and user authorization.
