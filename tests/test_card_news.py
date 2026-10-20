"""Behavioral checks for the portable offline card renderer."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.agents/skills/card-news/scripts/render_cards.py'


class CardNewsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def render(self, spec, output='result'):
        source = self.base / 'spec.json'
        source.write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
        return subprocess.run([sys.executable, str(SCRIPT), str(source), '--output',
                               str(self.base / output)], capture_output=True,
                              encoding='utf-8', timeout=30)

    def success(self, spec, output='result'):
        run = self.render(spec, output)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(run.stderr, '')
        return json.loads(Path(result['manifest']).read_text(encoding='utf-8'))

    def assert_error(self, run, code):
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout, '')
        error = json.loads(run.stderr)
        self.assertEqual(error['status'], 'error')
        self.assertEqual(error['code'], code)

    def test_multiple_png_dimensions_font_and_numbering(self):
        manifest = self.success({'width': 480, 'height': 640, 'numbering': True,
                                 'cards': [{'title': '함께 걷는 하루'}, {'body': '예시 일정'}]})
        self.assertEqual(len(manifest['cards']), 2)
        self.assertTrue(Path(manifest['font']['path']).is_file())
        self.assertEqual(len(manifest['font']['sha256']), 64)
        for index, card in enumerate(manifest['cards'], 1):
            with Image.open(card['path']) as image:
                self.assertEqual(image.size, (480, 640))
            self.assertEqual(card['numbering']['text'], f'{index} / 2')
            self.assertEqual(card['width'], 480)
            self.assertEqual(card['height'], 640)

    def test_unspaced_korean_and_english_wrap_within_actual_bounds(self):
        original = '함께걷는하루서로의이야기를듣고마음을나눕니다' * 5 + 'VeryLongUnspacedEnglishText' * 4
        card = self.success({'width': 300, 'height': 600, 'margin': 28,
                             'cards': [{'body': original}]})['cards'][0]
        lines = card['text'][0]['lines']
        self.assertEqual(''.join(line['text'] for line in lines), original)
        self.assertGreater(len(lines), 1)
        for line in lines:
            left, top, right, bottom = line['bounds']
            self.assertGreaterEqual(left, 28)
            self.assertGreaterEqual(top, 28)
            self.assertLessEqual(right, 272)
            self.assertLessEqual(bottom, 572)
        with Image.open(card['path']) as image:
            box = ImageChops.difference(image, Image.new('RGB', image.size, '#F5F1E8')).getbbox()
            self.assertIsNotNone(box)
            self.assertGreaterEqual(box[0], 28)
            self.assertLessEqual(box[2], 272)

    def test_auto_foreground_is_case_consistent_and_readable(self):
        lower = self.success({'background_color': '#ffffff', 'cards': [{'title': '낮'}]}, 'lower')
        upper = self.success({'background_color': '#FFFFFF', 'cards': [{'title': '낮'}]}, 'upper')
        dark = self.success({'background_color': '#101010', 'cards': [{'title': '밤'}]}, 'dark')
        self.assertEqual(lower['cards'][0]['text_color'], upper['cards'][0]['text_color'])
        self.assertEqual(lower['cards'][0]['text_color'], '#111111')
        self.assertEqual(dark['cards'][0]['text_color'], '#FFFFFF')

    def test_large_initial_glyph_can_shrink_to_fit(self):
        card = self.success({'width': 256, 'height': 256, 'margin': 85,
                             'font_size': 120, 'min_font_size': 16,
                             'cards': [{'title': '가나다'}]})['cards'][0]
        self.assertLess(card['text'][0]['font_size'], 120)
        self.assertEqual(''.join(line['text'] for line in card['text'][0]['lines']), '가나다')
        for line in card['text'][0]['lines']:
            self.assertLessEqual(line['bounds'][2], 171)
            self.assertLessEqual(line['bounds'][3], 171)

    def test_auto_foreground_chooses_higher_actual_contrast(self):
        card = self.success({'background_color': '#767676', 'cards': [{'title': '대비'}]})['cards'][0]
        # Against #767676, white is ~4.54:1; #111111 is only ~4.16:1.
        self.assertEqual(card['text_color'], '#FFFFFF')

    def test_background_is_relative_to_spec_and_overlay_is_visible(self):
        Image.new('RGB', (800, 300), '#FF0000').save(self.base / 'photo.png')
        card = self.success({'cards': [{'title': '사진 위 글', 'background_image': 'photo.png'}]})['cards'][0]
        self.assertEqual(card['background_image'], str((self.base / 'photo.png').resolve()))
        self.assertEqual(card['text_color'], '#FFFFFF')
        with Image.open(card['path']) as image:
            red, green, blue = image.getpixel((0, 0))
            self.assertTrue(0 < red < 255)
            self.assertEqual((green, blue), (0, 0))

    def test_missing_or_invalid_background_fails_without_output(self):
        for name in ['missing.png', 'broken.png']:
            (self.base / 'broken.png').write_text('not an image', encoding='utf-8')
            run = self.render({'cards': [{'body': '내용', 'background_image': name}]})
            self.assert_error(run, 'background_error')
            self.assertFalse((self.base / 'result').exists())

    def test_existing_output_and_files_are_preserved(self):
        output = self.base / 'result'
        output.mkdir()
        (output / 'keep.txt').write_text('keep', encoding='utf-8')
        self.assert_error(self.render({'cards': [{'title': '안녕'}]}), 'output_exists')
        self.assertEqual((output / 'keep.txt').read_text(), 'keep')
        self.assertEqual(len(list(output.iterdir())), 1)

    def test_overflow_fails_honestly_without_truncating(self):
        self.assert_error(self.render({'width': 256, 'height': 256,
                                      'cards': [{'body': '가' * 10000}]}), 'text_overflow')
        self.assertFalse((self.base / 'result').exists())

    def test_resource_limits_and_invalid_input(self):
        for spec in [{'width': 99999, 'cards': [{'title': 'a'}]},
                     {'cards': [{'title': 'a'}] * 25},
                     {'numbering': 'false', 'cards': [{'title': 'a'}]},
                     {'cards': [{'title': 'a', 'background_color': 'red'}]}]:
            self.assert_error(self.render(spec), 'invalid_spec')


if __name__ == '__main__':
    unittest.main()
