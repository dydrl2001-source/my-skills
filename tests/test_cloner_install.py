import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/install_cloners.sh'
SKILLS = ('clone-app', 'clone-website', 'true-web-clone')


@unittest.skipIf(os.name == 'nt', 'The Bash installer targets macOS and Linux.')
class ClonerInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cloner install ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repository with spaces'
        (self.repo / 'scripts').mkdir(parents=True)
        self.script = self.repo / 'scripts/install_cloners.sh'
        shutil.copyfile(SCRIPT, self.script)
        for skill in SKILLS:
            source = self.repo / '.agents/skills' / skill
            (source / 'references').mkdir(parents=True)
            (source / 'SKILL.md').write_text(f'# {skill}\n', encoding='utf-8')
            (source / 'references/guide.md').write_text('Complete skill resource.\n', encoding='utf-8')
        self.destination = self.root / 'local skills'

    def run_installer(self, *args, script=None, destination=None):
        env = os.environ.copy()
        env['CODEX_CLONER_SKILLS_DIR'] = str(destination or self.destination)
        return subprocess.run(
            ['bash', str(script or self.script), *args],
            cwd=self.root, env=env, text=True, encoding='utf-8',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )

    def assert_installed(self):
        for skill in SKILLS:
            target = self.destination / skill
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), (self.repo / '.agents/skills' / skill).resolve())
            self.assertEqual(
                (target / 'references/guide.md').read_text(encoding='utf-8'),
                'Complete skill resource.\n',
            )

    def test_fresh_install_links_complete_skill_directories(self):
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_installed()

    def test_repeated_run_preserves_existing_links(self):
        first = self.run_installer()
        self.assertEqual(first.returncode, 0, first.stderr)
        original = {
            skill: ((self.destination / skill).lstat(), os.readlink(self.destination / skill))
            for skill in SKILLS
        }
        second = self.run_installer()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assert_installed()
        for skill, (stat, link) in original.items():
            target = self.destination / skill
            self.assertEqual(target.lstat().st_ino, stat.st_ino)
            self.assertEqual(target.lstat().st_mtime_ns, stat.st_mtime_ns)
            self.assertEqual(os.readlink(target), link)

    def test_conflicts_are_preserved_without_partial_new_links(self):
        for kind in ('file', 'directory', 'other-link', 'dangling-link'):
            with self.subTest(kind=kind):
                destination = self.root / kind
                destination.mkdir()
                conflict = destination / SKILLS[-1]
                if kind == 'file':
                    conflict.write_text('Keep existing file.', encoding='utf-8')
                elif kind == 'directory':
                    conflict.mkdir()
                    (conflict / 'keep.txt').write_text('Keep existing directory.', encoding='utf-8')
                else:
                    other = self.root / f'{kind}-target'
                    if kind == 'other-link':
                        other.mkdir()
                    conflict.symlink_to(other, target_is_directory=True)
                before = conflict.lstat()
                result = self.run_installer(destination=destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(str(conflict), result.stderr)
                self.assertEqual(sorted(path.name for path in destination.iterdir()), [SKILLS[-1]])
                self.assertEqual(conflict.lstat().st_ino, before.st_ino)
                if kind == 'file':
                    self.assertEqual(conflict.read_text(encoding='utf-8'), 'Keep existing file.')
                elif kind == 'directory':
                    self.assertEqual(list(path.name for path in conflict.iterdir()), ['keep.txt'])
                else:
                    self.assertEqual(os.readlink(conflict), str(other))

    def test_missing_source_fails_before_creating_destination(self):
        missing = self.repo / '.agents/skills' / SKILLS[-1] / 'SKILL.md'
        missing.unlink()
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(missing), result.stderr)
        self.assertFalse(self.destination.exists())

    def test_destination_alias_cannot_hide_conflict_behind_missing_parent(self):
        self.destination.mkdir()
        conflict = self.destination / SKILLS[-1]
        conflict.write_text('Keep existing file.', encoding='utf-8')
        alias = self.root / 'destination alias'
        alias.symlink_to(self.destination, target_is_directory=True)
        unused = self.root / 'unused parent'
        result = self.run_installer(destination=unused / '..' / alias.name)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(conflict), result.stderr)
        self.assertFalse(unused.exists())
        self.assertTrue(alias.is_symlink())
        self.assertEqual(list(path.name for path in self.destination.iterdir()), [SKILLS[-1]])
        self.assertEqual(conflict.read_text(encoding='utf-8'), 'Keep existing file.')

    def test_relative_symlink_entrypoint_resolves_repository(self):
        launchers = self.root / 'linked entrypoints'
        launchers.mkdir()
        entrypoint = launchers / 'installer'
        entrypoint.symlink_to(Path('..') / self.repo.name / 'scripts/install_cloners.sh')
        alias = self.root / 'installer alias'
        alias.symlink_to(Path(launchers.name) / entrypoint.name)
        result = self.run_installer(script=alias)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_installed()

    def test_help_and_unexpected_args_never_install(self):
        help_result = self.run_installer('--help')
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn('CODEX_CLONER_SKILLS_DIR', help_result.stdout)
        for args in (('--unknown',), ('--help', 'extra')):
            with self.subTest(args=args):
                result = self.run_installer(*args)
                self.assertEqual(result.returncode, 2)
        self.assertFalse(self.destination.exists())


if __name__ == '__main__':
    unittest.main()
