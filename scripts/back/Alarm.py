import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QModelIndex
from utils import *
from KafkaConnection import ConvertTimeStamp
from PropertyDialog import *
from AlarmThread import *
from utils import *


#Encapsulate an alarm object
class Alarm(object) :
   
   #It is possible to create an alarm without a full definition.
   def __init__(self,name,type,params=None) :
      self.name = name
      self.type = type
     
      self.definition = params
      
      
      self.propwidget = None
      self.isshelved = False
      
      #Timestamps displayed on GUI. 
      #timestamp = time of ACTIVE ALARM
      #acktime   = time of ACKNOWLEDGEMENT  
      #cleartime = time of CLEARING
      self.timestamp = None
      
      self.acktime = None
      self.cleartime = None
      
      self.shelftime = None
      self.shelfexpire = None
      self.shelfreason = None
      self.timeleft = None
      self.shelftimer = None
      self.delay = 1.0
      
      self.worker = None
      self.counting = False
      
      self.debug = False
      if (self.GetName() == "alarm1") :
         self.debug = True
         
   #If alarm already exists, replace previous definition.
   def Configure(self,params) :
      self.definition = params      
      if (self.GetName() == "alarm1") :
         self.debug = True

     
   #accessors
   def GetName(self) :
      return(self.name)
   
   def GetType(self) :
      return(self.type)
      
   #extract the time stamp from the last active alarm
   def GetTimeStamp(self) :      
      return(self.timestamp)
         
   #Get the alarm's trigger for display
   def GetTrigger(self) :
      pv = None
      try :
         producer = self.GetParam('producer')
         pv = producer['pv']
      except :
         pass
      return(pv)
   
   #Does the alarm "latch" ie. Does the alarm require operator acknowledgement. 
   def IsLatching(self) :
      #By default, all alarms are latching. Better safe than sorry
      latching = True 
      if (self.GetParam('latching') != None) :
         latching = self.GetParam('latching')
      return(latching)
   
   #determine the alarming sevr/stat/latch    
   def SetAlarming(self,ts,status) :
     
      self.SetSevr(ts,status)      
      self.SetStat(status)
      self.SetLatchSevr()    
   
   #Get the location of the alarm 
   def GetLocation(self) :
      return(self.GetParam("location"))
   
   #And its category
   def GetCategory(self) :
      return(self.GetParam("category"))
   
   def GetURL(self) :
      return(self.GetParam("docurl"))
  
   def GetScreenPath(self) :
      return(self.GetParam("screenpath"))
        
   #General accessor
   def GetParam(self,param) :
      value = None 
       
      if (self.definition == None) :
         return
      if (param in self.definition) :
         value = self.definition[param]      
      return(value)
   
      
   
   #########        SHELVING   #################
   def IsShelved(self) :
      return(self.isshelved)
   
   def Shelve(self) :

      self.isshelved = True
      self.Display()
      self.ConfigProperties()
      
      
   def UnShelve(self) :
 
      self.isshelved = False
      self.Remove()
      self.counting = False
      self.ConfigProperties()
   
   def GetShelfTime(self) :
      return(self.shelftime)
   
   def Now(self) :
      return(ConvertTimeStamp(int(time.time()) * 1000))
   

   def SetShelvingStatus(self,ts,shelfstatus) :
      if (shelfstatus == None) :
         self.shelfstatus = None
         return
      
      self.shelftime = ts
      self.timeleft = None
      
      reason = None
      expiration = None
      if (shelfstatus != None) :
         if ('expiration' in shelfstatus) :
            expiration = shelfstatus['expiration']
            if (expiration == None) :
               self.shelfexpire = None
            else :  
               self.shelfexpire = ConvertTimeStamp(expiration)
               print(expiration,"EXPERATION!!",self.shelfexpire)
         if ('reason' in shelfstatus) :
            reason = shelfstatus['reason']
            self.shelfreason = reason      
      if (self.shelfexpire != None) :
         self.timeleft = self.shelfexpire - self.Now()
            
   
   def GetShelfExpiration(self) :            
      return(self.shelfexpire)
      
   def GetShelfReason(self) :
      return(self.shelfreason)
   
   def CalcTimeLeft(self) :
      
      if (self.Now() <= self.shelfexpire) :
         self.timeleft = self.shelfexpire - self.Now()      
      else :
         self.timeleft = None
      
      #self.SetDelay()
      return(self)
      
   def StartCountDown(self) :
      if (self.counting or self.GetShelfExpiration() == None) :
         return    
      worker = None
      self.counting = True
      GetManager().StartCountDown(self)
   
   def ConvertDurationString(self,string) :
   
      splitstring = string.split()
      magnitude = int(splitstring[0])
      units = splitstring[1]
      
      if ("min" in units) :
         magnitude = magnitude * 60
      elif ("hour" in units) :
         magnitude = magnitude * 3600
      
      #topic takes milliseconds
      seconds = time.time() + magnitude
      expiration = int(seconds * 1000)
      
      return(expiration)
      
   def ShelveRequest(self,reason,duration) :
      magnitude = duration
      seconds = time.time() + magnitude
      expiration = int(seconds * 1000)
      
      
     
      producer = GetProducer('shelved-alarms')
      print(self.GetName(),reason,expiration)
      
      producer.ShelveMessage(self.GetName(),reason,expiration)
   
   def UnShelveRequest(self) :
      producer = GetProducer('shelved-alarms')
      producer.UnShelveRequest(self.GetName()) 
   
   
   #Remove an inactive alarm from the alarm model
   def Remove(self) :
   
      GetModel().removeAlarm(self)
   
   #Add an active alarm to the alarm model
   def Display(self) :
      GetModel().addAlarm(self)
       
   #Display the alarm properties
   def ShowProperties(self) :
      
      dialog = self.propwidget
      if (dialog == None) :
         dialog = GetManager().PropertyDialog(self)
      
      RaiseDialog(dialog)
      self.propwidget = dialog
  
   
   #Configure the alarm properties widget
   def ConfigProperties(self) :            
      if (self.propwidget == None) :
         return      
      if (self.debug) :
         print("ALARM CONFIGURE PROPS",self.propwidget)
      
      self.propwidget.ConfigureProperties()

