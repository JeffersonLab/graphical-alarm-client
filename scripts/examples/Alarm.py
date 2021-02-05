import time

from utils import *
from KafkaConnection import *
from AlarmProperties import *


def ExtractAlarmType(definition) :
   type = "StreamRuleAlarm"
   
   producer = definition['producer']
  
   if ('pv' in producer) :
      type = "DirectCAAlarm"
   
   return(type)

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
      self.propwidget = None
      self.ack = False      

      #Timestamps displayed on GUI. 
      #timestamp = time of ACTIVE ALARM
      #acktime   = time of ACKNOWLEDGEMENT  
      #cleartime = time of CLEARING
      self.timestamp = None
      self.acktime = None
      self.cleartime = None
      #self.timestamp = StringVar()
      #self.acktime = StringVar()
      #self.cleartime = StringVar()
      
   #Determine which image to use as the status indicator
   def GetDisplayIndicator(self) :
      
      #The image is based on the current status, or
      #if the alarm has cleared, but not been acknowledged.
      image = None
      
      status = self.GetStatus()
      ack = self.GetAcknowledged()
      #Alarm is active, use the image associated with its current
      #status
      if (status) :
         image = GetStatusImage(status)
      elif (not status and not ack) :
         image = GetStatusImage("ACK")
      #latched alarm is no longer active, but cannot be removed since it 
      #has not been acknowledged. Image will be white.
#      elif (status == None and laststatus != None) :        
 #        image = GetPriorityImage("ACK")
      return(image)
  
   #If alarm already exists, replace previous definition.
   def Configure(self,params) :
      self.definition = params
 
   #accessors
   def GetName(self) :
      return(self.name)
   
   #extract the time stamp from the last active alarm
   def GetTimeStamp(self) :      
      return(self.timestamp)
   
   def GetAckTime(self) :
      return(self.acktime)
   
   def GetClearTime(self) :
      return(self.cleartime)
           
   #Priority from the current status 
   def GetPriority(self) :    
      return(self.priority)
   
   def GetLastPriority(self) :
      return(self.lastpriority)
      
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
   def GetLatching(self) :
      return(self.GetParam('latching'))
       
   #Has the alarm been acknowledged?
   def GetAcknowledged(self) :      
      ack = self.ack
      #If the alarm is not a latching alarm...consider it always
      #acknowledged.            
      if (not self.GetLatching()) :
         ack = True            
      return(ack)
   
   def GetLocation(self) :
      return(self.GetParam("location"))
   
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
   
      
   #Activate an alarm. Add or Remove from AlarmPane
   def Activate(self) :      
      
      #ack = self.GetAcknowledged()
      alarming = self.GetStatus()
      ack =self.GetAcknowledged()
      
      
      
      #If this is NOT, a latching alarm, remove from the AlarmPane
      if (not alarming and not self.GetLatching()) :
         self.Remove()
      elif (not alarming and ack) :
         self.Remove()
      else :
         if (self.GetLatching()) :
            print("ALARMING:",alarming,"ACK:",ack)         
         self.Display()
         return
         
         #This is a latching alarm that has been cleared. 
         #If it has not been acknowledged (cleartime > acktime)
         #DO NOT remove from the AlarmPane. Reconfigure to
         #show new status
         acktime = self.GetAckTime()
         cleartime = self.GetClearTime()
         
         #Alarm has been acknowledged, safe to to remove
         if (len(acktime) > 0 and cleartime >= acktime) :        
            
            self.Remove()
         elif (self.GetLastPriority() is None) :
            self.Remove()
         else :
           
            self.Display()
 
     
   def Reconfig(self) :
      GetMain().GetActivePane().ReconfigAlarm(self)
           
   #Remove an inactive alarm from the alarm pane      
   def Remove(self) :
      GetModel().removeAlarm(self)
   
   #Add an active alarm 
   def Display(self) :
      
      GetModel().addAlarm(self)
      #GetMain().GetActivePane().AddAlarm(self)

   
   #Acknowledge an alarm by sending a Kafka message to the 'active-alarms'
   #topic    
   def AcknowledgeAlarm(self) :
      producer = GetProducer()
      clear = False
      
      if (producer == None) :
         producer = KafkaProducer('active-alarms')
         SetProducer(producer)
      priority = self.GetPriority()
      
      if (priority is None) :
         priority = self.GetLastPriority()
         clear = True
         
      if (priority != None) :
         
         producer.AckMessage(self.GetName(),priority)
         if (clear) :
            producer.ClearMessage(self.GetName())
         
   
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

   
   
   #########        SHELVING   #################
   def GetShelfStatus(self) :
      return(self.shelfstatus)
      
   def Shelve(self) :
      print("SHELVING",self.GetName(),self.GetShelfExpiration())
      
    
   def SetShelvingStatus(self,ts,shelfstatus) :
      if (shelfstatus == None) :
         self.shelfstatus = None
         return
         
      duration = shelfstatus
      reason = None
      expiration = None
      if (shelfstatus != None) :
         if ('expiration' in shelfstatus['duration']) :
            expiration = shelfstatus['duration']['expiration']
         if ('reason' in shelfstatus['duration']) :
            reason = shelfstatus['duration']['reason']
            
      self.shelfstatus = (ts,expiration,reason)
   
   def GetShelfExpiration(self) :
      
      (ts,exp,reason) = self.shelfstatus
      return(exp)
   
   def GetShelfTimeStamp(self) :
      (ts,exp,reason) = self.shelfstatus
      return(ts)
   
   def GetShelfReason(self) :
      (ts,exp,reason) = self.shelfstatus
      return(reason)
      
