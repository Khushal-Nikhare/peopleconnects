@echo off
echo =====================================
echo  PeopleConnects - Social Media App
echo =====================================
echo.
echo Starting the application...
echo.
python -m uvicorn backend.main:app --reload --port 8000
