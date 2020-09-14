# graphical-alarm-client
A graphical desktop user interface client application for the [kafka-alarm-system](https://github.com/JeffersonLab/kafka-alarm-system).  Written in Python with TK and allows users to:
- List active alarms
- List alarm definitions (including inactive alarms)
- Shelve alarms
## Docker
```
docker-compose up
```
Connect to the gui container via a bash terminal:   
```
docker exec -it gui bash
```
**Note:** Use "docker-compose down" to cleanup
### Docker Build
```
docker build . -t gui 
```
**Note**: If building from on the JLab network you'll need to add the following additional build argument:
```
--build-arg CUSTOM_CRT_URL=http://pki.jlab.org/JLabCA.crt
```
### Docker Run
All of the containers must communicate, which is easiest if they're all on the same Docker network.  Also, an X-Windows DISPLAY environment variable must be set properly for the host in order to see the display.  Docker compose makes this easier, but if you want to just run the gui container use:
```
docker run -rm -it -e DISPLAY=? -v ? gui
```
Where the DISPLAY is host dependent and so is the relative path in the volume option:
```
_macOS_: 
```
-e DISPLAY=$ip:0 -v $(pwd)/scripts:/scripts
```
_Windows_:
```
-e DISPLAY=host.docker.internal:0 -v %cd%/scripts:/scripts
```
_Linux_:
```
-e DISPLAY=:0 -v $(pwd)/scripts:/scripts
```
**Note**: This Docker container requires a local X-Windows server, on Microsoft Windows and Mac in particular you may need to launch one.
