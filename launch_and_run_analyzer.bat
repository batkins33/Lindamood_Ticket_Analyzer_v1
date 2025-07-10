@echo off
echo =============================================
echo [Modular Analyzer Launcher]
echo ---------------------------------------------
echo Activating Conda environment...
echo =============================================

REM Full path to your Conda activate script
call U:\Dev\envs\doctr_env\Scripts\activate.bat

REM Optional: limit PATH to avoid DLL conflict
set PATH=U:\Dev\envs\doctr_env\Library\bin;U:\Dev\envs\doctr_env\Scripts;C:\Windows\System32;C:\Windows

REM Change directory to the project root
cd /d U:\Dev\projects\analyzer_projects\Lindamood_Ticket_Analyzer_v1

echo.
echo [INFO] Launching Modular Analyzer...
python launch_analyzer.py

echo.
echo [DONE] Press any key to exit.
pause >nul
