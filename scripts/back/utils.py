import datetime
import tempfile  
import tkinter as tk
from tkinter import *
import re 
#import psutil
import pytz
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont, QColor

from KafkaConnection import *

DEPLOY = "ops"

TEST = False
MANAGER = None

CONSUMER = None
PROCESSOR = None

ACTIVEPANE = None
SHELVEDPANE = None
MODEL = None
TABLE = None

REGISTEREDALARMS = {}
ACTIVEALARMS = {}
SHELVEDALARMS = {}
PRODUCERS = {}

BIGBOLD = "-*-helvetica-medium-r-bold-*-16-*-*-*-*-*-*-*"
SMALLBOLD =  "-*-helvetica-medium-r-bold-*-12-*-*-*-*-*-*-*"
SMALL = "-*-helvetica-medium-r-medium-*-12-*-*-*-*-*-*-*"

IMAGEPATH = "./"

ALARMSTATUS = {
   "MAJOR"     : {
      "rank" : 3, "color" : 'red',    "image" : None, "shelved" : None},
   "MINOR"     : {
      "rank" : 1 , "color" : 'yellow', "image" : None, "shelved" : None},
   "ALARMING"  : {
      "rank" : 2, "color" : 'orange', "image" : None, "shelved" : None},
   "ACK"       : {
      "rank" : 2 ,"color" : 'white' , "image" : None} ,
   "NO_ALARM"  : {
      "rank" : 0, "color" : 'white' , "image" : None, "shelved" : None},
}

SOURCEDIR = "./"
   
####
def checkIfProcessRunning(name) :
   return False
   for proc in psutil.process_iter() :
      try :
         print(name.lower(), proc.name().lower())
         if (name.lower() in proc.name().lower()) : return True
         
      except :
         pass
      return False

def MakeBold(label) :
   font = QtGui.QFont()
   font.setBold(True)
   label.setFont(font)
   
####### CREATE PROPERTY ROWS #####
def MakeLabel(text,bold=True) :
   label = QtWidgets.QLabel(text)
   if (bold) :
      MakeBold(label)
   return(label)
  
def RaiseDialog(dialog) :
   dialog.show()
   dialog.activateWindow()
   dialog.raise_()

def FormatTime(timestamp) :
   formatted = None
   if (timestamp != None) :
      formatted =  timestamp.strftime("%Y-%m-%d %H:%M:%S")
   
   return(formatted)
 
def ConfirmAlarms(alarmlist,which="Shelve") :
   alarmnames = []
   for alarm in alarmlist :
      alarmname = alarm.GetName()
      alarmnames.append(alarmname)
   
   
   message = which + " the following alarms?\n\n" + "\n".join(alarmnames)
   msgBox = QtWidgets.QMessageBox()
   msgBox.setIcon(QtWidgets.QMessageBox.Question)
   msgBox.setText(message)
   msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes|
      QtWidgets.QMessageBox.Cancel)
   reply = msgBox.exec()
      
   confirm = False
   if (reply == QtWidgets.QMessageBox.Yes) :
      confirm = True
         
   return(confirm)
      
   
def SetProcessor(processor) :
   global PROCESSOR
   PROCESSOR = processor
   
def GetProcessor() :
   return(PROCESSOR)
   
def GetAlarmType(msgtype) :
   
   type = "StreamRuleAlarm"
   if ("EPICS" in msgtype) :
      type = "DirectCAAlarm"
   
   return(type)
   
def ConvertTimeStamp(seconds) :
   #Work in utc time, then convert to local time zone.
   ts = datetime.fromtimestamp(seconds//1000)
   utc_ts = pytz.utc.localize(ts)
      
   #Finally convert to EST.
   est_ts = utc_ts.astimezone(pytz.timezone("America/New_York"))
   return(est_ts)

def GetRank(status) :   
   status = TranslateACK(status)   
   if (status == None) :
      return(None)
   return(ALARMSTATUS[status]['rank'])

#Little utility so that it's not necessary to keep track
#of the rows in case more/less are needed.
def NextRow(widget) :
   row = widget.row
   if (row != None) :
      row = row + 1
   else :
      row = 0
   widget.row = row
   return(row)

   
def WidgetExists(widget) :
   return(widget.winfo_exists())
   
def GetShelvedImage(status) :
   image = None
   color = GetStatusColor(status)
   if (color != None) :
      if (ALARMSTATUS[status]['shelved'] == None) :
         filename = IMAGEPATH + color + "-small.png"
         image = tk.PhotoImage(file=filename)
         ALARMSTATUS[status]['shelved'] = image
      image = ALARMSTATUS[status]['shelved']
   return(image)

def GetStatusImage(status) :
   
   status = TranslateACK(status)
  
   image = None
   color = GetStatusColor(status)
  
   if (color != None) :
      if (ALARMSTATUS[status]['image'] == None) :
         filename = IMAGEPATH + color + "-big.png"
 
         image = QImage(filename)
         pixmap = QPixmap.fromImage(image)
         
         ALARMSTATUS[status]['image'] = pixmap
      image = ALARMSTATUS[status]['image']
   return(image)

      
def SetModel(model) :
   global MODEL
   MODEL = model

def GetModel() :
   return(MODEL)

def TranslateACK(status) :
   
   ack = status
   if (status != None) :
      match = re.search("(.*)_ACK",status)
      if (match != None) :
         ack = match.group(1)
         if (ack == "NO") :
            ack = status
   return(ack)

def GetQtColor(status) :
   color = GetStatusColor(status)
   if (color != None) :
      return(QColor(color))
      
   return None

def GetStatusColor(status) :
   status = TranslateACK(status)
      
   color = None
   if (status in ALARMSTATUS.keys()) :
      color = ALARMSTATUS[status]['color']
   return(color)

def SetConsumer(consumer) :
   global CONSUMER
   CONSUMER = consumer

def GetConsumer() :
   return(CONSUMER)
   
def SetProducer(producer,topic) :
   global PRODUCERS
   PRODUCERS[topic] = producer

def GetProducer(topic) :
   
   if (not topic in PRODUCERS) :
      producer = KafkaProducer(topic)
      SetProducer(producer,topic)
   return(PRODUCERS[topic])
   

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

def GetActiveAlarms() :
   return(ACTIVEALARMS)
     
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

def SetManager(manager) :
   global MANAGER
   MANAGER = manager

#Access to the main gui
def GetManager() :
   return(MANAGER)   

def SetTable(table) :
   global TABLE
   TABLE = table

def GetTable() :
   return(TABLE)
   
#Determine if a widget exists
def WidgetExists(widget) :
   return(widget.winfo_exists())


#Create the timestamp for the datafile, using the current time.   
def TimeStamp() :
   timestamp = datetime.datetime.now()
  
   return(timestamp.strftime("%s"))

