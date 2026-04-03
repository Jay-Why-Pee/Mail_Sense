"""Mail Sense - AI Spell Checker (Abracadabra)"""
from model_manager import GeminiModelManager, APIQuotaExhaustedError

SPELLCHECK_PROMPT = """You are a professional editor and proofreader.
Analyze the provided text/image and identify all spelling mistakes, grammatical errors, awkward spacing, and poor sentence structures (in either Korean or English).
Provide a structured correction guide in Markdown format.

CRITICAL RULES:
1. Focus only on actual errors. Ignore UI text (like "Recipient To:", dates, button names).
2. Output your response formatted as a clear Markdown table if there are specific words corrected, followed by a full corrected text.
3. Use the exact format below.

Output Format:
## 맞춤법/문법 교정

| 잘못된 표현 | 올바른 표현 | 교정 사유 |
|---|---|---|
| (원본) | (수정) | (이유) |

### 📝 교정된 전체 문장
(수정된 자연스러운 전체 텍스트)

If there are no errors at all, return:
"## 맞춤법/문법 교정\n\n✨ 발견된 맞춤법이나 문법 오류가 없습니다. 완벽한 문장입니다!"
"""

class SpellChecker:
    """Spellchecker engine using GeminiModelManager API."""

    def __init__(self, api_key=''):
        self._manager = GeminiModelManager()
        if api_key:
            self._manager.set_api_key(api_key)

    def set_api_key(self, api_key):
        self._manager.set_api_key(api_key)

    def spellcheck_image(self, pil_image):
        if not self._manager.is_configured():
            return "API Key가 설정되어 있지 않아 텍스트 교정 기능을 사용할 수 없습니다. (설정 ⚙️ 버튼을 눌러 지정해주세요.)"
            
        try:
            result = self._manager.generate_content([SPELLCHECK_PROMPT, pil_image])
            return result
        except APIQuotaExhaustedError as e:
            return f"❌ {str(e)}"
        except ValueError as e:
            return f"❌ 인증 오류: {str(e)}"
        except Exception as e:
            return f"❌ 텍스트 교정 오류가 발생했습니다: {str(e)}"
