#! /bin/csh

INSTRUCTIONS 

#docker build . -t gui --no-cache
docker-compose up



######################################################
#Set up environment
ip=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
echo $ip
/opt/X11/bin/xhost + $ip
######################################################


#New code from Ryan
update docker-compose.yml
docker-compose build -—no-cache gui


#run script
docker exec -u root -it gui bash

python3 AlarmManager.py

run console in kafka-alarms directory
docker exec -it console bash

REMEMBER TO CHECK IP=DOCKER_DISPLAY if getting display errors


TO DO:
   Deal with first set of alarms on startup. 
   

Command=line editor = nano

./set-registered.py --producerpv VAL --location INJ --category Misc --latching --docurl "" --edmpath "" LATCHING

pyQT5 --
   apt-get update
  ** apt-get install -y libgl1-mesa-dev
  ** apt-get install libgtk2.0-dev
   apt install libxcb-xinerama0 
 ** pip3 install PyQt5