@echo off
set /p ip=Enter PI lasst IP number: 
start "" "C:\Program Files (x86)\PuTTY\putty.exe" -load %ip% -pw none
