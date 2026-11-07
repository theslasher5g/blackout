@echo off
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
set BLACKOUT_ROOT=%ROOT%
set PY=%ROOT%\bin\win-x64\python\python.exe
if not exist "%PY%" set PY=python
"%PY%" "%ROOT%\app\ingest.py" %*
pause
