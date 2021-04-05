from Processor import *


#The ShelfProcessor processes only shelved alarms 
#It inherits from the Processor class
class ShelfProcessor(Processor) :
   def __init__(self) :
      super(ShelfProcessor,self).__init__()
   
   
   #Once the initial state is determined (Processor.InitStat())
   #Initialize any shelved-alarms 
   def InitProcess(self) :
      self.InitShelf()
   
   #Process those alarms in the shelved-alarms topic.    
   def InitShelf(self) :
      
      shelved = self.initalarms['shelved-alarms']
      for alarmname in shelved.keys() :         
         
         alarm = shelved[alarmname]       
         if (alarm.IsShelved()) :
            alarm.Shelve()
            alarm.Display()
            print("ADDING:", alarm.GetName(), "to queue")
            GetManager().AddToQueue(alarm)
         else :
            alarm.UnShelve()
            alarm.Remove()

   def UpdateTimeLeft(self,alarm) :
      
      alarm.CalcTimeLeft()
      return(alarm)
   
   #Monitor and process any messages received after initialization
   def ProcessAlarms(self,msg) :
      consumer = self.kafkaconsumer      
      topic = consumer.GetTopic(msg)
           
      alarm = self.CreateAlarm(msg)
      
      #Not tracking messages from the "active" topic
      if ("active" in topic) :
         return      
      
      if (topic == "shelved-alarms") :
         #Deal with the shelved topic
         print("SHELVED?",alarm.IsShelved())
         if (alarm.IsShelved()) :          
            alarm.Display()
            
            alarm.StartCountDown()
         else :           
            alarm.Remove()
            
      #Also track registered-alarms in case need more info about alarm
      elif (topic == "registered-alarms") :         
         if (consumer.DecodeMessage(msg) == None) :
            alarm.Remove()

   #Create a shelved alarm 
   def ShelvedAlarm(self,msg) :
      
      #Initially call the parent's ShelvedAlarm subroutine.
      alarm = super().ShelvedAlarm(msg)
      
      consumer = self.kafkaconsumer
      status = consumer.DecodeMsgValue(msg)
      timestamp = consumer.DecodeTimeStamp(msg)
      
      #Act based on the status of the shelved-alarm
      if (status == None) :         
         alarm.UnShelve()
         
      else :
         
         alarm.SetShelvingStatus(timestamp,status)         
         alarm.Shelve()
         
      
         AddShelvedAlarm(alarm)
      return(alarm)
      
