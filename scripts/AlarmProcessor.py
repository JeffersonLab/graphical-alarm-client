from Processor import *

#The AlarmProcessor processes the alarms as they are received 
#It inherits from the Processor class
class AlarmProcessor(Processor) :
   def __init__(self) :      
      super(AlarmProcessor,self).__init__()  
   
   #Processor class handles the initial state of all alarms. 
   #In the InitState method
   #Process the initial alarm handler state
   def InitProcess(self) :
      
      self.InitAlarms()
      self.InitShelf()   
   
   #Process those alarms in the shelved-alarms topic.    
   def InitShelf(self) :
     
      shelved = self.initalarms['shelved-alarms']
      for alarmname in shelved.keys() :         
         
         alarm = shelved[alarmname]       
         if (alarm.IsShelved()) :
            
            alarm.UnShelve()
            #alarm.Remove()

   #Load the initial set of active alarms
   #state for each topic, each alarmname.
   def InitAlarms(self) :
      #Activate each alarm in the 'active-alarms' topic
      active = self.initalarms['active-alarms']               
      for alarmname in active.keys() :       
         alarm = active[alarmname]   
         alarm.Activate()         
     
   #For registered alarms, we want to make sure that 
   #it is activated as appropriate.
   def RegisteredAlarm(self,msg) :
      
      alarm = super().RegisteredAlarm(msg)
      alarm.Activate()
      return(alarm)   
      
   #Process alarms as they are received by the AlarmProcessor
   def ProcessAlarms(self,msg) :
      consumer = self.kafkaconsumer      
      topic = consumer.GetTopic(msg)
      
      if (msg != None) :
         print("        *PROCESSALARMS",msg)
      #Create the alarm
      alarm = self.CreateAlarm(msg)
      
      #If an active-alarm, activate it.
      if (topic == "active-alarms") :               
         alarm.Activate()        
      elif (topic == "shelved-alarms") :
         #Deal with any alarms that have been either shelved...
         #or their shelf expiration has passed.
         if (alarm.IsShelved()  or alarm.GetSevr() == "NO_ALARM") :
            alarm.Remove()
         else :            
            alarm.Activate()            
      elif (topic == "registered-alarms") :         
         #Could simply be defining a registered alarm.
         #If the alarm has been UNREGISTERED, remove it from the system
         if (consumer.DecodeMessage(msg) == None) :
            alarm.Remove()  
   
   #We have received a message from the "active-alarms" topic
   def ActiveAlarm(self,msg) :
      #The parent class does most of the work. 
      alarm  = super().ActiveAlarm(msg)
      
      kafkaconsumer = self.kafkaconsumer
      msgtype = kafkaconsumer.DecodeMsgType(msg)
      status = kafkaconsumer.DecodeMsgValue(msg)
      timestamp = kafkaconsumer.DecodeTimeStamp(msg)

      #An acknowledgement message from the active-alarms topic
      if ("Ack" in msgtype) :       
         #Alarm has been acknowledged
         alarm.ReceiveAck(timestamp,status)
      else :
         #Set the alarm's sevr/status       
         alarm.SetAlarming(timestamp,status)
                           
      #And add it to the master list of active-alarms         
      AddActiveAlarm(alarm)
      return(alarm)

     