# Separate Expo project setup

Read this before invoking `clone-app` in a blank workspace or one without the required Expo scaffold. This package contains the skill, not the runnable app template. Keep the skill source in `my-skills`; create and edit the app elsewhere.

## Pinned source

- Repository: https://github.com/Birkenpapier/ai-app-cloner
- Commit: `3a6d932d519773612cf79289c3102082bb76bb41`
- Upstream release at import: `v2.0.0`
- Stack at that commit: Expo SDK 56, Expo Router 56, React Native 0.85, React 19.2, NativeWind 4.
- Use a Node.js/npm environment compatible with the pinned packages. Review the exact Expo SDK 56 documentation and the package/lockfile requirements rather than substituting an older Expo scaffold.

## Existing project inspection

Confirm the project's package metadata, then check these project-relative paths:

- `package.json`, `package-lock.json`, `app.json`, `babel.config.js`, `metro.config.js`, `tsconfig.json`, `tailwind.config.js`.
- `src/app/_layout.tsx`, `src/global.css`, `src/lib/tokens.ts`, `src/lib/store.ts`.
- `docs/research/app-spec.schema.json`, `docs/research/app-spec.example.json`, `docs/screenshots/README.md`.
- `e2e/verify.mjs`, `e2e/flows.mjs`.
- For the optional local backend mode: `scripts/gen-backend.mjs` and the complete `src/backend/` tree.

Read the project's `AGENTS.md`. Reuse a compatible existing project without overwriting its source, branch, or settings. If it is a different framework, prepare a new app folder rather than copying isolated helper files into it.

## New project preparation

Run these commands from the selected parent directory **outside the skill repository**. Replace `mobile-clone-project` with a task-specific unused directory name. Do not rerun the clone into an existing folder.

```bash
git clone https://github.com/Birkenpapier/ai-app-cloner.git mobile-clone-project
cd mobile-clone-project
git switch -c work/mobile-clone 3a6d932d519773612cf79289c3102082bb76bb41
npm ci
npx playwright install chromium
npx tsc --noEmit
npm run web
```

Dependency installation and browser installation are execution steps, not effects of saving this skill. Carry them out only in the actual app-building task with the available runtime and network access. Keep the upstream remote as source provenance; use the user's chosen destination if they later ask to publish their app.

## Input and verification

Place reference screenshots in the app project's `docs/screenshots/`, or use the user-specified input folder. Connect an available supported browser automation tool for the render/screenshot/compare loop. Run the installed `clone-app` skill with the **app project** as the working directory.

After implementing screens, update `e2e/flows.mjs` for the actual routes and interactions, then run:

```bash
npx tsc --noEmit
npm run verify
```

`npm run verify` exports the Expo web build and runs `e2e/verify.mjs`. If local data-model generation is requested, use `npm run gen:backend` after preparing `docs/research/app-spec.json`; this mode remains on-device and offline. Server authentication and synchronization need a separate implementation.

Do not describe a saved skill, a downloaded template, or a passing type-check as a running or visually verified app. Report the actual preparation and execution status.
