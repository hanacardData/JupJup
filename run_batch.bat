setlocal

@echo off
set LOGDIR=C:\Users\user\Desktop\main\trend_analysis\logs

if not exist %LOGDIR% (
    mkdir %LOGDIR%
)

set LOGFILE=%LOGDIR%\log_%date:~0,4%%date:~5,2%%date:~8,2%.log

echo [%date% %time%] ==== Started ==== >> %LOGFILE%
cd /d "C:\Users\user\Desktop\main\trend_analysis"
git checkout main
git pull origin main
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" batch_runner.py >> %LOGFILE% 2>&1
set RETURN_CODE=%errorlevel%
if %RETURN_CODE% neq 0 (
    echo [%date% %time%] !!! Failed with errorlevel %RETURN_CODE% !!! >> %LOGFILE%
) else (
    echo [%date% %time%] --- Completed successfully --- >> %LOGFILE%
)
echo [%date% %time%] ==== Finished ==== >> %LOGFILE%

endlocal
