"""Mail Sense - Translation Engine (English → Korean using Gemini API)"""
import threading
from google import genai
from model_manager import GeminiModelManager, APIQuotaExhaustedError

TRANSLATE_PROMPT = """You are a highly skilled professional translator.
Translate the following extracted OCR text into natural, highly readable Korean.
CRITICAL RULES:
1. Ignore and EXCLUDE UI noise, button texts, email UI headers (e.g., "Recipient", "+ Address book", sender names, dates), and random OCR garbage characters.
2. Translate the CORE context / message smoothly and accurately.
3. Preserve paragraph structures (line breaks) perfectly to maintain readability.
4. Output ONLY the translated Korean text. Do not provide commentary.

Text to translate:
{text}
"""

IMAGE_PROMPT = """You are a highly skilled professional translator.
Read the text within the provided image and translate it into natural, highly readable Korean.
CRITICAL RULES:
1. Ignore and EXCLUDE UI noise, button texts, email UI headers, and garbage characters.
2. Translate the CORE message accurately.
3. Preserve paragraph structures (line breaks) perfectly to maintain readability.
4. Output ONLY the translated Korean text. Do not provide commentary.
"""

class Translator:
    """English to Korean translator using Gemini API."""

    def __init__(self, api_key=None):
        from model_manager import GeminiModelManager
        self._manager = GeminiModelManager()
        if api_key:
            self._manager.set_api_key(api_key)
        self._cache = {}
        self._lock = threading.Lock()

    def set_api_key(self, api_key):
        from model_manager import GeminiModelManager
        self._manager = GeminiModelManager()
        self._manager.set_api_key(api_key)

    def translate(self, text):
        if not text or not text.strip():
            return text
            
        text = text.strip()
        with self._lock:
            if text in self._cache:
                return self._cache[text]
                
        if not self._manager.is_configured():
            return "API Key가 설정되어 있지 않아 번역 기능을 사용할 수 없습니다. (설정 ⚙️ 버튼을 눌러 지정해주세요.)"
            
        try:
            prompt = TRANSLATE_PROMPT.format(text=text[:8000])
            result = self._manager.generate_content(prompt)
            with self._lock:
                self._cache[text] = result
            return result
        except Exception as e:
            return f"❌ 번역 API 오류가 발생했습니다: {str(e)}"

    def translate_image(self, pil_image):
        if not self._manager.is_configured():
            return "API Key가 설정되어 있지 않아 번역 기능을 사용할 수 없습니다. (설정 ⚙️ 버튼을 눌러 지정해주세요.)"
            
        try:
            result = self._manager.generate_content([IMAGE_PROMPT, pil_image])
            return result
        except Exception as e:
            return f"❌ 번역 API 오류가 발생했습니다: {str(e)}"

    def clear_cache(self):
        with self._lock:
            self._cache.clear()
