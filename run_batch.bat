@echo off
cd /d "C:\Users\user\Desktop\main\trend_analysis"
echo [%date% %time%] Start >> log.txt
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" batch_runner.py >> log.txt 2>&1
echo [%date% %time%] Finished >> log.txt
pause
