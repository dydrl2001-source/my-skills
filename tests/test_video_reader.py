import json
import subprocess
import sys
import tempfile
import unittest
import functools
import http.server
import threading
import urllib.parse
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / '.agents' / 'skills' / 'video-reader' / 'scripts' / 'video_reader.py'


class CliContractTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, encoding='utf-8', timeout=60)

    def test_help_explains_inspection_and_targeted_frames(self):
        result = self.invoke('--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('inspect', result.stdout)
        self.assertIn('frames', result.stdout)

    def test_missing_media_is_machine_readable_error_not_a_success(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.invoke('inspect', str(Path(folder) / 'absent.mp4'), '--output', str(Path(folder) / 'out'))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stdout.strip(), result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload['status'], 'error')
        self.assertEqual(payload['error']['code'], 'source_not_found')

    def test_url_with_non_web_scheme_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.invoke('inspect', 'ftp://example.com/video.mp4', '--output', str(Path(folder) / 'out'))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stdout.strip(), result.stderr)
        self.assertEqual(json.loads(result.stdout)['error']['code'], 'unsupported_scheme')


class MediaIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import imageio_ffmpeg
        cls.folder = tempfile.TemporaryDirectory()
        cls.root = Path(cls.folder.name)
        cls.video = cls.root / '한글 video & sample.mp4'
        subprocess.run([
            imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
            '-f', 'lavfi', '-i', 'color=c=red:s=320x240:r=10:d=2',
            '-f', 'lavfi', '-i', 'color=c=blue:s=320x240:r=10:d=2',
            '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]',
            '-map', '[v]', '-c:v', 'mpeg4', '-y', str(cls.video)
        ], check=True, capture_output=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, encoding='utf-8', timeout=90)

    def test_targeted_frames_show_the_correct_time_and_actual_image(self):
        from PIL import Image
        out = self.root / 'exact frames'
        result = self.invoke('frames', str(self.video), '--at', '0.5', '00:02.5', '--output', str(out))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['frames']), 2)
        for frame, seconds, channel in zip(data['frames'], [0.5, 2.5], [0, 2]):
            self.assertAlmostEqual(frame['requested_seconds'], seconds, places=2)
            self.assertAlmostEqual(frame['seconds'], seconds, delta=0.11)
            with Image.open(frame['path']) as pic:
                rgb = pic.convert('RGB').getpixel((160, 120))
            self.assertGreater(rgb[channel], 200)
            self.assertLess(rgb[2 if channel == 0 else 0], 40)

    def test_bounded_sampling_spans_the_video_and_reports_missing_audio(self):
        out = self.root / 'bounded'
        result = self.invoke('inspect', str(self.video), '--interval', '0.1', '--max-frames', '3', '--output', str(out))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(data['status'], 'complete')
        self.assertEqual(len(data['frames']), 3)
        self.assertEqual(data['frames'][0]['requested_seconds'], 0)
        self.assertGreater(data['frames'][-1]['seconds'], 3.5)
        self.assertEqual(data['transcription']['status'], 'no_audio')
        self.assertTrue(Path(data['contact_sheets'][0]).is_file())

    def test_existing_output_is_preserved(self):
        out = self.root / 'existing'
        out.mkdir()
        sentinel = out / 'keep.txt'
        sentinel.write_text('untouched')
        result = self.invoke('inspect', str(self.video), '--output', str(out), '--no-transcribe')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error']['code'], 'output_exists')
        self.assertEqual(sentinel.read_text(), 'untouched')

    def test_timestamp_past_end_is_rejected(self):
        result = self.invoke('frames', str(self.video), '--at', '5', '--output', str(self.root / 'out-of-range'))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error']['code'], 'invalid_range')

    def test_duration_limit_is_checked_before_extraction(self):
        result = self.invoke('inspect', str(self.video), '--max-duration', '3', '--output', str(self.root / 'too-long'))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error']['code'], 'duration_limit')

    def test_url_acquisition_produces_real_video_evidence(self):
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(self.root))
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}/' + urllib.parse.quote(self.video.name)
            out = self.root / 'url evidence'
            result = self.invoke('inspect', url, '--output', str(out), '--no-transcribe', '--max-frames', '2')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(data['source']['kind'], 'url')
            self.assertTrue(Path(data['video_path']).is_file())
            self.assertEqual(len(data['frames']), 2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()

