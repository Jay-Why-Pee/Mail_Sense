@echo off
chcp 65001 >nul
echo ========================================
echo   Mail Sense - 환경 설정
echo ========================================
echo.

python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    echo Python 3.10 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] Python 패키지 설치 중...
pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [ERROR] 패키지 설치 실패
    pause
    exit /b 1
)

echo.
echo [2/2] Tesseract OCR 확인 중...
where tesseract 2>nul
if errorlevel 1 (
    if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo Tesseract OCR: OK
    ) else (
        echo.
        echo [WARNING] Tesseract OCR가 설치되어 있지 않습니다.
        echo 다음 링크에서 설치해주세요:
        echo https://github.com/UB-Mannheim/tesseract/wiki
        echo.
        echo 설치 시 "Additional language data"에서 "Korean"을 선택해주세요.
    )
) else (
    echo Tesseract OCR: OK
)

echo.
echo ========================================
echo   설치 완료! mail_sense.pyw를 더블클릭하여 실행하세요.
echo ========================================
pause
