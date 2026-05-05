@echo off
title Offline LLM Cold Outreach Engine - Startup
color 0A

echo.
echo ========================================================
echo    🚀 OFFLINE LLM COLD OUTREACH ENGINE - STARTUP
echo ========================================================
echo.
echo 📋 Starting all required services...
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Ollama not found in PATH
    echo Please install Ollama first: https://ollama.ai
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo 📚 Installing/updating dependencies...
pip install -q fastapi uvicorn pydantic jinja2 aiofiles python-multipart requests

REM Start Ollama in background
echo 🤖 Starting Ollama server...
start /B ollama serve
timeout /t 3 /nobreak >nul

REM Wait for Ollama to be ready
echo ⏳ Waiting for Ollama to initialize...
:wait_ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    timeout /t 2 /nobreak >nul
    goto wait_ollama
)

echo ✅ Ollama is ready!

REM Check if LLaMA model exists
echo 🔍 Checking for LLaMA 3 model...
ollama list | findstr "llama3" >nul
if %ERRORLEVEL% NEQ 0 (
    echo 📥 LLaMA 3 not found. Downloading... (this may take a while)
    ollama pull llama3
)

echo.
echo ========================================================
echo    🎯 STARTING DEMO SERVER
echo ========================================================
echo.
echo 📍 Demo will be available at: http://localhost:8000
echo 🔒 Privacy-First: All processing happens locally
echo 🤖 AI-Powered: Real LLaMA 3 generation
echo 📱 Multi-Channel: 5 platforms simultaneously
echo.
echo Press Ctrl+C to stop the demo
echo.

REM Start the demo
echo 🎯 Starting demo with live logs...
echo ========================================================
echo   LIVE DEMO LOGS (Ollama generation activity below)
echo ========================================================
python run_demo.py

REM Cleanup on exit
echo.
echo 🛑 Shutting down services...
taskkill /F /IM ollama.exe >nul 2>&1
echo ✅ Demo stopped. Thanks for trying our solution!
pause