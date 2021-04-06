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
docker-compose build -—no-cache 

#Create schemas prior to start up
docker exec -it console /scripts/registry/create-alarm-schemas.py
#run script
docker exec -u root -it gui bash

python3 AlarmManager.py


CONSOLE COMMANDS
-------------------
docker exec -it console /scripts/client/set-shelved.py --reason "We are testing this alarm" --expirationseconds 5 alarm1

docker exec -it console /scripts/client/set-shelved.py --unset alarm1

docker exec -it console /scripts/client/set-registered.py --producerpv VAL --location INJ --category Misc --latching --docurl "" --screenpath "" LATCHING

docker exec -it console /plugins/epics/scripts/set-alarming-epics.py --sevr MAJOR --stat HIHI channel2



#docker exec -it console bash

REMEMBER TO CHECK IP=DOCKER_DISPLAY if getting display errors


TO DO:
   Deal with first set of alarms on startup. 
   

Command=line editor = nano


pyQT5 --
   apt-get update
  ** apt-get install -y libgl1-mesa-dev
  ** apt-get install libgtk2.0-dev
   apt install libxcb-xinerama0 
 ** pip3 install PyQt5