import importlib.util
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

    def test_ignored_private_files_cannot_silently_enter_archive(self):
        for private in ('cookies.txt', '.env.local', 'source.mp4', 'models/weights.bin'):
            with self.subTest(private=private), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                skills = root / 'skills'
                for name in ('diagram-design', 'engineering-upgrades', 'video-reader'):
                    (skills / name).mkdir(parents=True)
                    (skills / name / 'SKILL.md').write_text('skill')
                forbidden = skills / 'video-reader' / private
                forbidden.parent.mkdir(parents=True, exist_ok=True)
                forbidden.write_text('test fixture')
                with patch.object(builder, 'SKILLS', skills), self.assertRaises(ValueError):
                    builder.build(root / 'archive.zip')
                self.assertFalse((root / 'archive.zip').exists())


if __name__ == '__main__':
    unittest.main()
