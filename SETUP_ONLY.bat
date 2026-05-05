@echo off
title Setup Only - Install Dependencies
color 0E

echo.
echo 🔧 SETUP ONLY - Installing Dependencies
echo.

REM Create venv if needed
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate and install
call venv\Scripts\activate.bat
echo 📚 Installing dependencies...
pip install fastapi uvicorn pydantic jinja2 aiofiles python-multipart requests

echo.
echo ✅ Setup complete! 
echo.
echo Next steps:
echo 1. Make sure Ollama is installed: https://ollama.ai
echo 2. Run: ollama pull llama3
echo 3. Double-click START_DEMO.bat
echo.
pause