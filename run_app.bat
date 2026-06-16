@echo off
setlocal

cd /d "%~dp0"

if exist "runtime\python\python.exe" (
  set "PYTHON_EXE=%~dp0runtime\python\python.exe"
) else (
  set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

if not exist "%PYTHON_EXE%" (
  echo [AI News Dashboard] Creating local Python environment...
  py -3.12 -m venv .venv
  if errorlevel 1 (
    py -3 -m venv .venv
  )
  set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

if not exist "%PYTHON_EXE%" (
  echo [AI News Dashboard] Python was not found. Install Python 3.10+ or copy runtime\python.
  pause
  exit /b 1
)

"%PYTHON_EXE%" -c "import streamlit, feedparser" >nul 2>nul
if errorlevel 1 (
  echo [AI News Dashboard] Installing dependencies...
  "%PYTHON_EXE%" -m pip install --upgrade pip
  "%PYTHON_EXE%" -m pip install -r requirements.txt
)

if not exist "data" mkdir "data"
set APP_DATA_DIR=%~dp0data

echo [AI News Dashboard] Starting app...
"%PYTHON_EXE%" -m streamlit run app.py --server.port 8501

endlocal
