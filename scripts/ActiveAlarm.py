from Alarm import *

class ActiveAlarm(Alarm) :
   def __init__(self,name,type,params=None) :
      super(ActiveAlarm,self).__init__(name,type,params)
      
      self.ack = False
      self.latched = True
      self.latchsevr = None
      
      self.acktime = None
      self.cleartime = None
   
   #If alarm already exists, replace previous definition.
   def Configure(self,params) :
      super().Configure(params)
      
      #Have to reset the latchsevr because the "latching" property
      #may have been changed.
      self.SetLatchSevr()
   
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
      print("        ALARM ACTIVATE")
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