################################################   
class StreamRuleAlarm(Alarm) :
   def __init__(self,name,params=None) :
      super(StreamRuleAlarm,self).__init__(name,"streamrule",params)
      
      self.alarming = False
   
   def GetStatus(self) :
      alarming = self.alarming
      if (self.alarming) :
         alarming = "ALARMING"
      return(alarming)
   
   #Get the alarm's trigger for display
   def GetTrigger(self) :
      
      pv = None
      try :
         producer = self.GetParam('producer')
         pv = producer['jar']
      except :
         pass
      return(pv)

   def ExtractAlarming(self,status) :
      
      #alarming = status['msg']['alarming']
      return(status)
      
   def SetStatus(self,ts,status) :
      self.alarming = True
      self.ack = False
      
      #self.alarming = self.ExtractAlarming(status)
      self.timestamp = ts
   
   def ExtractAck(self,status) :
      #ack = status['msg']['acknowledged']
      return(status)
      
   def SetAck(self,ts,status) :
      self.ack = True
      #self.ack = self.ExtractAck(status)
      self.acktime = ts
      
class EpicsAlarm(Alarm) :
   def __init__(self,name,params=None) :
      super(EpicsAlarm,self).__init__(name,"epics",params)
      
      self.stat = None
      self.sevr = None
      self.laststat = None
      self.lastsevr = None
      
   
   #Returns SEVR or False if SEVR = NO_ALARM   
   def GetStatus(self) :
      sevr = self.sevr
      if (sevr == "NO_ALARM") :
         sevr = False
      return(sevr)

   def ExtractSevr(self,status) :
      sevr = status['msg']['sevr']
      return(sevr)
   
   def ExtractStat(self,status) :
      return(status['msg']['stat'])
         
   #An EPICS alarm has a status and a severity
   def SetStatus(self,ts,status) :
      sevr = self.ExtractSevr(status)
      stat = self.ExtractStat(status)
      
      #If a severity is assigned, 
      #Alarm has been cleared
      if (sevr == "NO_ALARM") :
         self.cleartime = ts
         
      else :
         self.timestamp = ts
         self.ack = False
         self.acktime = ""
         self.cleartime = ""
      
      self.lastsevr = self.sevr
      self.laststat = self.stat
      self.sevr = sevr
      self.stat = stat
   
   
   def ExtractAck(self,status) :
      ack = False
      ack = status['msg']['ack']
      if (ack != "NO_ACK") :
         ack = True
      return(ack)
   
   def SetAck(self,ts,status) :
      self.ack = self.ExtractAck(status)
      self.acktime = ts
   
   #Has the alarm been acknowledged?
   def GetAcknowledged(self) :      
      ack = self.ack
      #If the alarm is not a latching alarm...consider it always
      #acknowledged.            
      if (not self.GetLatching()) :
         ack = True     
      elif (ack == "NO_ACK") :
         ack = False       
      return(ack)
   
   #Acknowledge an alarm by sending a Kafka message to the 'active-alarms'
   #topic    
   def AcknowledgeAlarm(self) :
      producer = GetProducer()
      clear = False      
      if (producer == None) :
         producer = KafkaProducer('active-alarms')
         SetProducer(producer)
      
      status = self.GetStatus()
      if (status) :
         producer.AckMessage(self.GetName(),status + "_ACK")
         if (clear) :
            producer.ClearMessage(self.GetName())

