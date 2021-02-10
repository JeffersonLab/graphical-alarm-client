import time

from utils import *
from KafkaConnection import *
from AlarmProperties import *

#Figure out what type of alarm we're dealing with.
def ExtractAlarmType(definition) :
   type = "StreamRuleAlarm"
   
   producer = definition['producer']  
   if ('pv' in producer) :
      type = "DirectCAAlarm"   
   return(type)

#Create an alarm of the correct type
def MakeAlarm(alarmname,type,params=None) :
   alarm = None
  
   if (type == None) :
      type = ExtractAlarmType(params)
   
   if (type == "DirectCAAlarm") :
      alarm = EpicsAlarm(alarmname,params)
   elif (type == "StreamRuleAlarm") :
      alarm = StreamRuleAlarm(alarmname,params)
   return(alarm)

     
#Encapsulate an alarm object
class Alarm(object) :
   
   #It is possible to create an alarm without a full definition.
   def __init__(self,name,type,params=None) :
      self.name = name
      self.type = type
      self.definition = params
      self.registered = False
      self.propwidget = None
      self.ack = False      
      self.latched = True
      self.latchsevr = None
      
      #Timestamps displayed on GUI. 
      #timestamp = time of ACTIVE ALARM
      #acktime   = time of ACKNOWLEDGEMENT  
      #cleartime = time of CLEARING
      self.timestamp = None
      self.acktime = None
      self.cleartime = None
   
      self.debug = False
         
   #If alarm already exists, replace previous definition.
   def Configure(self,params) :
      self.definition = params      
      
      #Have to reset the latchsevr because the "latching" property
      #may have been changes.
      self.SetLatchSevr()
     
   #accessors
   def GetName(self) :
      return(self.name)
   
   #extract the time stamp from the last active alarm
   def GetTimeStamp(self) :      
      return(self.timestamp)
   
   #What time was the alarm acknowledged?
   def GetAckTime(self) :
      return(self.acktime)
   
   def GetClearTime(self) :
      return(self.cleartime)
      
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
      
   #Get the location of the alarm 
   def GetLocation(self) :
      return(self.GetParam("location"))
   
   #And its category
   def GetCategory(self) :
      return(self.GetParam("category"))
      
   #General accessor
   def GetParam(self,param) :
      value = None 
       
      if (self.definition == None) :
         return
      if (param in self.definition) :
         value = self.definition[param]      
      return(value)
   
      
   #Activate an alarm. Add or Remove from AlarmModel
   def Activate(self) :      
      #Alarms that latch are a little more complicated when
      #determining whether not they are removed or displayed     
      sevr = self.GetSevr()
      self.SetLatchSevr()
      
      latched = self.GetLatchSevr()
      
      #The alarm has been acknowledged (if necessary) and cleared
      if ((latched == None or latched == "NO_ALARM")  and 
         (sevr == None or sevr == "NO_ALARM")) :
         self.Remove()
      
      #The alarm is in, and does not need to be acknowledged
      elif (sevr != None and latched == None) :        
         self.Display()
      
      #alarm is latched
      elif (latched != None) :                
         self.Display()
                 
   #Remove an inactive alarm from the alarm model
   def Remove(self) :
      GetModel().removeAlarm(self)
   
   #Add an active alarm to the alarm model
   def Display(self) :
      GetModel().addAlarm(self)
       
   #Display the alarm properties
   def ShowProperties(self) :
      if (self.propwidget != None) :
         self.propwidget.Close()      
      self.propwidget = AlarmProperties(self)
   
   #Configure the alarm properties widget
   def ConfigProperties(self) :            
      if (self.propwidget == None or not WidgetExists(self.propwidget)) :
         return      
      priority = self.GetPriority()
      self.propwidget.ConfigProperties(priority)

#Kafka alarm system connects and monitors to the EPICS.STAT 
#Kafka type: "DirectCAAlarm"       
class EpicsAlarm(Alarm) :
   def __init__(self,name,params=None) :
      super(EpicsAlarm,self).__init__(name,"epics",params)
      
      self.stat = None
      self.sevr = None
      
   #determine the alarming sevr/stat/latch    
   def SetAlarming(self,ts,status) :
      self.SetSevr(ts,status)      
      self.SetStat(status)
      self.SetLatchSevr()    
   
   #An EPICS alarm's sevr: MAJOR/MINOR/NO_ALARM
   def SetSevr(self,ts,status) :
      sevr = self.ExtractSevr(status)
      
      #If a severity is assigned, 
      #Alarm has been cleared
      if (sevr == "NO_ALARM") :
         self.cleartime = ts        
      else :
         self.timestamp = ts
         self.ack = False
         self.acktime = None
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
      
      #First time through, latchsevr set to the same as the sevr  
      elif (latchsevr == None or latchsevr == "NO_ALARM") :
         latchsevr = sevr
         
      #Upon invocation of the manager.
      #Alarm has been cleared (NO_ALARM), but not yet acknowledged
      elif (self.acktime != None and self.timestamp == None) :        
         self.sevr = "NO_ALARM"
      
      #acknowledgement came AFTER new alarm
      elif (self.acktime != None and self.acktime > self.timestamp) :
         
         #Alarm considered unlatched/acknowledged if the latchsevr 
         #is at least as great as the sevr
         if (GetRank(latchsevr) >= GetRank(sevr)) :
            latchsevr = None
         else :
            latchsevr = sevr

      #Translate the latchsevr into sevr, to make easier comparison   
      self.latchsevr = TranslateACK(latchsevr)
   
   #Access the latchsevr
   def GetLatchSevr(self) :
      return(TranslateACK(self.latchsevr))
   
   ###STATUS == HIHI,LOLO etc. Not implemented yet.
   def SetStat(self,status) :
      return(None)
   def ExtractStat(self,status) :
      return(status['msg']['stat'])

 ##############################################################  
   
   
   #Acknowledge an alarm by sending a Kafka message to the 'active-alarms'
   #topic    
   def AcknowledgeAlarm(self) :
      producer = GetProducer('active-alarms')
          
      status = self.GetLatchSevr()
      print("STATUS:",status)
      if (status) :
         producer.AckMessage(self.GetName(),status)
        

   #Get an acknowledgement message form the server
   def ReceiveAck(self,ts,status) :
      self.latchsevr = self.ExtractAck(status)
      self.acktime = ts
      
      #self.SetLatchSevr()
            
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
