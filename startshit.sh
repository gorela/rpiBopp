#!/bin/bash
#rm /home/pi/yay.txt
echo 'zonk' >> /home/pi/yay.txt
# Increase volume by 2%
alias volu='sudo amixer set PCM -- $[$(amixer get PCM|grep -o [0-9]*%|sed 's/%//')+2]%'
# Decrease volume by 2%
alias vold='sudo amixer set PCM -- $[$(amixer get PCM|grep -o [0-9]*%|sed 's/%//')-2]%'
sudo amixer set PCM -- 80%
sudo killall telegram-cli
screen -dmS TelegramCLI /home/pi/tg/bin/telegram-cli -s /home/pi/tg/spotiTele.lua -k /home/pi/tg/tg-server.pub
/home/pi/spotipyV0.2.py
