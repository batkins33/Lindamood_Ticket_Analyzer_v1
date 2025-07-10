@echo off
setlocal

echo [🔧] Activating environment: analyzer_env
call conda activate analyzer_env

echo [ℹ️] Launching analyzer...
python launch_analyzer.py

endlocal
pause
