"""Mail Sense - Configuration Management"""
import json
import os
import sys
import shutil


def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_FILE = os.path.join(get_app_dir(), 'config.json')

DEFAULT_CONFIG = {
    'gemini_api_key': '',
    'tesseract_path': '',
    'capture_interval_ms': 200,
    'similarity_threshold': 0.95,
    'stable_duration_sec': 3.0,
    'translation_font_name': 'Malgun Gothic',
    'ocr_confidence_threshold': 40,
    'window_width': 1400,
    'window_height': 850,
}


def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass
    if not config['tesseract_path']:
        config['tesseract_path'] = find_tesseract()
    return config


def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError:
        pass


def find_tesseract():
    username = os.getenv('USERNAME', '')
    paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        rf'C:\Users\{username}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    result = shutil.which('tesseract')
    return result if result else ''
