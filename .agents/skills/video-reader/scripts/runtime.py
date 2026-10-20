"""Shared, dependency-free runtime paths for Windows, Linux and macOS."""
import os
from pathlib import Path


def runtime_root(platform=None):
    platform = platform or os.name
    override = os.environ.get('VIDEO_READER_HOME')
    if override:
        return Path(override).expanduser().resolve()
    if platform == 'nt':
        base = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData/Local')
    else:
        base = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache')
    return base.expanduser().resolve() / 'CodexVideoReader'


def venv_python(root=None, platform=None):
    platform = platform or os.name
    return (root or runtime_root(platform)) / ('venv/Scripts/python.exe' if platform == 'nt' else 'venv/bin/python')
