import threading
from google import genai
import logging

FALLBACK_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-pro'
]

class APIQuotaExhaustedError(Exception):
    pass

class GeminiModelManager:
    """Manages Gemini API calls, handling 429 quota exhaustion with automatic model fallback."""
    
    _instance = None
    _lock_singleton = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Singleton pattern so all tools share the same client and model state
        with cls._lock_singleton:
            if cls._instance is None:
                cls._instance = super(GeminiModelManager, cls).__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        self._client = None
        self._lock = threading.Lock()
        self.current_model = FALLBACK_MODELS[0]
        self._callbacks = []

    def register_callback(self, cb):
        if cb not in self._callbacks:
            self._callbacks.append(cb)

    def _notify(self, model_name):
        for cb in self._callbacks:
            try:
                cb(model_name)
            except:
                pass

    def set_api_key(self, api_key):
        with self._lock:
            self._client = genai.Client(api_key=api_key) if api_key else None
            self.current_model = FALLBACK_MODELS[0]

    def is_configured(self):
        return bool(self._client)

    def generate_content(self, contents):
        """Returns tuple: (generated_text, used_model_name). Raises exceptions on failure."""
        if not self._client:
            raise ValueError("API Key가 설정되어 있지 않습니다.")

        # Always try to use the absolute best model first, as quotas reset efficiently (rolling window).
        for idx in range(len(FALLBACK_MODELS)):
            model_name = FALLBACK_MODELS[idx]
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                if not response.text:
                    raise Exception("응답 텍스트가 비어있습니다.")
                    
                with self._lock:
                    if self.current_model != model_name:
                        self.current_model = model_name
                        self._notify(model_name)
                return response.text
                
            except Exception as e:
                err_str = str(e)
                if '429' in err_str or 'exhausted' in err_str.lower():
                    logging.warning(f"Model {model_name} quota exhausted. Falling back to next model...")
                    continue # Try the next model
                else:
                    raise e # If it's a 400 or other failure, stop.

        # If it finished the loop without returning, all models exhausted their 429 quota.
        raise APIQuotaExhaustedError("❌ 모든 모델의 이용 한도(Rolling Window)가 체증되었습니다. 각 모델의 토큰은 사용 1분 후 순차적으로 복귀됩니다. 잠시 후 시도해주세요.")
