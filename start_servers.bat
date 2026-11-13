@echo off
title QR Sentinel - Platform Launcher
echo ============================================================
echo Starting QR Sentinel - AI QR Threat Detection Platform
echo ============================================================
echo.

echo [1/2] Starting Backend (FastAPI on http://127.0.0.1:8000)...
start "QR Sentinel - Backend" cmd /k "title Backend && call .\venv\Scripts\activate.bat && python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Frontend (Vite on http://127.0.0.1:5173)...
start "QR Sentinel - Frontend" cmd /k "title Frontend && cd frontend && npm run dev -- --host 0.0.0.0 --port 5173"

echo.
echo ============================================================
echo QR Sentinel is starting!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://localhost:8000/api/docs
echo ============================================================
