#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/Card-dispenser
export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/authenFile/key_dispenser-75e647798c48.json"
python3 main.py
cd /
