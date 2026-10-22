@echo off
echo ========================================================
echo  Starting Smart Wealth Tracker and Budget Planner
echo ========================================================
cd /d "%~dp0wealth_tracker\wealthtracker"
call "..\venv\Scripts\activate.bat"
echo Virtual environment activated.
echo Server running at http://127.0.0.1:8000/
echo Press CTRL+C to stop the server.
echo.
python manage.py runserver 127.0.0.1:8000
pause
