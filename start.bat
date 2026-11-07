@echo off
rem BLACKOUT Start (Windows). Optional vorher: set MODEL=datei.gguf
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
set BLACKOUT_ROOT=%ROOT%
set BIN=%ROOT%\bin\win-x64
if not exist "%BIN%\llama-server.exe" ( echo Programme fehlen in %BIN% & pause & exit /b 1 )
if "%MODEL%"=="" set /p MODEL=<"%ROOT%\models\default.txt"
echo Modell: %MODEL%
if exist "%ROOT%\zim\*.zim" start "Kiwix" /B "%BIN%\kiwix-serve.exe" --port 8080 "%ROOT%\zim\*.zim"
start "LLM" /B "%BIN%\llama-server.exe" -m "%ROOT%\models\%MODEL%" -c 8192 --host 127.0.0.1 --port 8081
set PY=%BIN%\python\python.exe
if not exist "%PY%" set PY=python
echo Gleich bereit: http://localhost:8000  (KI braucht beim Laden 10-60 s)
start "" /B cmd /c "timeout /t 4 >nul & start http://localhost:8000"
"%PY%" "%ROOT%\app\rag_server.py"
taskkill /F /IM llama-server.exe >nul 2>&1
taskkill /F /IM kiwix-serve.exe >nul 2>&1
