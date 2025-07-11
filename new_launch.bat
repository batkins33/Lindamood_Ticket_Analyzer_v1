@echo off
setlocal

echo [🔧] Activating environment: doctr_env
call conda activate doctr_env

echo [ℹ️] Launching analyzer...
python launch_analyzer.py

endlocal
pause
