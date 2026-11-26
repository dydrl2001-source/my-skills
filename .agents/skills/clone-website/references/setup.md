# Separate website project setup

Read this when there is no existing web application to edit. The bundled skill and its two inspection references can work with a compatible existing project, but do not provide an executable website by themselves.

## Pinned template

- Repository: https://github.com/JCodesMore/ai-website-cloner-template
- Commit: `14085f8ba2a15b5e7f509c78dfc4017dbbfced6d`
- Upstream release at import: `v0.6.2`
- Runtime prerequisite: Node.js 24+ and npm.
- Framework: Next.js 16, React 19, TypeScript, Tailwind CSS 4.

## Existing project

Read its instructions, package scripts, routes, and existing source. Follow that project's framework and verification command. Keep unrelated routes and assets. The upstream template is optional when a suitable project already exists.

Never create the website in `my-skills`, the installed skill directory, or a plugin cache. Choose a separate task-specific folder when starting from nothing.

## New project preparation

Run from the chosen parent directory outside the skill repository. Replace `website-clone-project` with a task-specific unused name.

```bash
git clone https://github.com/JCodesMore/ai-website-cloner-template.git website-clone-project
cd website-clone-project
git switch -c work/website-clone 14085f8ba2a15b5e7f509c78dfc4017dbbfced6d
npm ci
npm run check
npm run dev
```

These are setup instructions for the app-building task; importing the skill does not run them. Inspect any installation or build failure before continuing. Keep the source remote for provenance and use the user's selected destination if publishing is later requested.

## Use and completion

Use the installed `clone-website` skill with the web project as the working directory and the user's target URL(s). If a host has no slash-command support, invoke it by name in the request. The host needs browser access for source inspection and local comparison.

In this template, `npm run check` runs lint, type-check, and production build. A build is only one part of completion: verify the rendered pages and the observed interactions as required by the skill. Saving the skill in GitHub does not deploy or start a website.
