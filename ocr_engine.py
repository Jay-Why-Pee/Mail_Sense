"""Mail Sense - OCR Engine (text extraction with bounding boxes)"""
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance


class OCREngine:
    """Extracts text and bounding boxes from images using Tesseract."""

    def __init__(self, tesseract_path='', confidence=40):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self._conf = confidence

    def extract_text(self, image):
        try:
            img = self._preprocess(image)
            return pytesseract.image_to_string(img, lang='eng+kor').strip()
        except Exception as e:
            return f"[OCR Error: {e}]"

    def extract_with_boxes(self, image):
        try:
            img = self._preprocess(image)
            data = pytesseract.image_to_data(img, lang='eng+kor', output_type=pytesseract.Output.DICT)
            return self._group_lines(data)
        except Exception:
            return []

    def _preprocess(self, image):
        img = image.convert('RGB') if image.mode != 'RGB' else image.copy()
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = img.filter(ImageFilter.SHARPEN)
        return img

    def _group_lines(self, data):
        lines = {}
        for i in range(len(data['text'])):
            txt = data['text'][i].strip()
            conf = int(data['conf'][i]) if str(data['conf'][i]) != '-1' else 0
            if not txt or conf < self._conf:
                continue

            key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
            if key not in lines:
                lines[key] = {
                    'text': '', 'words': [],
                    'left': data['left'][i], 'top': data['top'][i],
                    'right': data['left'][i] + data['width'][i],
                    'bottom': data['top'][i] + data['height'][i],
                }

            ln = lines[key]
            ln['text'] = (ln['text'] + ' ' + txt).strip()
            ln['words'].append({
                'text': txt, 'left': data['left'][i], 'top': data['top'][i],
                'width': data['width'][i], 'height': data['height'][i],
            })
            ln['left'] = min(ln['left'], data['left'][i])
            ln['top'] = min(ln['top'], data['top'][i])
            ln['right'] = max(ln['right'], data['left'][i] + data['width'][i])
            ln['bottom'] = max(ln['bottom'], data['top'][i] + data['height'][i])

        result = []
        for key in sorted(lines.keys()):
            ln = lines[key]
            ln['width'] = ln['right'] - ln['left']
            ln['height'] = ln['bottom'] - ln['top']
            ln['is_english'] = self._is_english(ln['text'])
            result.append(ln)
        return result

    @staticmethod
    def _is_english(text):
        if not text:
            return False
        alpha = [c for c in text if c.isalpha()]
        if not alpha:
            return False
        ascii_alpha = sum(1 for c in alpha if c.isascii())
        return (ascii_alpha / len(alpha)) > 0.5
