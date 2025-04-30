setlocal

@echo off
set DIR=C:\Users\user\project\ScrapCompetitor
set LOGDIR=%DIR%\logs
set LOGFILE=%LOGDIR%\log_%date:~0,4%%date:~5,2%%date:~8,2%.log

if not exist %LOGDIR% (
    mkdir %LOGDIR%
)

echo [%date% %time%] ==== Started ==== >> %LOGFILE%
cd /d %DIR%

call C:\Users\user\AppData\Local\anaconda3\Scripts\activate.bat jupjup
echo [%date% %time%] ==== Conda setted ==== >> %LOGFILE%
echo [%date% %time%] ==== Git setted ==== >> %LOGFILE%
python batch_runner.py >> %LOGFILE% 2>&1
set RETURN_CODE=%errorlevel%
if %RETURN_CODE% neq 0 (
    echo [%date% %time%] !!! Failed with errorlevel %RETURN_CODE% !!! >> %LOGFILE%
) else (
    echo [%date% %time%] --- Completed successfully --- >> %LOGFILE%
)
echo [%date% %time%] ==== Finished ==== >> %LOGFILE%

endlocal
