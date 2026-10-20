import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import io
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.agents/skills/video-reader/scripts'


class PortableRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('portable_runtime', SCRIPTS / 'runtime.py')
        cls.runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runtime)

    def test_override_is_used_on_both_platforms(self):
        for platform in ('nt', 'posix'):
            with self.subTest(platform=platform), patch.dict(os.environ, {'VIDEO_READER_HOME': 'custom runtime'}, clear=True):
                self.assertEqual(self.runtime.runtime_root(platform), Path('custom runtime').resolve())

    def test_windows_reuses_existing_runtime_location(self):
        with patch.dict(os.environ, {'LOCALAPPDATA': 'local cache'}, clear=True):
            self.assertEqual(self.runtime.runtime_root('nt'), Path('local cache').resolve() / 'CodexVideoReader')

    def test_linux_respects_xdg_cache(self):
        with patch.dict(os.environ, {'XDG_CACHE_HOME': 'linux cache'}, clear=True):
            self.assertEqual(self.runtime.runtime_root('posix'), Path('linux cache').resolve() / 'CodexVideoReader')

    def test_interpreter_layouts(self):
        root = Path('runtime')
        self.assertEqual(self.runtime.venv_python(root, 'nt'), root / 'venv/Scripts/python.exe')
        self.assertEqual(self.runtime.venv_python(root, 'posix'), root / 'venv/bin/python')

    def test_missing_runtime_gives_actionable_error(self):
        with tempfile.TemporaryDirectory() as temp:
            env = dict(os.environ, VIDEO_READER_HOME=temp)
            result = subprocess.run([sys.executable, str(SCRIPTS / 'run.py'), 'doctor'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('setup.py', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_setup_rejects_python_310_before_installing_incompatible_pillow(self):
        with patch.object(sys, 'path', [str(SCRIPTS), *sys.path]):
            spec = importlib.util.spec_from_file_location('video_setup', SCRIPTS / 'setup.py')
            setup = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(setup)
        with patch.object(sys, 'version_info', (3, 10, 0)), patch('subprocess.run') as command, patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(setup.main(), 2)
            command.assert_not_called()


if __name__ == '__main__':
    unittest.main()
