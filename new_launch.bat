@echo off
setlocal

echo [🔧] Activating environment: analyzer_env
call conda activate analyzer_env

echo [🔍] Checking environment integrity...
python test_env_integrity.py > env_check.log

findstr /C:"❌" env_check.log > nul
if %errorlevel%==0 (
    echo [❌] Environment check failed. Please fix issues in env_check.log
    pause
    exit /b 1
)

echo [✅] Environment looks good. Launching analyzer...
python launch_analyzer.py

endlocal
pause
