"""Mail Sense - AI Summarizer (Google Gemini API - new google.genai package)"""
from google import genai
from model_manager import GeminiModelManager, APIQuotaExhaustedError


SUMMARY_PROMPT = """당신은 전문적인 텍스트 요약가입니다. 아래 텍스트를 한국어로 요약해주세요.

요약 규칙:
1. Markdown 형식으로 작성
2. 핵심 내용을 불릿 포인트로 정리
3. 중요한 키워드는 **굵게** 표시
4. 간결하지만 핵심을 놓치지 않도록 작성
5. 원문이 영어인 경우 한국어로 번역하여 요약

출력 형식:
## 요약

### 핵심 내용
- 포인트 1
- 포인트 2

### 세부 사항
- 세부 내용

---
요약할 텍스트:

{text}
"""


class Summarizer:
    """Text summarizer using Google Gemini API (google.genai)."""

    def __init__(self, api_key=''):
        from model_manager import GeminiModelManager
        self._manager = GeminiModelManager()
        if api_key:
            self._manager.set_api_key(api_key)

    def set_api_key(self, api_key):
        from model_manager import GeminiModelManager
        self._manager = GeminiModelManager()
        self._manager.set_api_key(api_key)

    def summarize(self, text):
        if not text or not text.strip():
            return "요약할 텍스트가 없습니다."
        if not self._manager.is_configured():
            return self._fallback_summary(text)
        try:
            prompt = SUMMARY_PROMPT.format(text=text[:8000])
            result = self._manager.generate_content(prompt)
            return result
        except Exception as e:
            err_msg = str(e)
            return f"## ⚠️ API 오류\n\n`{err_msg}`\n\n---\n\n" + self._fallback_summary(text)

    def is_configured(self):
        from model_manager import GeminiModelManager
        return GeminiModelManager().is_configured()

    @staticmethod
    def _fallback_summary(text):
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not lines:
            return "텍스트를 추출할 수 없습니다."
        summary = "## 📄 추출된 텍스트\n\n"
        summary += "> API 키가 설정되지 않아 원문을 표시합니다.\n\n"
        for line in lines[:30]:
            summary += f"- {line}\n"
        if len(lines) > 30:
            summary += f"\n*... 외 {len(lines) - 30}줄*\n"
        return summary
