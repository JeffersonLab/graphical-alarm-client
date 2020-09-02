# graphical-alarm-client
A graphical desktop user interface client application for the [kafka-alarm-system](https://github.com/JeffersonLab/kafka-alarm-system).  Written in Python with TK and allows users to:
- List active alarms
- List alarm definitions (including inactive alarms)
- Shelve alarms
## Docker
```
docker-compose up
```
To launch just the GUI:
```
docker build . -t gui 
```
**Note**: If building from on the JLab network you'll need to add the following additional build argument:
```
--build-arg CUSTOM_CRT_URL=http://pki.jlab.org/JLabCA.crt
```
_macOS_: 
```
docker run --rm -ti -e DISPLAY=docker.for.mac.host.internal:0 gui
```
_Windows_:
```
docker run --rm -ti -e DISPLAY=host.docker.internal:0 gui
```
_Linux_:
```
docker run --rm -ti --net=host -e DISPLAY=:0 gui
```
**Note**: This Docker container requires a local X-Windows server, on Microsoft Windows in particular you may need to launch one.