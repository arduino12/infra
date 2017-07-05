@echo off
hc04conf --detect-ports
set /p port=Enter BT module port: 
hc04conf --port %port% --set-baud 115200 --set-pin 1000 --set-name "UV Bicycle"
