#! /bin/csh

INSTRUCTIONS 

#docker build . -t gui --no-cache
docker-compose up

#load ps command
apt-get update && apt-get install -y procps


######################################################
#Set up environment
ip=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
echo $ip
/opt/X11/bin/xhost + $ip
######################################################


#New code from Ryan
update docker-compose.yml
docker-compose build -—no-cache (do not cut and paste)

#Create schemas prior to start up
docker exec -it jaws /scripts/registry/create-alarm-schemas.py
#run script
pip install jlab-jaws
docker exec -u root -it gui bash

python3 AlarmManager.py


CONSOLE COMMANDS
-------------------
docker exec -it jaws /scripts/client/set-registered.py latching1 --latching --producersimple
docker exec -it jaws /scripts/client/set-state.py alarm1 --state Active
docker exec -it jaws /scripts/client/set-active.py alarm1 


REMEMBER TO CHECK IP=DOCKER_DISPLAY if getting display errors
----------------------------
^Cqt.qpa.xcb: could not connect to display 192.168.1.2:0
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.

Command=line editor = nano
nano ./bash_profile




pyQT5 --
   apt-get update
  ** apt-get install -y libgl1-mesa-dev
  ** apt-get install libgtk2.0-dev
   apt install libxcb-xinerama0 
 ** pip3 install PyQt5