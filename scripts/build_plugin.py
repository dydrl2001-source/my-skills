"""Package canonical repository skills into a portable plugin, without caches."""
import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents/skills'
EXCLUDED = {'__pycache__', '.git', '.venv', 'venv', 'node_modules'}
PRIVATE_DIRS = {'models', 'video-evidence', 'credentials', 'secrets'}
PRIVATE_SUFFIXES = {'.mp4', '.mov', '.webm', '.wav', '.mp3', '.pem', '.key'}


def build(output):
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Write the archive outside the source repository.')
    manifest = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))
    assert manifest['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
    assert len(manifest['extensions']['com.openai']['interface']['shortDescription']) <= 30
    entries = [(ROOT / 'plugin.json', 'plugin.json')]
    for path in sorted(SKILLS.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink cannot be packaged: {path}')
        relative = path.relative_to(SKILLS)
        if path.is_file() and not EXCLUDED.intersection(relative.parts) and path.suffix not in {'.pyc', '.pyo'}:
            if (PRIVATE_DIRS.intersection(relative.parts) or path.suffix.lower() in PRIVATE_SUFFIXES
                    or path.name.lower().startswith('.env') or 'cookies' in path.name.lower()):
                raise ValueError(f'Private media, cache or credential file cannot be packaged: {relative}')
            entries.append((path, 'skills/' + relative.as_posix()))
    expected = {'diagram-design', 'engineering-upgrades', 'video-reader'}
    assert {p.parent.name for p in SKILLS.glob('*/SKILL.md')} == expected
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for source, destination in entries:
            archive.write(source, destination)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert {name.split('/')[1] for name in archive.namelist() if name.endswith('/SKILL.md')} == expected
    return {'archive': str(output), 'files': len(entries), 'bytes': output.stat().st_size, 'skills': sorted(expected)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(json.dumps(build(parser.parse_args().output), ensure_ascii=False))
