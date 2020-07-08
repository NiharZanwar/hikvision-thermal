#!/bin/bash
cd /app
sleep 5
git clone https://github.com/NiharZanwar/hikvision-thermal.git
cd hikvision-thermal
git checkout docker
echo "clone complete"
cd /app/hikvision-thermal
python app.py >> /data/log.txt &
ps -aef
cd /data;
python -m http.server 8008
