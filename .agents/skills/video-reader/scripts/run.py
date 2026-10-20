"""Launch the skill in its isolated runtime; forward arguments unchanged."""
import os
from pathlib import Path
import subprocess
import sys
from runtime import runtime_root, venv_python


def main():
    root = runtime_root()
    python = venv_python(root)
    if not python.is_file():
        print('Video Reader runtime is missing. Run Python 3.10-3.13 with scripts/setup.py first.', file=sys.stderr)
        return 2
    env = dict(os.environ, VIDEO_READER_HOME=str(root))
    return subprocess.call([str(python), str(Path(__file__).with_name('video_reader.py')), *sys.argv[1:]], env=env)


if __name__ == '__main__':
    raise SystemExit(main())
