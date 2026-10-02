@echo off

cd /d "D:\VS Code\Test_PPA"

python auto_commit.py

git add .

for /f "delims=" %%i in (commit_message.txt) do set MSG=%%i

git commit -m "%MSG%"

git push