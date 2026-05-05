@echo off
title Quick Start - Offline LLM Outreach Demo
color 0B

echo.
echo ⚡ QUICK START - Offline LLM Cold Outreach Engine
echo.
echo This assumes Ollama is already running and LLaMA 3 is installed.
echo.

REM Activate venv and start demo directly
call venv\Scripts\activate.bat
echo 🚀 Starting demo server...
echo.
echo 📍 Open: http://localhost:8000
echo.
python run_demo.py