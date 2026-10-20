"""Package canonical repository skills into a portable plugin, without caches."""
import argparse
import json
import re
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents/skills'
EXCLUDED = {'__pycache__', '.git', '.venv', 'venv', 'node_modules'}
PRIVATE_DIRS = {'models', 'video-evidence', 'credentials', 'secrets', 'output', 'outputs'}
PRIVATE_SUFFIXES = {'.mp4', '.mov', '.webm', '.wav', '.mp3', '.pem', '.key'}
PRIVATE_NAMES = {'transcript.txt', 'transcript.json'}
EXPECTED_SKILLS = {'diagram-design', 'engineering-upgrades', 'video-reader', 'web-design', 'card-news'}


def build(output):
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Write the archive outside the source repository.')
    manifest = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('$schema') != 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json':
        raise ValueError('Unsupported portable plugin schema.')
    if len(manifest['extensions']['com.openai']['interface']['shortDescription']) > 30:
        raise ValueError('Plugin subtitle exceeds 30 characters.')
    entries = [(ROOT / 'plugin.json', 'plugin.json')]
    for path in sorted(SKILLS.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink cannot be packaged: {path}')
        relative = path.relative_to(SKILLS)
        if path.is_file() and not EXCLUDED.intersection(relative.parts) and path.suffix not in {'.pyc', '.pyo'}:
            if (PRIVATE_DIRS.intersection(part.lower() for part in relative.parts) or path.suffix.lower() in PRIVATE_SUFFIXES
                    or path.name.lower() in PRIVATE_NAMES or path.name.lower().startswith('.env') or 'cookies' in path.name.lower()):
                raise ValueError(f'Private media, cache or credential file cannot be packaged: {relative}')
            entries.append((path, 'skills/' + relative.as_posix()))
    expected = EXPECTED_SKILLS
    if {p.parent.name for p in SKILLS.glob('*/SKILL.md')} != expected:
        raise ValueError('Canonical skill set differs from the selected release.')
    for name in sorted(expected):
        entry = SKILLS / name / 'SKILL.md'
        text = entry.read_text(encoding='utf-8')
        match = re.search(r'^name:\s*([^\n]+)', text, re.MULTILINE)
        if not text.startswith('---\n') or not match or match.group(1).strip().strip('\"\'') != name:
            raise ValueError(f'Skill name must match its folder: {name}')
    for asset in ('assets/fonts/NanumGothic-Regular.ttf', 'assets/fonts/OFL.txt'):
        if not (SKILLS / 'card-news' / asset).is_file():
            raise ValueError(f'Missing bundled font or license: {asset}')
    compat = {key: manifest[key] for key in ('name', 'version', 'description', 'author') if key in manifest}
    compat['interface'] = manifest['extensions']['com.openai']['interface']
    compat['skills'] = './skills'
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for source, destination in entries:
            archive.write(source, destination)
        archive.writestr('.codex-plugin/plugin.json', json.dumps(compat, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed.')
        if {name.split('/')[1] for name in archive.namelist() if name.endswith('/SKILL.md')} != expected:
            raise ValueError('Archive skill discovery differs from selected skills.')
    return {'archive': str(output), 'files': len(entries) + 1, 'bytes': output.stat().st_size, 'skills': sorted(expected)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(json.dumps(build(parser.parse_args().output), ensure_ascii=False))
