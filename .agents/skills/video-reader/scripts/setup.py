"""Install a private runtime using this interpreter, without changing the OS."""
import os
from pathlib import Path
import subprocess
import sys
from runtime import runtime_root, venv_python


def main():
    if not (3, 10) <= sys.version_info[:2] < (3, 14):
        print('Use Python 3.10 through 3.13 (3.12 recommended).', file=sys.stderr)
        return 2
    root = runtime_root()
    python = venv_python(root)
    env = dict(os.environ, VIDEO_READER_HOME=str(root))
    try:
        if not python.is_file():
            subprocess.run([sys.executable, '-m', 'venv', str(root / 'venv')], check=True, env=env)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(Path(__file__).resolve().parents[1] / 'requirements.txt')], check=True, env=env)
        subprocess.run([str(python), str(Path(__file__).with_name('video_reader.py')), 'doctor'], check=True, env=env)
    except subprocess.CalledProcessError as error:
        print(f'Runtime setup failed (exit {error.returncode}). Check the command output above.', file=sys.stderr)
        return error.returncode or 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
