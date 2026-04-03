"""Mail Sense - Overlay Renderer (translation overlay on mirrored image)"""
from PIL import Image, ImageDraw, ImageFont
import os


class OverlayRenderer:
    """Renders Korean translation overlay on top of captured screen images."""

    def __init__(self, font_name='Malgun Gothic', base_font_size=14):
        self._font_name = font_name
        self._base_size = base_font_size
        self._fonts = {}  # size -> font cache

    def _get_font(self, size):
        if size in self._fonts:
            return self._fonts[size]
        try:
            # Try system fonts
            for name in [self._font_name, 'malgun.ttf', 'Malgun Gothic',
                         'malgungothic', 'NanumGothic', 'gulim', 'Arial']:
                try:
                    font = ImageFont.truetype(name, size)
                    self._fonts[size] = font
                    return font
                except (OSError, IOError):
                    continue
            # Try Windows font directory
            winfonts = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
            for fname in ['malgun.ttf', 'malgunbd.ttf', 'NanumGothic.ttf', 'gulim.ttc']:
                fpath = os.path.join(winfonts, fname)
                if os.path.exists(fpath):
                    font = ImageFont.truetype(fpath, size)
                    self._fonts[size] = font
                    return font
        except Exception:
            pass
        font = ImageFont.load_default()
        self._fonts[size] = font
        return font

    def render(self, base_image, ocr_lines, translations):
        """
        Render translation overlay.

        Args:
            base_image: PIL Image (original screen capture)
            ocr_lines: list of dicts from OCR with bounding box info
            translations: dict mapping English text -> Korean translation
        Returns:
            PIL Image with overlay applied
        """
        img = base_image.copy().convert('RGBA')
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for line in ocr_lines:
            if not line.get('is_english', False):
                continue
            original = line['text']
            translated = translations.get(original, '')
            if not translated or translated == original:
                continue

            x, y = line['left'], line['top']
            w, h = line['width'], line['height']

            # Draw white background over English text
            padding = 2
            draw.rectangle(
                [x - padding, y - padding, x + w + padding, y + h + padding],
                fill=(255, 255, 255, 240)
            )

            # Calculate font size to fit within bounding box
            font_size = max(10, min(h - 2, self._base_size))
            font = self._get_font(font_size)

            # Auto-shrink if text is too wide
            bbox = draw.textbbox((0, 0), translated, font=font)
            text_w = bbox[2] - bbox[0]
            while text_w > w + 20 and font_size > 8:
                font_size -= 1
                font = self._get_font(font_size)
                bbox = draw.textbbox((0, 0), translated, font=font)
                text_w = bbox[2] - bbox[0]

            # Center vertically
            text_h = bbox[3] - bbox[1]
            ty = y + (h - text_h) // 2

            # Draw Korean text
            draw.text((x, ty), translated, fill=(0, 0, 0, 255), font=font)

        result = Image.alpha_composite(img, overlay)
        return result.convert('RGB')
