#!/bin/bash 
docker exec -it jaws /scripts/client/set-activation.py simplealarm 

docker exec -it jaws /scripts/client/set-activation.py epicsalarm --sevr MAJOR --stat HIHI

docker exec -it jaws /scripts/client/set-activation.py latchingalarm --sevr MAJOR --stat HIHI
docker exec -it jaws /scripts/client/set-effective-activation.py latchingalarm --override Latched --unset
