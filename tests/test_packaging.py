import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/build_plugin.py'
spec = importlib.util.spec_from_file_location('build_plugin', SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackagingTests(unittest.TestCase):
    def test_archive_uses_portable_layout_and_omits_python_caches(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / 'plugin.zip'
            builder.build(archive)
            with zipfile.ZipFile(archive) as plugin:
                names = plugin.namelist()
                self.assertIn('plugin.json', names)
                self.assertIn('skills/video-reader/scripts/runtime.py', names)
                self.assertFalse(any('__pycache__' in name or name.startswith('.agents/') for name in names))

    def test_integrated_package_has_five_canonical_skills_and_font_license(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / 'plugin.zip'
            builder.build(archive)
            with zipfile.ZipFile(archive) as plugin:
                names = plugin.namelist()
                skills = {n.split('/')[1] for n in names if n.endswith('/SKILL.md')}
                self.assertEqual(skills, {'diagram-design', 'engineering-upgrades', 'video-reader', 'web-design', 'card-news'})
                self.assertIn('skills/card-news/assets/fonts/OFL.txt', names)
                self.assertIn('skills/card-news/assets/fonts/NanumGothic-Regular.ttf', names)
                self.assertNotIn('skills/codex/skill.md', names)
                root = json.loads(plugin.read('plugin.json'))
                compat = json.loads(plugin.read('.codex-plugin/plugin.json'))
                self.assertEqual(root['name'], compat['name'])
                self.assertEqual(root['version'], compat['version'])
                self.assertEqual(root['extensions']['com.openai']['interface'], compat['interface'])

    def test_ignored_private_files_cannot_silently_enter_archive(self):
        for private in ('cookies.txt', '.env.local', 'source.mp4', 'models/weights.bin',
                        'output/transcript.txt', 'outputs/report.md', 'transcript.json'):
            with self.subTest(private=private), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                skills = root / 'skills'
                for name in ('diagram-design', 'engineering-upgrades', 'video-reader', 'web-design', 'card-news'):
                    (skills / name).mkdir(parents=True)
                    (skills / name / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Fixture skill.\n---\n')
                font_dir = skills / 'card-news/assets/fonts'
                font_dir.mkdir(parents=True)
                (font_dir / 'NanumGothic-Regular.ttf').write_bytes(b'Packaging fixture')
                (font_dir / 'OFL.txt').write_text('Packaging fixture license')
                with patch.object(builder, 'SKILLS', skills):
                    builder.build(root / 'valid-baseline.zip')
                forbidden = skills / 'video-reader' / private
                forbidden.parent.mkdir(parents=True, exist_ok=True)
                forbidden.write_text('test fixture')
                with patch.object(builder, 'SKILLS', skills), self.assertRaisesRegex(ValueError, 'Private media'):
                    builder.build(root / 'archive.zip')
                self.assertFalse((root / 'archive.zip').exists())


if __name__ == '__main__':
    unittest.main()