#Kafka alarm system connects and monitors to the EPICS.STAT 
#Kafka type: "DirectCAAlarm"       
class EpicsAlarm(Alarm) :
   def __init__(self,name,params=None) :
      super(EpicsAlarm,self).__init__(name,"epics",params)
      
      print("CREATING EPICS ALARM",self.GetName())
      self.stat = None
      self.sevr = None
      self.ack = False
      self.latched = True
      self.latchsevr = None
      
   #   if (self.debug) :
    #     print("INIT ALARM TO NONE")
      self.acktime = None
      self.cleartime = None
   
   #If alarm already exists, replace previous definition.
   def Configure(self,params) :
      super().Configure(params)
      
      #Have to reset the latchsevr because the "latching" property
      #may have been changed.
      self.SetLatchSevr()
     
   #determine the alarming sevr/stat/latch    
   def SetAlarming(self,ts,status) :
      
      self.SetSevr(ts,status)      
      self.SetStat(status)
      self.SetLatchSevr() 
      self.ConfigProperties()   
   
   #An EPICS alarm's sevr: MAJOR/MINOR/NO_ALARM
   def SetSevr(self,ts,status) :
      
      sevr = self.ExtractSevr(status)
      
      #If a severity is assigned, 
      #Alarm has been cleared
      if (sevr == "NO_ALARM") :
         self.cleartime = ts        
      else :
      #   if (self.debug) :
            #print("\nSET SEVR")
            #print("ALRTIME",ts)
            #print("ACKTIME", self.acktime,"\n")
            
         self.timestamp = ts
         if (self.acktime != None and self.acktime < self.timestamp) :
            self.acktime = None
            
         self.ack = False
         
         self.cleartime = ""
      
      self.sevr = sevr
   
   #Read the kafka message and access the sevr
   def ExtractSevr(self,status) :
      sevr = status['msg']['sevr']            
      return(sevr)
      
   #Returns SEVR  
   def GetSevr(self) :
      return(self.sevr)

   #Latch severity and severity are intertwined.
   #All use cases for LATCHING alarms only 
   def SetLatchSevr(self) :

      sevr = self.GetSevr()
      latchsevr = self.GetLatchSevr()

      #If not a latching alarm...easy
      if (not self.IsLatching()) :         
         latchsevr = None
      
      #acknowledgement came AFTER new alarm
      elif (self.acktime != None and self.timestamp != None 
         and self.acktime > self.timestamp) :
   
         latchsevr = None

      #First time through, latchsevr set to the same as the sevr  
      elif (latchsevr == None or latchsevr == "NO_ALARM") :
         
        
         latchsevr = sevr
         
      #Upon invocation of the manager.
      #Alarm has been cleared (NO_ALARM), but not yet acknowledged
      elif (self.acktime != None and self.timestamp == None) :        
         self.sevr = "NO_ALARM"
        
 
      self.latchsevr = TranslateACK(latchsevr)
      
      
   #Access the latchsevr
   def GetLatchSevr(self) :
      return(TranslateACK(self.latchsevr))
   
   ###STATUS == HIHI,LOLO etc. Not implemented yet.
   def SetStat(self,status) :
      return(None)
   def ExtractStat(self,status) :
      return(status['msg']['stat'])
   #What time was the alarm acknowledged?
   def GetAckTime(self) :
      return(self.acktime)
   
   def GetClearTime(self) :
      return(self.cleartime)
   
   #Activate an alarm. Add or Remove from AlarmModel
   #####WORKS FOR ALARM MANAGER
   def Activate(self) :            
      #Alarms that latch are a little more complicated when
      #determining whether not they are removed or displayed     
      sevr = self.GetSevr()
      self.SetLatchSevr()
      latched = self.GetLatchSevr()
      
      #The alarm has been acknowledged (if necessary) and cleared
      if ((latched == None or latched == "NO_ALARM")  and 
         (sevr == None or sevr == "NO_ALARM") or self.IsShelved()) :
         self.Remove()
      
      #The alarm is in, and does not need to be acknowledged
      elif (sevr != None and latched == None) :        
         self.Display()
      
      #alarm is latched
      elif (latched != None) :                
         self.Display()
      self.ConfigProperties()

 ##############################################################  
   
   
   #Acknowledge an alarm by sending a Kafka message to the 'active-alarms'
   #topic    
   def AcknowledgeAlarm(self) :
      producer = GetProducer('active-alarms')
          
      status = self.GetLatchSevr()
      if (status) :
         producer.AckMessage(self.GetName(),status)
        

   #Get an acknowledgement message form the server
   def ReceiveAck(self,ts,status) :
      self.latchsevr = self.ExtractAck(status)           
      self.acktime = ts
            
   #Extract the ack status from the message
   def ExtractAck(self,status) :
      ack = False
      ack = status['msg']['ack']
      return(ack)
   
################################################   
class StreamRuleAlarm(Alarm) :
   def __init__(self,name,params=None) :
      super(StreamRuleAlarm,self).__init__(name,"streamrule",params)
      
      self.alarming = False
################################################   



 
      