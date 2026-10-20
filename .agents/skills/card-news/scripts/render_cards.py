#!/usr/bin/env python3
"""Render an explicit UTF-8 card spec locally. Python 3.11+ and Pillow only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import warnings


class RenderError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(message)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RenderError('arguments_error', message)


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise RenderError('invalid_spec', f'{name} must be an integer in {low}..{high}')
    return value


def color(value, name, auto=False):
    if auto and value == 'auto':
        return value
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise RenderError('invalid_spec', f'{name} must be #RRGGBB' + (' or auto' if auto else ''))
    return value.upper()


def validate(raw):
    if not isinstance(raw, dict):
        raise RenderError('invalid_spec', 'Spec must be an object')
    known = {'width', 'height', 'margin', 'background_color', 'text_color', 'overlay_opacity',
             'font_size', 'min_font_size', 'numbering', 'cards'}
    if raw.keys() - known:
        raise RenderError('invalid_spec', f'Unknown spec fields: {sorted(raw.keys() - known)}')
    spec = dict(raw)
    for key, default, low, high in [('width', 600, 256, 2048), ('height', 600, 256, 2048),
                                  ('font_size', 44, 12, 120), ('min_font_size', 16, 12, 120)]:
        spec[key] = integer(raw.get(key, default), key, low, high)
    spec['margin'] = integer(raw.get('margin', 48), 'margin', 12, min(spec['width'], spec['height']) // 3)
    if spec['min_font_size'] > spec['font_size']:
        raise RenderError('invalid_spec', 'min_font_size must not exceed font_size')
    spec['numbering'] = raw.get('numbering', False)
    if type(spec['numbering']) is not bool:
        raise RenderError('invalid_spec', 'numbering must be boolean')
    opacity = raw.get('overlay_opacity', 0.55)
    if type(opacity) not in (int, float) or not 0 <= opacity <= 1:
        raise RenderError('invalid_spec', 'overlay_opacity must be between 0 and 1')
    spec['overlay_opacity'] = opacity
    spec['background_color'] = color(raw.get('background_color', '#F5F1E8'), 'background_color')
    spec['text_color'] = color(raw.get('text_color', 'auto'), 'text_color', auto=True)
    cards = raw.get('cards')
    if not isinstance(cards, list) or not 1 <= len(cards) <= 24:
        raise RenderError('invalid_spec', 'cards must contain 1..24 objects')
    if spec['width'] * spec['height'] * len(cards) > 48_000_000:
        raise RenderError('invalid_spec', 'Total output area exceeds 48 million pixels')
    total_text = 0
    spec['cards'] = []
    for index, raw_card in enumerate(cards, 1):
        allowed = {'title', 'body', 'background_color', 'text_color', 'background_image'}
        if not isinstance(raw_card, dict) or raw_card.keys() - allowed:
            raise RenderError('invalid_spec', f'Card {index} has invalid fields')
        card = dict(raw_card)
        for field in ['title', 'body']:
            value = card.get(field, '')
            if not isinstance(value, str):
                raise RenderError('invalid_spec', f'Card {index} {field} must be text')
            value = value.replace('\r\n', '\n').replace('\r', '\n')
            if any(ord(c) < 32 and c != '\n' for c in value):
                raise RenderError('invalid_spec', f'Card {index} contains unsupported control characters')
            card[field] = value
        length = len(card['title']) + len(card['body'])
        if not (card['title'].strip() or card['body'].strip()) or length > 12000:
            raise RenderError('invalid_spec', f'Card {index} needs nonempty text, at most 12000 characters')
        total_text += length
        card['background_color'] = color(card.get('background_color', spec['background_color']), 'background_color')
        card['text_color'] = color(card.get('text_color', spec['text_color']), 'text_color', auto=True)
        if 'background_image' in card and (not isinstance(card['background_image'], str) or not card['background_image']):
            raise RenderError('invalid_spec', 'background_image must be a nonempty local path')
        spec['cards'].append(card)
    if total_text > 60000:
        raise RenderError('invalid_spec', 'Total text exceeds 60000 characters')
    return spec


def wrap(text, font, width, max_lines):
    """Preserve every character, preferring spaces then breaking long tokens."""
    result = []
    for paragraph in text.split('\n'):
        if not paragraph:
            result.append('')
        while paragraph:
            # Search a short prefix first; measuring half of a 12000-character
            # paragraph at every line needlessly makes overflow cases expensive.
            low, high = 0, min(16, len(paragraph))
            while high < len(paragraph):
                box = font.getbbox(paragraph[:high])
                if box[2] - box[0] > width:
                    break
                low, high = high, min(high * 2, len(paragraph))
            while low < high:
                middle = (low + high + 1) // 2
                box = font.getbbox(paragraph[:middle])
                if box[2] - box[0] <= width:
                    low = middle
                else:
                    high = middle - 1
            if low == 0:
                return None
            end = low
            if end < len(paragraph):
                space = paragraph.rfind(' ', 0, end)
                if space > 0:
                    end = space + 1
            result.append(paragraph[:end])
            if len(result) > max_lines:
                return None
            paragraph = paragraph[end:]
        if len(result) > max_lines:
            return None
    return result


def layout(card, spec, font_path, ImageFont):
    width, height, margin = spec['width'], spec['height'], spec['margin']
    available = height - 2 * margin - (36 if spec['numbering'] else 0)
    for size in range(spec['font_size'], spec['min_font_size'] - 1, -1):
        blocks, cursor, fits = [], margin, True
        for field in ['title', 'body']:
            if not card[field]:
                continue
            font_size = size if field == 'title' else max(spec['min_font_size'], round(size * 0.65))
            font = ImageFont.truetype(str(font_path), font_size)
            ascent, descent = font.getmetrics()
            advance = ascent + descent + max(3, font_size // 5)
            lines = wrap(card[field], font, width - 2 * margin, max(0, (margin + available - cursor) // advance + 1))
            if lines is None:
                fits = False
                break
            placed = []
            for line in lines:
                box = font.getbbox(line)
                placed.append({'text': line, 'bounds': [margin, cursor, margin + box[2] - box[0],
                                                       cursor + box[3] - box[1]],
                               'offset': [margin - box[0], cursor - box[1]]})
                cursor += advance
            blocks.append({'role': field, 'font_size': font_size, 'lines': placed, '_font': font})
            cursor += max(10, size // 2)
        if not fits:
            continue
        bottom = max(line['bounds'][3] for block in blocks for line in block['lines'])
        if bottom <= margin + available:
            return blocks
    raise RenderError('text_overflow', 'Text cannot fit at min_font_size; shorten it, split cards or enlarge dimensions')


def foreground(background):
    rgb = [int(background[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    luminance = sum(v * weight for v, weight in zip(linear, [0.2126, 0.7152, 0.0722]))
    dark_channel = 17 / 255
    dark_luminance = ((dark_channel + 0.055) / 1.055) ** 2.4
    dark_contrast = (max(luminance, dark_luminance) + 0.05) / (min(luminance, dark_luminance) + 0.05)
    white_contrast = 1.05 / (luminance + 0.05)
    return '#111111' if dark_contrast >= white_contrast else '#FFFFFF'


def render(spec_path, output, font_path):
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError as exc:
        raise RenderError('dependency_missing', 'Pillow is required; install it explicitly before rendering') from exc
    if output.exists():
        raise RenderError('output_exists', f'Output must be a new directory: {output}')
    if not output.parent.is_dir():
        raise RenderError('output_error', 'Output parent directory must already exist')
    if spec_path.stat().st_size > 1_048_576:
        raise RenderError('invalid_spec', 'Spec exceeds 1 MiB')
    try:
        spec = validate(json.loads(spec_path.read_text(encoding='utf-8-sig')))
    except (ValueError, UnicodeError) as exc:
        raise RenderError('invalid_spec', f'Invalid UTF-8 JSON: {exc}') from exc
    try:
        if font_path.stat().st_size > 20_000_000:
            raise ValueError('Font exceeds 20 MB')
        probe_font = ImageFont.truetype(str(font_path), 16)
        font_info = {'path': str(font_path), 'sha256': hashlib.sha256(font_path.read_bytes()).hexdigest(),
                     'family': probe_font.getname()[0], 'style': probe_font.getname()[1]}
    except (OSError, ValueError) as exc:
        raise RenderError('font_error', str(exc)) from exc
    # Preflight every card before creating output, including background decoding.
    prepared = []
    for index, card in enumerate(spec['cards'], 1):
        background = None
        if 'background_image' in card:
            background = (spec_path.parent / card['background_image']).resolve()
            try:
                if background.stat().st_size > 20_000_000:
                    raise ValueError('Background exceeds 20 MB')
                with warnings.catch_warnings():
                    warnings.simplefilter('error', Image.DecompressionBombWarning)
                    with Image.open(background) as source:
                        if source.width * source.height > 16_000_000:
                            raise ValueError('Background exceeds 16 million pixels')
                        source.load()
            except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
                raise RenderError('background_error', f'Card {index}: {background}: {exc}') from exc
        prepared.append((card, background, layout(card, spec, font_path, ImageFont)))
    temporary = Path(tempfile.mkdtemp(prefix='.card-news-', dir=output.parent))
    try:
        manifest = {'status': 'ok', 'schema_version': 1, 'font': font_info, 'cards': []}
        for index, (card, background, blocks) in enumerate(prepared, 1):
            size = (spec['width'], spec['height'])
            image = Image.new('RGB', size, card['background_color'])
            if background:
                with Image.open(background) as source:
                    oriented = ImageOps.exif_transpose(source).convert('RGBA')
                    fitted = ImageOps.fit(oriented, size, method=Image.Resampling.LANCZOS)
                    image.paste(fitted, (0, 0), fitted)
                image = Image.blend(image, Image.new('RGB', size, '#000000'), spec['overlay_opacity'])
            text_color = card['text_color']
            if text_color == 'auto':
                text_color = '#FFFFFF' if background else foreground(card['background_color'])
            draw = ImageDraw.Draw(image)
            for block in blocks:
                for line in block['lines']:
                    draw.text(tuple(line.pop('offset')), line['text'], font=block['_font'], fill=text_color)
                del block['_font']
            numbering = None
            if spec['numbering']:
                text = f'{index} / {len(prepared)}'
                font = ImageFont.truetype(str(font_path), 16)
                box = font.getbbox(text)
                x, y = spec['width'] - spec['margin'] - (box[2] - box[0]), spec['height'] - spec['margin'] - (box[3] - box[1])
                draw.text((x - box[0], y - box[1]), text, font=font, fill=text_color)
                numbering = {'text': text, 'font_size': 16, 'bounds': [x, y, x + box[2] - box[0], y + box[3] - box[1]]}
            name = f'card-{index:02d}.png'
            image.save(temporary / name, format='PNG')
            manifest['cards'].append({'path': str(output / name), 'width': size[0], 'height': size[1],
                                      'background_color': card['background_color'],
                                      'background_image': str(background) if background else None,
                                      'overlay_opacity': spec['overlay_opacity'] if background else 0,
                                      'text_color': text_color, 'text': blocks, 'numbering': numbering})
        (temporary / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        # Path.rename refuses a destination directory on Windows; check also on POSIX.
        if output.exists():
            raise RenderError('output_exists', f'Output appeared during rendering: {output}')
        temporary.rename(output)
        return {'status': 'ok', 'manifest': str(output / 'manifest.json'), 'count': len(prepared)}
    finally:
        if temporary.exists():
            resolved_temp = temporary.resolve()
            if resolved_temp.parent == output.parent.resolve() and resolved_temp.name.startswith('.card-news-'):
                shutil.rmtree(resolved_temp)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    try:
        parser = Parser(description=__doc__)
        parser.add_argument('spec', type=Path)
        parser.add_argument('--output', required=True, type=Path, help='New output directory; parent must exist')
        parser.add_argument('--font', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/fonts/NanumGothic-Regular.ttf')
        args = parser.parse_args()
        result = render(args.spec.resolve(), args.output.resolve(), args.font.resolve())
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except RenderError as exc:
        print(json.dumps({'status': 'error', 'code': exc.code, 'message': exc.message}, ensure_ascii=False), file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'code': 'io_error', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
