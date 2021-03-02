Remove working code clutter
Contains future definitions. 


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
      
