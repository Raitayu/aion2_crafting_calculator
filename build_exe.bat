@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 ( set PYCMD=py -3 ) else ( set PYCMD=python )
%PYCMD% -m venv .venv || goto :fail
.venv\Scripts\python -m pip install pyinstaller || goto :fail
.venv\Scripts\python -m PyInstaller --noconfirm --clean --onedir --name AION2CraftPlanner --add-data "calculator.html;." local_planner.py || goto :fail
echo.
echo Done. Zip the folder dist\AION2CraftPlanner for a release.
pause
exit /b 0
:fail
echo Build failed - see messages above.
pause
exit /b 1
