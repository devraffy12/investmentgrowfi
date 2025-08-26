@echo off
REM Daily Investment Processor for GrowFi
REM Run this script daily to process payouts and update investments

echo.
echo ===============================================
echo GrowFi Daily Investment Processor
echo ===============================================
echo.

cd /d "C:\Users\raffy\OneDrive\Desktop\investment"

echo Activating virtual environment...
call dbonline\Scripts\activate.bat

echo.
echo Running daily investment processing...
python daily_processor.py

echo.
echo Process completed!
echo Check daily_payouts.log for detailed logs.
echo.

pause
