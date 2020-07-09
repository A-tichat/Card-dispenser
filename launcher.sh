!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/Card-dispenser
source bin/activate
sudo python3 main.py
cd /