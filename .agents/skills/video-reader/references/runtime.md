# Runtime and outputs

`scripts/run.py` selects an isolated runtime on Windows, Linux or macOS. Windows uses `%LOCALAPPDATA%/CodexVideoReader/venv/Scripts/python.exe`; Unix uses `${XDG_CACHE_HOME:-~/.cache}/CodexVideoReader/venv/bin/python`. `VIDEO_READER_HOME` overrides the runtime root. Dependencies and model cache remain outside the skill so installing a skill update preserves them. The PowerShell wrappers remain available on Windows.

If `doctor` reports missing dependencies, use the bundled setup with an available Python 3.10–3.13 executable (3.12 recommended). Locate an existing compatible interpreter before installing Python. Codex's workspace dependency tool can supply its bundled Python path.

```sh
python3 '<skill-dir>/scripts/setup.py'
python3 '<skill-dir>/scripts/run.py' doctor
```

On Windows, replace `python3` with the full compatible Python executable or use `setup.ps1 -PythonPath '<compatible-python.exe>'` and `run.ps1`. Never install dependencies into a host's system interpreter. Python's `venv` module and network access to PyPI are needed for setup. Model downloads require Hugging Face access; URL acquisition requires access to the video host. A sandbox without network can still inspect an available local video using `--no-transcribe` after dependencies have been installed. Preload the selected speech model during environment setup when later task networking is disabled. A chat without Python/shell/image tools cannot execute the video pipeline; explain the actual missing capability without claiming the video was viewed.

Setup creates an isolated virtual environment and installs `requirements.txt`. Local transcription downloads faster-whisper model weights from Hugging Face on first use; subsequent use reuses the local cache. The `small` model favors useful multilingual transcription over minimal download size; `--model base` and `--model tiny` trade accuracy for smaller models. CPU speed depends on the computer. No external audio transcription API is used.

Default limits: one video, 20 minutes, 500 MiB, 150-second acquisition timeout, 600-second transcription timeout, 48 sampled frames. Maximum explicit frames: 120. These limits are configurable in CLI help; do not silently truncate the requested video. The script rejects live streams and playlists. Downloaded media can be retained in the evidence folder for closer inspection; local source files are used in place and never modified.

Outputs: `manifest.json`, `report.md`, `frames/*.jpg`, `contact-sheet-*.jpg`, plus `audio.wav`, `transcript.json` and `transcript.txt` when applicable. URL runs also retain `source.<ext>`. A failed run writes `failure.json`. Existing output directories are rejected rather than overwritten. Stdout is JSON; progress is on stderr. `partial` is a usable result with an explicit failed transcription, not proof of successful audio analysis.

The manifest stores the input URL, publisher description and local evidence paths. These are local artifacts. Cookie files, browser sessions and signed media download URLs are not included in the manifest.
