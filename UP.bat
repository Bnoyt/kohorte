@echo off

set /p message="commit message :"

git add .

git commit -m "%message%"
git push origin master

pause