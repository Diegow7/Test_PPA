@echo off

cd /d "D:\VS Code\Test_PPA"

python auto_commit.py

git add .

git commit -m "feat: modify backend files"

git push