import datetime
import tempfile  
import tkinter as tk
from tkinter import *


DEPLOY = "ops"

TEST = False
MAIN = None
ROOT = None
PRODUCER = None


ACTIVEPANE = None
SHELVEDPANE = None

REGISTEREDALARMS = {}
ACTIVEALARMS = {}
SHELVEDALARMS = {}

BIGBOLD = "-*-helvetica-medium-r-bold-*-16-*-*-*-*-*-*-*"
SMALLBOLD =  "-*-helvetica-medium-r-bold-*-12-*-*-*-*-*-*-*"
SMALL = "-*-helvetica-medium-r-medium-*-12-*-*-*-*-*-*-*"

IMAGEPATH = "./"

ALARMSTATUS = {
   "MAJOR"     : {"color" : 'red',    "image" : None, "shelved" : None},
   "MINOR"     : {"color" : 'yellow', "image" : None, "shelved" : None},
   "ALARMING"  : {"color" : 'orange', "image" : None, "shelved" : None},
   "ACK"       : {"color" : 'white' , "image" : None} ,
   "NO_ALARM"  : {"color" : 'green' , "shelved" : None},
}


   
####

def GetAlarmType(msgtype) :
   type = "StreamRuleAlarm"
   if ("EPICS" in msgtype) :
      type = "DirectCAAlarm"
   return(type)
   


def WidgetExists(widget) :
   return(widget.winfo_exists())
   
def GetShelvedImage(status) :
   image = None
   color = GetStatusColor(status)
   if (color != None) :
      if (ALARMSTATUS[status]['shelved'] == None) :
         filename = IMAGEPATH + color + "-shelved.png"
         image = tk.PhotoImage(file=filename)
         ALARMSTATUS[status]['shelved'] = image
      image = ALARMSTATUS[status]['shelved']
   return(image)
   
def GetStatusImage(status) :
   image = None
   color = GetStatusColor(status)
   if (color != None) :
      if (ALARMSTATUS[status]['image'] == None) :
         filename = IMAGEPATH + color + "-ball.png"
         image = tk.PhotoImage(file=filename)
         ALARMSTATUS[status]['image'] = image
            
      image = ALARMSTATUS[status]['image']
   return(image)
         
      
      
def GetStatusColor(status) :
   color = None
   if (status in ALARMSTATUS.keys()) :
      color = ALARMSTATUS[status]['color']
   return(color)

def SetProducer(producer) :
   global PRODUCER
   PRODUCER = producer

def GetProducer() :
   return(PRODUCER)
   
def SetRoot(root) :
   global ROOT
   ROOT = root

def GetRoot() :
   return(ROOT)

#Add and access registered alarms  

#Looks in all alarm lists and returns if found 
def FindAlarm(alarmname) :
  
   #Look at the registered alarms. 
   found = FindRegAlarm(alarmname)
   
   #Look in active alarms 
   if (alarmname in ACTIVEALARMS) :
      found = FindActiveAlarm(alarmname)
      
   elif (alarmname in SHELVEDALARMS) :
      found = SHELVEDALARMS[alarmname]
   
   return(found)

def AddRegAlarm(alarm) :
   REGISTEREDALARMS[alarm.GetName()] = alarm
   
def FindRegAlarm(alarmname) :  
   found = None
   if (alarmname in REGISTEREDALARMS) :
      found = REGISTEREDALARMS[alarmname] 
   return(found)

def AddShelvedAlarm(alarm) :
   SHELVEDALARMS[alarm.GetName()] = alarm
   
def FindShelvedAlarm(alarmname) :
   found = None
   if (alarmname in SHELVEDALARMS) :
      found = SHELVEDALARMS[alarmname]
   return(found)
   
#Add and access active alarms
def AddActiveAlarm(alarm) :
   ACTIVEALARMS[alarm.GetName()] = alarm

      
def FindActiveAlarm(alarmname) :
   found = None
   if (alarmname in ACTIVEALARMS) :
      found = ACTIVEALARMS[alarmname]
   return(found)





#def AddActiveAlarm(alarm) :
 #  ACTIVELIST[alarm   
def SetActivePane(frame) :
   global ACTIVEFRAME
   ACTIVEFRAME = frame
   
def GetActivePane() :
   return(ACTIVEFRAME)

def SetShelvedPane(frame) :
   global SHELVEDPANE
   SHELVEDPANE = frame

def GetSelvedPane() :
   return(SHELVEDPANE)    

def SetAlarmList(alarmlist) :
   global ALARMLIST
   ALARMLIST = alarmlist

def GetAlarmList() :
   return(ALARMLIST)
   
def SetShelvedList(shelvedlist) :
   global SHELVEDLIST
   SHELVEDLIST = shelvedlist

def GetShelvedList() :
   return(SHELVEDLIST)

def SetActiveList(activelist) :
   global ACTIVELIST
   ACTIVELIST = activelist

def GetActiveList() :
   return(ACTIVELIST) 
   
#Command-line option -deploy. Set to use throughout.      
def SetDeployment(deploy) :
   global DEPLOY
   DEPLOY = deploy

#Access command-line -deploy option
def GetDeployment() :
   return(DEPLOY)

#Command-line option -test. Set to use throughout   
def SetTest(test) :
   global TEST
   TEST = test

#Access command-line -test option
def GetTest() :
   return(TEST)

def SetMain(main) :
   global MAIN
   MAIN = main

#Access to the main gui
def GetMain() :
   return(MAIN)   

#Determine if a widget exists
def WidgetExists(widget) :
   return(widget.winfo_exists())


#Create the timestamp for the datafile, using the current time.   
def TimeStamp() :
   timestamp = datetime.datetime.now()
  
   return(timestamp.strftime("%s"))

