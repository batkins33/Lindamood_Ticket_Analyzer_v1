@echo off
setlocal EnableDelayedExpansion

:: --- Modular Analyzer Launcher ---
echo =============================================
echo [Modular Analyzer Launcher]
echo ---------------------------------------------
echo Current directory: %cd%
echo Activating Conda environment...
echo =============================================

REM Update this line if your Conda install path is different
CALL "C:\Users\brian.atkins\anaconda3\Scripts\activate.bat" analyzer_env

REM Change to the project directory
cd /d "U:\Dev\projects\analyzer_projects\Lindamood_Ticket_Analyzer_v1"

echo Checking required packages...
python -c "import numpy, pandas" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Missing required packages. Installing...
    pip install -r requirements.txt
)

echo.
echo [INFO] Launching Modular Analyzer...
python launch_analyzer.py

echo.
echo [DONE] Press any key to exit.
pause >nul
