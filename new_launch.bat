@echo off
setlocal

where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Conda not found. Ensure dependencies are installed.
    echo Run "pip install -r requirements.txt" if you do not use Conda.
) else (
    echo [🔧] Activating environment: doctr_env
    call conda activate doctr_env
)

echo [ℹ️] Launching analyzer...
python launch_analyzer.py

endlocal
pause
