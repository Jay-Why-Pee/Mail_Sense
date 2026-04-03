"""
Mail Sense - 화면 텍스트 요약, 번역 & 교정 도구
더블클릭으로 실행하세요.
"""
import sys
import os

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QFrame, QLabel, QPushButton, QTextBrowser, QStatusBar,
        QDialog, QLineEdit, QDialogButtonBox, QMessageBox
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMetaObject, Q_ARG
    from PyQt6.QtGui import QPixmap, QImage, QFont
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Setup Required", "필요한 패키지가 설치되지 않았습니다.\nsetup.bat를 먼저 실행해주세요.")
    root.destroy()
    sys.exit(1)

import markdown
from PIL import Image

from config import load_config, save_config
from styles import MAIN_STYLE, SUMMARY_CSS, PLACEHOLDER_HTML, SUMMARY_PLACEHOLDER
from region_selector import RegionSelector
from screen_mirror import ScreenMirror
from ocr_engine import OCREngine
from translator import Translator
from summarizer import Summarizer
from spellchecker import SpellChecker
from model_manager import GeminiModelManager
from overlay_renderer import OverlayRenderer


# ── Worker Threads ──────────────────────────────────────────────

class SummarizeWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, summarizer, text):
        super().__init__()
        self.summarizer = summarizer
        self.text = text

    def run(self):
        result = self.summarizer.summarize(self.text)
        self.finished.emit(result)


class TranslateWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, image, ocr_engine, translator_engine):
        super().__init__()
        self.image = image
        self.ocr = ocr_engine
        self.trans = translator_engine

    def run(self):
        translated = self.trans.translate_image(self.image)
        if not translated.strip():
            self.finished.emit("<p style='color:#8E8E93;'>텍스트를 찾을 수 없습니다.</p>")
            return
            
        translated = translated.replace('\r', '')
        paragraphs = translated.split('\n\n')
        html_blocks = []
        for p in paragraphs:
            if not p.strip(): continue
            p_html = p.replace('\n', '<br>')
            html_blocks.append(f"<p style='margin-bottom: 12px; font-size:15px; line-height:1.7; word-break:keep-all; color:#E5E5EA;'>{p_html}</p>")
            
        result_html = f"<div>{''.join(html_blocks)}</div>"
        self.finished.emit(result_html)


class SpellcheckWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, image, spellchecker):
        super().__init__()
        self.image = image
        self.spellchecker = spellchecker

    def run(self):
        result = self.spellchecker.spellcheck_image(self.image)
        if not result.strip():
            self.finished.emit("<p style='color:#8E8E93;'>텍스트를 찾을 수 없습니다.</p>")
            return
            
        html = markdown.markdown(result, extensions=['tables', 'fenced_code'])
        self.finished.emit(html)


# ── API Key Dialog ──────────────────────────────────────────────

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None, current_key=''):
        super().__init__(parent)
        self.setWindowTitle("Gemini API Key 설정")
        self.setFixedSize(500, 200)
        self.setStyleSheet("""
            QDialog { background-color: #2C2C2E; }
            QLabel { color: #FFFFFF; font-size: 14px; }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        lbl = QLabel("Google Gemini API Key를 입력해주세요:")
        layout.addWidget(lbl)

        sub = QLabel("※ 없으면 비워두세요. 요약은 원문 표시로 대체됩니다.")
        sub.setStyleSheet("color: #8E8E93; font-size: 12px;")
        layout.addWidget(sub)

        self.input = QLineEdit(current_key)
        self.input.setPlaceholderText("AIza...")
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF; color: white; border: none;
                border-radius: 8px; padding: 8px 20px; font-size: 13px;
            }
            QPushButton:hover { background-color: #409CFF; }
        """)
        layout.addWidget(buttons)

    def get_key(self):
        return self.input.text().strip()


# ── Main Window ─────────────────────────────────────────────────

class MailSenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = load_config()
        self._init_engines()
        self._current_frame = None
        self._translate_worker = None
        self._summarize_worker = None
        self._spellcheck_worker = None
        self._region_selector = None
        self._setup_ui()
        self._check_first_run()

    def _init_engines(self):
        cfg = self._config
        self._mirror = ScreenMirror(
            interval_ms=cfg.get('capture_interval_ms', 200),
            threshold=cfg.get('similarity_threshold', 0.95),
            stable_sec=0.5
        )
        self._ocr = OCREngine(cfg.get('tesseract_path', ''), cfg.get('ocr_confidence_threshold', 50))
        
        # Init tools
        api_key = cfg.get('gemini_api_key', '')
        self._translator = Translator(api_key)
        self._summarizer = Summarizer(api_key)
        self._spellchecker = SpellChecker(api_key)
        
        # Register for model fallback UI updates
        GeminiModelManager().register_callback(self._on_model_changed)
        
        self._overlay = OverlayRenderer(cfg.get('translation_font_name', 'Arial'))
        
        self._mirror.frame_captured.connect(self._on_frame)

    def _setup_ui(self):
        self.setWindowTitle("Mail Sense")
        cfg = self._config
        self.resize(cfg.get('window_width', 1200), cfg.get('window_height', 800))
        self.setMinimumSize(900, 600)
        self.setStyleSheet(MAIN_STYLE)

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setSpacing(8)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # ── Toolbar ──
        toolbar = QWidget()
        toolbar.setObjectName("toolbarWidget")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 8, 20, 8)
        tb_layout.setSpacing(12)

        title = QLabel("✦ Mail Sense")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF; padding-right: 16px;")
        tb_layout.addWidget(title)
        
        # Dynamic active AI model label
        self._model_label = QLabel(f"🤖  AI Model: {GeminiModelManager().current_model}")
        self._model_label.setStyleSheet("color: #8E8E93; font-size: 13px; font-weight: bold;")
        tb_layout.addWidget(self._model_label)
        
        tb_layout.addStretch()

        self.btn_region = QPushButton("✨ 윙가르디움 레비오우사\n(화면 영역 캡처)")
        self.btn_region.setObjectName("btnRegionSelect")
        self.btn_region.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_region.setToolTip("화면 캡처 영역을 지정합니다.")
        self.btn_region.clicked.connect(self._on_select_region)
        tb_layout.addWidget(self.btn_region)

        self.btn_summarize = QPushButton("🔮 아수라발발타\n(내용 핵심 요약)")
        self.btn_summarize.setObjectName("btnSummarize")
        self.btn_summarize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_summarize.setToolTip("캡처 영역의 내용을 자동으로 요약합니다.")
        self.btn_summarize.setEnabled(False)
        self.btn_summarize.clicked.connect(self._on_summarize)
        tb_layout.addWidget(self.btn_summarize)

        self.btn_translate = QPushButton("💡 루모스\n(이미지 전문 번역)")
        self.btn_translate.setObjectName("btnTranslate")
        self.btn_translate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_translate.setToolTip("캡처 영역 내용을 형태를 유지하며 전문 번역합니다.")
        self.btn_translate.setEnabled(False)
        self.btn_translate.clicked.connect(self._on_translate_once)
        tb_layout.addWidget(self.btn_translate)

        self.btn_spellcheck = QPushButton("🪄 아브라카다브라\n(맞춤법/문법 교정)")
        self.btn_spellcheck.setObjectName("btnSpellcheck")
        self.btn_spellcheck.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_spellcheck.setToolTip("한글/영문 맞춤법과 띄어쓰기를 검사하고 교정합니다.")
        self.btn_spellcheck.setEnabled(False)
        self.btn_spellcheck.clicked.connect(self._on_spellcheck)
        tb_layout.addWidget(self.btn_spellcheck)

        # Settings button
        btn_settings = QPushButton("⚙")
        btn_settings.setStyleSheet("""
            QPushButton { background: transparent; color: #8E8E93; border: none;
                         font-size: 18px; border-radius: 8px; padding: 12px; }
            QPushButton:hover { background: #3A3A3C; color: #FFFFFF; }
        """)
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setToolTip("API Key 설정")
        btn_settings.clicked.connect(self._on_settings)
        tb_layout.addWidget(btn_settings)

        root_layout.addWidget(toolbar)

        # ── Content (Splitter) ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)

        # Left: Mirror panel
        mirror_frame = QFrame()
        mirror_frame.setObjectName("mirrorPanel")
        ml = QVBoxLayout(mirror_frame)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        mirror_hdr = QLabel("📺  SCREEN MIRROR")
        mirror_hdr.setObjectName("panelHeader")
        ml.addWidget(mirror_hdr)

        self.mirror_view = QLabel()
        self.mirror_view.setObjectName("mirrorView")
        self.mirror_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mirror_view.setMinimumSize(300, 200)
        self.mirror_view.setScaledContents(False)
        self.mirror_view.setTextFormat(Qt.TextFormat.RichText)
        self.mirror_view.setText(PLACEHOLDER_HTML)
        ml.addWidget(self.mirror_view, 1)
        splitter.addWidget(mirror_frame)

        # Right: Summary panel
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryPanel")
        sl = QVBoxLayout(summary_frame)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)

        summary_hdr = QLabel("📋  SUMMARY & TRANSLATION")
        summary_hdr.setObjectName("panelHeader")
        sl.addWidget(summary_hdr)

        self.summary_view = QTextBrowser()
        self.summary_view.setObjectName("summaryView")
        self.summary_view.setOpenExternalLinks(True)
        self.summary_view.setHtml(f"<style>{SUMMARY_CSS}</style>{SUMMARY_PLACEHOLDER}")
        sl.addWidget(self.summary_view, 1)
        splitter.addWidget(summary_frame)

        splitter.setSizes([700, 500])
        root_layout.addWidget(splitter, 1)

        # ── Status Bar ──
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._status_label = QLabel("● Ready")
        self._status_label.setStyleSheet("color: #30D158; font-weight: 600;")
        self.status.addWidget(self._status_label)

    def _check_first_run(self):
        if not self._config.get('gemini_api_key'):
            self._set_status("API Key를 설정하면 AI 기능을 사용할 수 있습니다", "#FF9F0A")
        if not self._config.get('tesseract_path'):
            self._set_status("⚠ Tesseract OCR가 감지되지 않았습니다. 설치 후 재시작해주세요.", "#FF453A")

    # ── Callbacks ─────────────────────────────────────────────────

    def _on_model_changed(self, model_name):
        # Update UI label safely from any background thread
        QMetaObject.invokeMethod(self._model_label, "setText", Qt.ConnectionType.QueuedConnection, Q_ARG(str, f"🤖  AI Model: {model_name}"))

    # ── Actions ─────────────────────────────────────────────────

    def _on_select_region(self):
        self._set_status("영역을 선택해주세요...", "#0A84FF")
        self._mirror.stop()
        self.hide()
        self._region_selector = RegionSelector()
        self._region_selector.region_selected.connect(self._on_region_selected)
        self._region_selector.selection_cancelled.connect(self._on_region_cancelled)
        self._region_selector.show()

    def _on_region_selected(self, x, y, w, h):
        self.show()
        self.activateWindow()
        self._mirror.set_region(x, y, w, h)
        self._mirror.start()
        self.btn_summarize.setEnabled(True)
        self.btn_translate.setEnabled(True)
        self.btn_spellcheck.setEnabled(True)
        self._set_status(f"영역 선택됨: ({x}, {y}) {w}×{h}", "#30D158")

    def _on_region_cancelled(self):
        self.show()
        self.activateWindow()
        self._set_status("영역 선택 취소됨", "#8E8E93")

    def _on_frame(self, pil_image):
        self._current_frame = pil_image
        self._display_image(pil_image)

    def _on_summarize(self):
        if not self._current_frame:
            return
        self._set_status("텍스트 추출 및 요약 중...", "#FF9F0A")
        self.btn_summarize.setEnabled(False)
        text = self._ocr.extract_text(self._current_frame)
        if not text.strip():
            self.btn_summarize.setEnabled(True)
            self._set_status("텍스트를 추출할 수 없습니다", "#FF453A")
            return
        self._summarize_worker = SummarizeWorker(self._summarizer, text)
        self._summarize_worker.finished.connect(self._on_summary_done)
        self._summarize_worker.start()

    def _on_summary_done(self, md_text):
        html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
        self.summary_view.setHtml(f"<style>{SUMMARY_CSS}</style><h2 style='color:#FF9F0A;'>🔮 요약 결과</h2><br>{html}")
        self.btn_summarize.setEnabled(True)
        self._set_status("요약 완료!", "#30D158")

    def _on_translate_once(self):
        if not self._current_frame:
            return
        if self._translate_worker and self._translate_worker.isRunning():
            return
        
        self._set_status("단일 전문 번역 중...", "#64D2FF")
        self.btn_translate.setEnabled(False)
        self._translate_worker = TranslateWorker(
            self._current_frame, self._ocr, self._translator
        )
        self._translate_worker.finished.connect(self._on_translate_done)
        self._translate_worker.start()

    def _on_translate_done(self, html_text):
        self.summary_view.setHtml(f"<style>{SUMMARY_CSS}</style><h2 style='color:#64D2FF;'>💡 번역 (Lumos)</h2><br>{html_text}")
        self.btn_translate.setEnabled(True)
        self._set_status("번역 완료!", "#30D158")
        
    def _on_spellcheck(self):
        if not self._current_frame:
            return
        if self._spellcheck_worker and self._spellcheck_worker.isRunning():
            return
            
        self._set_status("맞춤법 및 문법 검사 중...", "#AF52DE")
        self.btn_spellcheck.setEnabled(False)
        self._spellcheck_worker = SpellcheckWorker(self._current_frame, self._spellchecker)
        self._spellcheck_worker.finished.connect(self._on_spellcheck_done)
        self._spellcheck_worker.start()

    def _on_spellcheck_done(self, html_text):
        self.summary_view.setHtml(f"<style>{SUMMARY_CSS}</style><h2 style='color:#AF52DE;'>🪄 텍스트 교정 (Abracadabra)</h2><br>{html_text}")
        self.btn_spellcheck.setEnabled(True)
        self._set_status("맞춤법/문법 교정 완료!", "#30D158")

    def _on_settings(self):
        dlg = ApiKeyDialog(self, self._config.get('gemini_api_key', ''))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            key = dlg.get_key()
            self._config['gemini_api_key'] = key
            save_config(self._config)
            self._summarizer.set_api_key(key)
            self._translator.set_api_key(key)
            self._spellchecker.set_api_key(key)
            if key:
                self._set_status("API Key 설정 완료", "#30D158")
            else:
                self._set_status("API Key 없이 실행 (원문 표시 모드)", "#FF9F0A")

    # ── Helpers ──────────────────────────────────────────────────

    def _display_image(self, pil_image):
        try:
            from PIL.ImageQt import ImageQt
            qimg = ImageQt(pil_image)
            pixmap = QPixmap.fromImage(qimg)
            view_size = self.mirror_view.size()
            scaled = pixmap.scaled(
                view_size, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.mirror_view.setPixmap(scaled)
        except Exception:
            pass

    def _set_status(self, text, color="#8E8E93"):
        self._status_label.setText(f"● {text}")
        self._status_label.setStyleSheet(f"color: {color}; font-weight: 600;")

    def closeEvent(self, event):
        self._mirror.stop()
        self._config['window_width'] = self.width()
        self._config['window_height'] = self.height()
        save_config(self._config)
        super().closeEvent(event)


# ── Entry Point ─────────────────────────────────────────────────

def main():
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font = QFont('Segoe UI', 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)
    window = MailSenseApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
