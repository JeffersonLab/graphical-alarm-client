#! /bin/csh

INSTRUCTIONS 

#HAVE TO HAVE DOCKER DESKTOP
#docker build . -t gui --no-cache
docker-compose up

#load ps command
apt-get update && apt-get install -y procps

192.168.1.6
######################################################
#Set up environment
ip=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
echo $ip
/opt/X11/bin/xhost + $ip
######################################################

#MUST GET IN BASH SHELL
source ~erb/.bash_profile

#New code from Ryan
update docker-compose.yml
docker-compose build -—no-cache (do not cut and paste)

***** DOCKER ENGINE MUST BE STARTED
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

SHELVE
----------------
docker exec -it jaws /scripts/client/list-overridden.py --monitor 
docker exec -it jaws /scripts/client/set-overridden.py --override Shelved alarm1 --reason Other --expirationseconds 5

ONSHOT
----------------
docker exec -it jaws /scripts/client/set-active.py alarm1 
docker exec -it jaws /scripts/client/set-overridden.py alarm1 --override Shelved --oneshot --reason Other --expirationseconds 90
docker exec -it jaws /scripts/client/set-active.py alarm1 --unset

LATCH
-----------
docker exec -it jaws /scripts/client/set-registered.py alarm1 --latching --producersimple
docker exec -it jaws /scripts/client/set-active.py alarm1 
docker exec -it jaws /scripts/client/set-overridden.py alarm1 --override Latched --unset


REMEMBER TO CHECK IP=DOCKER_DISPLAY if getting display errors
----------------------------
^Cqt.qpa.xcb: could not connect to display 192.168.1.2:0
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.

Command=line editor = nano
nano .bash_profile (. file, not directory)

git commands
--------------
git status

pyQT5 --
   apt-get update
  ** apt-get install -y libgl1-mesa-dev
  ** apt-get install libgtk2.0-dev
   apt install libxcb-xinerama0 
 ** pip3 install PyQt5