@echo off
if not "%1" == "max" start /MAX cmd /c %0 max & exit/b
cd /d %~dp0
python appender.py
echo.
echo =========================
echo Script finished or crashed
echo =========================
pause