# Personal agent skills

The user designated `https://github.com/dydrl2001-source/my-skills` as the canonical home for future custom skills. Update the source here when asked to customize these skills, then verify the relevant behavior. Follow [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md) for distribution. Existing `skills/` and `.claude/` resources are separate legacy collections; preserve their files and do not automatically activate or publish all of them with the personal plugin.

This repository contains reusable skills in `.agents/skills/`:
- `diagram-design`: diagrams and visual explanations.
- `engineering-upgrades`: domain language, module boundaries and code review checks.
- `video-reader`: timestamped video frames and local speech transcription.

Read the relevant skill's SKILL.md before use. Supporting resources live in that skill's directory. Explain results in the user's language. Existing authorization and task scope take precedence over optional setup prompts in imported guidance.

For video runtime setup use Python 3.10–3.13 (3.12 recommended):
`python3 .agents/skills/video-reader/scripts/setup.py`
Then run `python3 .agents/skills/video-reader/scripts/run.py doctor`.
Setup needs PyPI network access. Online video retrieval and first speech model download need network access during execution or preloading. Do not claim videos were watched without reviewing generated frames and transcript status. Hosts without shell/Python cannot execute the video pipeline.

Run tests with the video runtime interpreter: `python -m unittest discover -s tests -v`.
Build the portable plugin archive: `python scripts/build_plugin.py --output <outside-repo-path.zip>`.
Never commit private media, cookies, credentials, model caches or runtime environments.
