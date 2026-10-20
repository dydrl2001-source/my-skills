"""Local video evidence extraction. JSON on stdout; progress on stderr."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlsplit


class ReaderError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(message)


def dump(data):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def timestamp(value):
    try:
        parts = str(value).split(':')
        if not 1 <= len(parts) <= 3:
            raise ValueError()
        numbers = [float(p) for p in parts]
        if any(not math.isfinite(p) or p < 0 for p in numbers):
            raise ValueError()
        return sum(p * 60 ** i for i, p in enumerate(reversed(numbers)))
    except ValueError:
        raise ReaderError('invalid_range', f'Invalid timestamp: {value}')


def clock(seconds):
    ms = round(seconds * 1000)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}.{ms % 1000:03}'


def command(args, timeout=60):
    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ReaderError('timeout', f'Operation exceeded {timeout} seconds.')
    if result.returncode:
        # Bound error output; never dump a whole downloaded page or traceback.
        detail = (result.stderr or result.stdout).strip()[-1800:]
        raise ReaderError('process_failed', detail or f'Process exited with {result.returncode}.')
    return result


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def source_kind(source):
    if re.match(r'^[A-Za-z]:[\\/]', source):
        return 'file'
    parsed = urlsplit(source)
    if parsed.scheme:
        if parsed.scheme not in ('http', 'https'):
            raise ReaderError('unsupported_scheme', 'Only HTTP(S) URLs or local file paths are supported.')
        if not parsed.hostname or parsed.username or parsed.password:
            raise ReaderError('invalid_url', 'Use a valid HTTP(S) URL without embedded credentials.')
        return 'url'
    return 'file'


def probe(path):
    import av
    try:
        with av.open(str(path)) as media:
            videos = media.streams.video
            if not videos:
                raise ReaderError('no_video', 'The input has no video stream.')
            stream = videos[0]
            duration = float(stream.duration * stream.time_base) if stream.duration is not None else float(media.duration or 0) / 1000000
            if not math.isfinite(duration) or duration <= 0:
                raise ReaderError('unknown_duration', 'Cannot establish a finite video duration.')
            return {'duration_seconds': round(duration, 6), 'width': stream.width, 'height': stream.height,
                    'fps': float(stream.average_rate or 0), 'has_audio': bool(media.streams.audio),
                    'size_bytes': path.stat().st_size}
    except ReaderError:
        raise
    except Exception as exc:
        raise ReaderError('invalid_media', f'Cannot open video: {str(exc)[:500]}')


def sampling(start, end, interval, count, fps):
    # Include a frame near the end, and spread a capped sample across the whole range.
    last = max(start, end - max(0.1, 1 / (fps or 25)))
    desired = max(2, math.ceil((last - start) / interval) + 1)
    n = min(count, desired)
    if last == start or n == 1:
        return [start]
    if desired > count:
        return [start + (last - start) * i / (n - 1) for i in range(n)]
    points = [start + i * interval for i in range(desired - 1) if start + i * interval < last]
    return points + [last]


def extract_frames(path, times, output):
    frames_dir = output / 'frames'
    frames_dir.mkdir()
    frames = []
    for index, seconds in enumerate(times, 1):
        target = frames_dir / f'frame-{index:03d}-{seconds:010.3f}.jpg'
        result = command([ffmpeg(), '-hide_banner', '-nostdin', '-loglevel', 'info',
                          '-ss', f'{seconds:.6f}', '-i', str(path), '-map', '0:v:0',
                          '-vf', "showinfo,scale=w='min(1280,iw)':h='min(1280,ih)':force_original_aspect_ratio=decrease",
                          '-frames:v', '1', '-q:v', '2', '-y', str(target)], timeout=45)
        if not target.is_file() or not target.stat().st_size:
            raise ReaderError('frame_failed', f'No image decoded at {seconds:.3f} seconds.')
        match = re.search(r'Parsed_showinfo[^\n]*n:\s*0\s+[^\n]*pts_time:([-+\d.eE]+)', result.stderr)
        actual = seconds + float(match.group(1)) if match else None
        frames.append({'requested_seconds': round(seconds, 6), 'seconds': round(actual, 6) if actual is not None else None,
                       'timestamp': clock(actual if actual is not None else seconds),
                       'timestamp_basis': 'decoded_pts' if actual is not None else 'requested_seek', 'path': str(target)})
    return frames


def contact_sheets(frames, output):
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    sheets = []
    font = ImageFont.load_default(size=18)
    for offset in range(0, len(frames), 12):
        batch = frames[offset:offset + 12]
        columns = min(3, len(batch))
        rows = math.ceil(len(batch) / columns)
        canvas = Image.new('RGB', (columns * 320, rows * 344), '#e8e8e8')
        draw = ImageDraw.Draw(canvas)
        for i, frame in enumerate(batch):
            x, y = (i % columns) * 320, (i // columns) * 344
            with Image.open(frame['path']) as original:
                thumb = ImageOps.contain(original.convert('RGB'), (304, 304))
            canvas.paste(thumb, (x + (320 - thumb.width) // 2, y + (304 - thumb.height) // 2 + 4))
            draw.text((x + 10, y + 316), f"{offset + i + 1:02}  {frame['timestamp']}", fill='#111111', font=font)
        target = output / f'contact-sheet-{len(sheets) + 1:02}.jpg'
        canvas.save(target, quality=90)
        sheets.append(str(target))
    return sheets


def download_worker(args):
    import yt_dlp
    limit = int(args.max_mib * 1024 * 1024)

    class Logger:
        def debug(self, msg):
            pass
        def warning(self, msg):
            pass
        def error(self, msg):
            print(str(msg)[:1200], file=sys.stderr)

    def progress(event):
        if event.get('downloaded_bytes', 0) > limit:
            raise ReaderError('size_limit', f'Download exceeds {args.max_mib:g} MiB.')

    options = {'outtmpl': str(Path(args.output) / 'source.%(ext)s'), 'noplaylist': True,
               'format': 'b[ext=mp4]/b/bv*+ba', 'merge_output_format': 'mp4',
               'quiet': True, 'no_warnings': True, 'logger': Logger(), 'cachedir': False,
               'socket_timeout': 20, 'retries': 1, 'extractor_retries': 1, 'fragment_retries': 1,
               'max_filesize': limit, 'progress_hooks': [progress], 'ffmpeg_location': ffmpeg()}
    if args.cookies_file:
        options['cookiefile'] = str(Path(args.cookies_file).resolve())
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(args.source, download=False)
        if not info or info.get('_type') in ('playlist', 'multi_video') or 'entries' in info:
            raise ReaderError('playlist_not_supported', 'Supply a URL for one video, not a playlist.')
        if info.get('is_live') or info.get('live_status') in ('is_live', 'is_upcoming'):
            raise ReaderError('live_not_supported', 'Live or upcoming streams are not supported.')
        if info.get('duration') and info['duration'] > args.max_duration:
            raise ReaderError('duration_limit', f'Video exceeds {args.max_duration:g} seconds.')
        if (info.get('filesize') or info.get('filesize_approx') or 0) > limit:
            raise ReaderError('size_limit', f'Video exceeds {args.max_mib:g} MiB.')
        downloader.process_ie_result(info, download=True)
    candidates = [p for p in Path(args.output).glob('source.*') if p.suffix.lower() in ('.mp4', '.mkv', '.webm', '.mov', '.m4v', '.avi')]
    if len(candidates) != 1:
        raise ReaderError('download_incomplete', 'Downloader did not produce one complete video file.')
    details = {key: info.get(key) for key in ('id', 'title', 'description', 'uploader', 'webpage_url', 'extractor')}
    return {'status': 'complete', 'path': str(candidates[0].resolve()), 'details': details}


def acquire(args, output):
    kind = source_kind(args.source)
    if kind == 'file':
        path = Path(args.source).expanduser().resolve()
        if not path.is_file():
            raise ReaderError('source_not_found', f'Local video not found: {path}')
        return path, {'kind': 'local_file', 'input': str(path)}
    print('Acquiring one video with yt-dlp...', file=sys.stderr, flush=True)
    cmd = [sys.executable, str(Path(__file__).resolve()), '_download', args.source,
           '--output', str(output), '--max-duration', str(args.max_duration), '--max-mib', str(args.max_mib)]
    if args.cookies_file:
        cmd += ['--cookies-file', args.cookies_file]
    try:
        result = command(cmd, timeout=args.download_timeout)
        data = json.loads(result.stdout)
        if data.get('status') == 'error':
            raise ReaderError(data['error']['code'], data['error']['message'])
    except ReaderError as exc:
        raise ReaderError('acquisition_failed', f'Could not acquire the video. {exc.message}')
    return Path(data['path']), {'kind': 'url', 'input': args.source, **data['details']}


def transcription_worker(args):
    from faster_whisper import WhisperModel
    from runtime import runtime_root
    model_root = runtime_root() / 'models'
    os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')
    os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')
    model = WhisperModel(args.model, device='cpu', compute_type='int8',
                         cpu_threads=min(8, os.cpu_count() or 2), download_root=str(model_root))
    segments, info = model.transcribe(args.source, language=None if args.language == 'auto' else args.language,
                                       beam_size=5, vad_filter=True, condition_on_previous_text=False)
    items = [{'start': round(s.start + args.offset, 3), 'end': round(s.end + args.offset, 3),
              'text': s.text.strip(), 'avg_logprob': round(s.avg_logprob, 4),
              'no_speech_probability': round(s.no_speech_prob, 4)} for s in segments]
    return {'status': 'complete' if items else 'no_speech_detected', 'engine': 'faster-whisper',
            'model': args.model, 'language': info.language, 'language_probability': info.language_probability,
            'segments': items, 'notice': 'Machine transcription; verify uncertain wording against the source.'}


def transcribe(args, path, metadata, output, start, end):
    if not metadata['has_audio']:
        return {'status': 'no_audio', 'segments': []}
    if getattr(args, 'no_transcribe', False):
        return {'status': 'skipped', 'segments': []}
    print(f'Transcribing locally with {args.model}; first use downloads model weights...', file=sys.stderr, flush=True)
    wav = output / 'audio.wav'
    try:
        command([ffmpeg(), '-hide_banner', '-nostdin', '-loglevel', 'error', '-ss', str(start), '-i', str(path),
                 '-t', str(end - start), '-vn', '-ac', '1', '-ar', '16000', '-y', str(wav)], timeout=90)
        cmd = [sys.executable, str(Path(__file__).resolve()), '_transcribe', str(wav),
               '--model', args.model, '--language', args.language, '--offset', str(start)]
        result = command(cmd, timeout=args.transcription_timeout)
        data = json.loads(result.stdout)
        if data.get('status') == 'error':
            return {'status': 'failed', 'error': data['error'], 'segments': []}
        lines = [f"[{clock(s['start'])} --> {clock(s['end'])}] {s['text']}" for s in data['segments']]
        (output / 'transcript.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        data['path'] = str(output / 'transcript.txt')
        save_json(output / 'transcript.json', data)
        return data
    except (ReaderError, ValueError) as exc:
        return {'status': 'failed', 'error': {'code': getattr(exc, 'code', 'transcription_failed'), 'message': str(exc)[:1500]}, 'segments': []}


def report(data, output):
    source = data['source']
    lines = ['# Video evidence', '', f"Status: {data['status']}", f"Source: {source['input']}",
             f"Local video: {data['video_path']}", f"Duration: {data['metadata']['duration_seconds']:.3f} seconds",
             f"Inspected range: {data['range']['start_seconds']:.3f}–{data['range']['end_seconds']:.3f} seconds", '',
             '## Visual evidence', '', 'These are sampled frames, not continuous playback. Open the contact sheets and individual images before describing the visuals.']
    for path in data['contact_sheets']:
        lines.append(f'- [Contact sheet]({Path(path).name})')
    for frame in data['frames']:
        lines.append(f"- [{frame['timestamp']}]({Path(frame['path']).relative_to(output).as_posix()}) ({frame['timestamp_basis']})")
    lines += ['', '## Audio evidence', '', f"Transcription status: {data['transcription']['status']}"]
    for segment in data['transcription'].get('segments', []):
        lines.append(f"- [{clock(segment['start'])}–{clock(segment['end'])}] {segment['text']}")
    if data['transcription'].get('error'):
        lines.append(data['transcription']['error']['message'])
    if source.get('description'):
        lines += ['', '## Publisher description (not video evidence)', '', source['description']]
    (output / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def inspect(args):
    kind = source_kind(args.source)
    # Validate source before making output directories.
    if kind == 'file' and not Path(args.source).expanduser().is_file():
        raise ReaderError('source_not_found', f'Local video not found: {args.source}')
    for name in ('max_duration', 'max_mib'):
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            raise ReaderError('invalid_option', f'{name} must be positive and finite.')
    if args.action == 'inspect' and (not math.isfinite(args.interval) or args.interval <= 0 or not 1 <= args.max_frames <= 120):
        raise ReaderError('invalid_option', 'Use a positive finite interval and 1–120 frames.')
    out = Path(args.output).expanduser().resolve()
    if out.exists():
        raise ReaderError('output_exists', 'Choose a new output directory; previous evidence is never overwritten.')
    out.mkdir(parents=True)
    try:
        path, source = acquire(args, out)
        metadata = probe(path)
        if metadata['duration_seconds'] > args.max_duration:
            raise ReaderError('duration_limit', f'Video exceeds {args.max_duration:g} seconds.')
        if metadata['size_bytes'] > args.max_mib * 1024 * 1024:
            raise ReaderError('size_limit', f'Video exceeds {args.max_mib:g} MiB.')
        start = timestamp(args.start)
        end = timestamp(args.end) if args.end is not None else metadata['duration_seconds']
        if start >= end or end > metadata['duration_seconds'] + 0.001:
            raise ReaderError('invalid_range', 'Requested range must lie inside the video and have positive length.')
        if args.action == 'frames':
            times = sorted(set(timestamp(t) for t in args.at))
            if len(times) > 120 or any(t >= metadata['duration_seconds'] for t in times):
                raise ReaderError('invalid_range', 'Use at most 120 timestamps strictly before the video end.')
        elif args.action == 'inspect':
            times = sampling(start, end, args.interval, args.max_frames, metadata['fps'])
        else:
            times = []
        frames = extract_frames(path, times, out) if times else []
        sheets = contact_sheets(frames, out) if frames else []
        transcript = {'status': 'not_requested', 'segments': []} if args.action == 'frames' else transcribe(args, path, metadata, out, start, end)
        status = 'partial' if transcript['status'] == 'failed' else 'complete'
        data = {'schema_version': 1, 'status': status, 'source': source, 'video_path': str(path), 'metadata': metadata,
                'range': {'start_seconds': start, 'end_seconds': end}, 'visual_evidence': 'sampled_frames' if frames else 'none',
                'frames': frames, 'contact_sheets': sheets, 'transcription': transcript,
                'manifest_path': str(out / 'manifest.json'), 'report_path': str(out / 'report.md')}
        save_json(out / 'manifest.json', data)
        report(data, out)
        return {'status': status, 'manifest_path': data['manifest_path'], 'report_path': data['report_path'],
                'frame_count': len(frames), 'contact_sheets': sheets, 'transcription_status': transcript['status'], 'video_path': str(path)}
    except Exception as exc:
        failure = {'status': 'error', 'error': {'code': getattr(exc, 'code', 'unexpected_error'), 'message': str(exc)[:2000]}}
        save_json(out / 'failure.json', failure)
        raise


def doctor():
    names = ['yt-dlp', 'imageio-ffmpeg', 'Pillow', 'av', 'faster-whisper', 'ctranslate2']
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    try:
        executable = ffmpeg()
        command([executable, '-version'], timeout=15)
    except Exception as exc:
        executable = str(exc)
    ready = all(versions.values()) and Path(executable).is_file()
    return {'status': 'ready' if ready else 'missing_dependencies', 'python': sys.executable, 'versions': versions, 'ffmpeg': executable,
            'transcription': 'CPU int8; model weights downloaded on first use; audio stays local.'}


def parser():
    p = argparse.ArgumentParser(description='Extract local, timestamped video evidence from a URL or video file.')
    sub = p.add_subparsers(dest='action', required=True)
    sub.add_parser('doctor', help='Check local dependencies without downloading a speech model.')
    for name in ('inspect', 'frames', 'transcribe', '_download'):
        part = sub.add_parser(name, help={'inspect': 'Sample frames and transcribe audio.', 'frames': 'Extract exact requested timestamps.', 'transcribe': 'Transcribe an existing local video.', '_download': argparse.SUPPRESS}[name])
        part.add_argument('source')
        part.add_argument('--output', required=True)
        part.add_argument('--max-duration', type=float, default=1200)
        part.add_argument('--max-mib', type=float, default=500)
        part.add_argument('--cookies-file', help='Explicitly supplied Netscape cookies file; browser cookies are never read automatically.')
        part.add_argument('--download-timeout', type=int, default=150)
        part.add_argument('--start', default='0')
        part.add_argument('--end')
        if name in ('inspect', 'transcribe'):
            part.add_argument('--model', choices=['tiny', 'base', 'small', 'medium'], default='small')
            part.add_argument('--language', default='auto')
            part.add_argument('--transcription-timeout', type=int, default=600)
            part.add_argument('--no-transcribe', action='store_true')
        if name == 'inspect':
            part.add_argument('--interval', type=float, default=2)
            part.add_argument('--max-frames', type=int, default=48)
        if name == 'frames':
            part.add_argument('--at', nargs='+', required=True, help='Seconds or HH:MM:SS timestamps.')
    worker = sub.add_parser('_transcribe', help=argparse.SUPPRESS)
    worker.add_argument('source')
    worker.add_argument('--model', default='small')
    worker.add_argument('--language', default='auto')
    worker.add_argument('--offset', type=float, default=0)
    return p


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    args = parser().parse_args()
    try:
        if args.action == 'doctor':
            data = doctor()
        elif args.action == '_download':
            data = download_worker(args)
        elif args.action == '_transcribe':
            data = transcription_worker(args)
        else:
            data = inspect(args)
        dump(data)
        return 0 if data['status'] != 'missing_dependencies' else 2
    except Exception as exc:
        dump({'status': 'error', 'error': {'code': getattr(exc, 'code', 'operation_failed'), 'message': str(exc)[:2000]}})
        return 2


if __name__ == '__main__':
    sys.exit(main())
