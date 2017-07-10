@echo off
set /p port=Enter serial port: 
python C:\Users\arad-lab\AppData\Local\Programs\Python\Python36\Lib\site-packages\serial\tools\miniterm.py %port% 115200 --eol CRLF
REM python C:\Users\arad-lab\AppData\Local\Programs\Python\Python36\Lib\site-packages\serial\tools\miniterm.py spy://COM34 115200 --eol CR
