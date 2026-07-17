@echo off
cd /d "%~dp0backend"
set DB_TYPE=sqlite
echo [??] ??API??...
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

timeout /t 3 >nul

cd /d "%~dp0frontend"
echo [??] ???????...
start /B npm run dev

echo.
echo ====================================
echo   ??????????!
echo   ??: http://localhost:3000
echo   ??: http://localhost:8000
echo   ?????: 37108220071109031X / Zyw20071109
echo ====================================
echo.
echo ??????????...
pause >nul

taskkill /f /fi "WINDOWTITLE eq uvicorn*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq npm*" >nul 2>&1
echo ?????
