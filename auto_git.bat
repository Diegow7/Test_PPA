@echo off

cd /d "D:\VS Code\Test_PPA"

echo ===================================== >> git_log.txt
echo %date% %time% >> git_log.txt

python auto_commit.py >> git_log.txt 2>&1

git add . >> git_log.txt 2>&1

for /f "delims=" %%i in (commit_message.txt) do set MSG=%%i

git commit -m "%MSG%" >> git_log.txt 2>&1

git push >> git_log.txt 2>&1

echo ===================================== >> git_log.txt