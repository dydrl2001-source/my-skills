# Choosing design sources

Read this when the user names a brand, Apple-style interaction, OpenDesign, or Vercel UI review.

| Request | Source and use |
| --- | --- |
| Brand such as Linear, Stripe or Notion | Prefer the user's actual design system. For OpenDesign, inspect the selected package's DESIGN.md, manifest.json and tokens.css in https://github.com/nexu-io/open-design/tree/main/design-systems ; confirm the exact slug in the catalog rather than deriving it from the brand name. |
| Apple-style drag, swipe or sheet | Read the bundled apple-design skill at ../../apple-design/SKILL.md. Preserve the selected visual brand; Apple motion does not require replacing colors or typography. |
| General UI polish and motion | Use the bundled emil-design-eng skill at ../../emil-design-eng/SKILL.md where useful. |
| Requested Vercel UI/accessibility or pre-release audit | Read ../../web-design-guidelines/SKILL.md and retrieve the current rules. |

OpenDesign is an independent application with a design-system catalog, skills and optional MCP integration. A reference link does not install its application, connect MCP, bundle its 151 systems or give this plugin access to a running instance. Use available repository access to retrieve the selected package. If the user requests installation or integration, inspect current official setup documentation and the existing environment first.

OpenDesign's catalog describes community/upstream-derived and project-owned packages. A brand-named package is not proof of that brand's official endorsement or exact internal tokens. Record source, revision when available, and whether values are verified, adapted or inferred. Preserve individual asset and package licenses; do not bulk-import the catalog merely to use one style.

Translate the selected contract into project tokens and real component states. Verify Korean text, keyboard access, contrast, mobile layout and reduced motion. Do not apply unrelated styles or run a full audit for a small content edit. No screenshot, source guide or star count proves a completed implementation.

