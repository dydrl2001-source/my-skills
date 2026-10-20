# Turn a short request into a small, concrete change

Read project instructions and the relevant code before asking the user to repeat context. Look for the current screen or entry point, established names, reusable components, existing service functions and adjacent checks.

Write only the detail needed for the task:

- **Requested behavior:** what the user can do after the change, including explicit constraints.
- **Existing path:** the component, service or command already responsible for related behavior. Name only files actually found.
- **Completion:** a few observable outcomes, including a meaningful failure case where appropriate.
- **Open decision:** ask only if an unresolved behavior, permission or scope materially blocks progress. For optional details, state a reasonable assumption.

An already-authenticated application's new registration button should normally reuse the existing registration service and button states. It does not imply building a new authentication system, choosing a new stack or adding a generic service layer. Trace current behavior first.

Respect output scope: a request for a reusable prompt produces a self-contained prompt; a planning request produces a plan; an authorized implementation proceeds through the existing development workflow. Do not add a second brainstorming/TDD/review process or a compulsory confirmation step. Use Claude, Codex, Cursor or subagents only when the active task and available tools justify them; this checklist does not require another CLI or account.

Adapted as newly written guidance from the project-reading and request-structuring ideas in the legacy `prompt-enhancer` and `meta-prompt-generator` resources in this repository. Their fixed paths, model choices, blanket approval gates and mandatory agent counts are not imported.
