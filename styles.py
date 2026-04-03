"""Mail Sense - Apple Dark Mode Styles"""

MAIN_STYLE = """
QMainWindow { background-color: #1C1C1E; color: #FFFFFF; font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; }
QWidget { color: #FFFFFF; font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; }
QWidget#centralWidget { background-color: #1C1C1E; }
QWidget#toolbarWidget { background-color: #2C2C2E; border-radius: 16px; margin: 12px 16px 4px 16px; padding: 12px 20px; }

QPushButton#btnRegionSelect {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7B2FBE, stop:0.5 #9B59B6, stop:1 #BF5AF2);
    color: #FFFFFF; border: none; border-radius: 12px; padding: 12px 24px; font-size: 14px; font-weight: 600;
}
QPushButton#btnRegionSelect:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E44AD, stop:0.5 #A569BD, stop:1 #D2B4DE);
}
QPushButton#btnRegionSelect:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C3483, stop:0.5 #7D3C98, stop:1 #9B59B6);
}
QPushButton#btnRegionSelect:disabled { background: #3A3A3C; color: #636366; }

QPushButton#btnSummarize {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #D35400, stop:0.5 #E67E22, stop:1 #FF9F0A);
    color: #FFFFFF; border: none; border-radius: 12px; padding: 12px 24px; font-size: 14px; font-weight: 600;
}
QPushButton#btnSummarize:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E67E22, stop:0.5 #F39C12, stop:1 #FFB84D);
}
QPushButton#btnSummarize:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #BA4A00, stop:0.5 #D35400, stop:1 #E67E22);
}
QPushButton#btnSummarize:disabled { background: #3A3A3C; color: #636366; }

QPushButton#btnTranslate {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0077B6, stop:0.5 #00B4D8, stop:1 #64D2FF);
    color: #FFFFFF; border: none; border-radius: 12px; padding: 12px 24px; font-size: 14px; font-weight: 600;
}
QPushButton#btnTranslate:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00B4D8, stop:0.5 #48CAE4, stop:1 #90E0EF);
}
QPushButton#btnTranslate:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #005F8F, stop:0.5 #0077B6, stop:1 #00B4D8);
}
QPushButton#btnTranslate:disabled { background: #3A3A3C; color: #636366; }

QPushButton#btnTranslateActive {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1B4332, stop:0.5 #2D6A4F, stop:1 #30D158);
    color: #FFFFFF; border: none; border-radius: 12px; padding: 12px 24px; font-size: 14px; font-weight: 600;
}
QPushButton#btnTranslateActive:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2D6A4F, stop:0.5 #40916C, stop:1 #52B788);
}

QPushButton#btnSpellcheck {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #AF52DE, stop:0.5 #C644FC, stop:1 #E089FC);
    color: #FFFFFF; border: none; border-radius: 12px; padding: 12px 24px; font-size: 14px; font-weight: 600;
}
QPushButton#btnSpellcheck:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #C644FC, stop:0.5 #D96CFD, stop:1 #F0A5FD);
}
QPushButton#btnSpellcheck:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E3BB9, stop:0.5 #AF52DE, stop:1 #C644FC);
}
QPushButton#btnSpellcheck:disabled { background: #3A3A3C; color: #636366; }

QFrame#mirrorPanel, QFrame#summaryPanel {
    background-color: #2C2C2E; border-radius: 16px; border: 1px solid #38383A;
}
QLabel#panelHeader {
    color: #8E8E93; font-size: 12px; font-weight: 600; padding: 16px 20px 8px 20px;
}
QLabel#mirrorView {
    background-color: #1C1C1E; border-radius: 12px; margin: 4px 16px 16px 16px; padding: 8px;
}
QTextBrowser#summaryView {
    background-color: #1C1C1E; color: #FFFFFF; border: none; border-radius: 12px;
    margin: 4px 16px 16px 16px; padding: 16px; font-size: 14px; selection-background-color: #0A84FF;
}
QScrollBar:vertical {
    background: transparent; width: 8px; margin: 4px 2px; border-radius: 4px;
}
QScrollBar::handle:vertical { background-color: #48484A; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background-color: #636366; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QStatusBar { background-color: #2C2C2E; color: #8E8E93; font-size: 12px; border-top: 1px solid #38383A; }
QStatusBar QLabel { color: #8E8E93; }
QSplitter::handle { background-color: #38383A; width: 2px; margin: 16px 0; border-radius: 1px; }
QSplitter::handle:hover { background-color: #0A84FF; }
QDialog { background-color: #2C2C2E; }
QLineEdit {
    background-color: #3A3A3C; color: #FFFFFF; border: 1px solid #48484A;
    border-radius: 8px; padding: 10px 16px; font-size: 14px;
}
QLineEdit:focus { border-color: #0A84FF; }
QToolTip { background-color: #3A3A3C; color: #FFFFFF; border: 1px solid #48484A; border-radius: 8px; padding: 8px; }
"""

SUMMARY_CSS = """
body { color: #FFFFFF; font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; font-size: 14px; line-height: 1.7; }
h1 { color: #FFFFFF; font-size: 22px; border-bottom: 1px solid #38383A; padding-bottom: 8px; }
h2 { color: #E5E5EA; font-size: 18px; margin-top: 20px; }
h3 { color: #C7C7CC; font-size: 16px; }
p { color: #E5E5EA; margin: 8px 0; }
ul, ol { padding-left: 24px; }
li { color: #E5E5EA; margin: 4px 0; }
strong { color: #0A84FF; }
em { color: #BF5AF2; }
code { background: #3A3A3C; color: #FF9F0A; padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; }
pre { background: #3A3A3C; padding: 16px; border-radius: 8px; }
blockquote { border-left: 3px solid #0A84FF; padding: 8px 16px; background: rgba(10,132,255,0.1); border-radius: 0 8px 8px 0; }
table { border-collapse: collapse; width: 100%; }
th { background: #3A3A3C; padding: 10px; border: 1px solid #48484A; }
td { padding: 8px; border: 1px solid #38383A; }
"""

PLACEHOLDER_HTML = """
<div style="display:flex; align-items:center; justify-content:center; height:100%; text-align:center; color:#636366;">
    <div>
        <p style="font-size: 48px; margin-bottom: 16px;">✨</p>
        <p style="font-size: 16px; font-weight: 600; color: #8E8E93;">영역을 선택해주세요</p>
        <p style="font-size: 13px; color: #636366; margin-top: 8px;">
            "윙가르디움 레비오우사" 버튼을 클릭하여<br>화면 영역을 선택하세요
        </p>
    </div>
</div>
"""

SUMMARY_PLACEHOLDER = """
<div style="display:flex; align-items:center; justify-content:center; height:100%; text-align:center;">
    <div>
        <p style="font-size: 48px; margin-bottom: 16px;">📋</p>
        <p style="font-size: 16px; font-weight: 600; color: #8E8E93;">요약 결과</p>
        <p style="font-size: 13px; color: #636366; margin-top: 8px;">
            "아수라발발타" 버튼을 클릭하면<br>선택 영역의 텍스트가 요약됩니다
        </p>
    </div>
</div>
"""
