# Upstream source

- Repository: https://github.com/Birkenpapier/ai-app-cloner
- Commit: `3a6d932d519773612cf79289c3102082bb76bb41`
- Imported: 2026-11-27.
- License: MIT; the original upstream `LICENSE` is included unchanged.

## Imported files

- `skills/clone-app/SKILL.md` → `SKILL.md` (upstream blob `3d977fc0f321cd9cb48ddc2e79ea60ef20b7046d`)
- `LICENSE` → `LICENSE` (upstream blob `89d6e346a4785eb9a39a53eeb5ee4e57bf98c0f0`)

## Local adaptation

- Reduced metadata to name and description, with Korean request triggers.
- Added portable startup guidance and a pinned full-template setup reference. Project paths remain relative to a separate Expo workspace; the skill repository is not the application.
- Kept the upstream app reconstruction workflow and its component specification template.
- No upstream runtime source or dependencies are bundled or executed.

The pinned commit identifies the imported source. Any later upstream update requires reviewing the skill and its bundled references together. GitHub registration, local skill installation, dependency setup, and application execution are separate operations.
