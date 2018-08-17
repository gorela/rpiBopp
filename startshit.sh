#!/bin/bash
killall screen
rm /home/pi/yay.txt
echo 'zonk' >> /home/pi/yay.txt
# Increase volume by 2%
alias volu='sudo amixer set PCM -- $[$(amixer get PCM|grep -o [0-9]*%|sed 's/%//')+2]%'
# Decrease volume by 2%
alias vold='sudo amixer set PCM -- $[$(amixer get PCM|grep -o [0-9]*%|sed 's/%//')-2]%'
sudo amixer set PCM -- 90%
sudo killall telegram-cli
screen -dmS tele /home/pi/tg/bin/telegram-cli -s /home/pi/tg/spotiTele.lua -k /home/pi/tg/tg-server.pub
screen -mS spoti /home/pi/spotipyV0.5.py $1 $2
