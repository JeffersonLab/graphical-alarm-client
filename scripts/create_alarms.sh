#!/bin/bash 
docker exec -it jaws /scripts/client/set-registration.py simplealarm --producersimple --location BSY2 --category RADCON --priority P1_CRITICAL
docker exec -it jaws /scripts/client/set-registration.py latchingalarm --latching --producerpv MAG.BDL --location EA --category Box --priority P2_MAJOR
docker exec -it jaws /scripts/client/set-registration.py epicsalarm --producerpv RF.GSET --location NL --category RF --priority P3_MINOR
docker exec -it jaws /scripts/client/set-registration.py calcalarm --producerexpression "BPM.XPOS > 6" --location INJ --category BPM --priority P4_INCIDENTAL
