#!/bin/bash
export FLASK_APP="apps/app.py"  
netstat -lntp | grep 8000 | awk '{print $7}' | awk -F '/' '{print $1}' | xargs kill -9
nohup python apps/app.py &