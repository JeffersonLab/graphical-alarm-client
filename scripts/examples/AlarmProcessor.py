from Alarm import *
from KafkaConnection import *


      
#This class subscribes to the kafka alarm system(s) 
class AlarmProcessor(object) :
   def __init__(self,root=None) :      
      self.root = root
      
      #Create the KafkaConsumer. To listen for messages.
      self.kafkaconsumer = KafkaConsumer()
      
      #The topics to which we will subscribe
      self.topics = self.kafkaconsumer.GetTopics()
         
      self.topicloaded = {}
      self.initalarms = {}
      
      #initialize topic dependent variables
      for topic in self.topics :
         self.topicloaded[topic] = False 
         self.initalarms[topic] = {}
      
      #only wait so long for startup alarms      
      self.initcount = 0
      self.initmax = 10
      
      self.running = True

      #Get and create the first batch of alarms upon connection
      self.InitState()
      self.InitAlarms()
   
   
   #Create the alarm as appropriate to the topic
   def CreateAlarm(self,msg) :
      topic = msg.topic()
      alarm = None
      
      if (topic == "registered-alarms") :  
              
         alarm = self.RegisteredAlarm(msg)        
      if (topic == "active-alarms") :   
         
         alarm = self.ActiveAlarm(msg)
         
      elif (topic == "shelved-alarms") :       
         alarm = self.ShelvedAlarm(msg)          
      return(alarm) 
 
      
        
   #Get the initial state of the alarm handler system. 
   #There will be a flurry of alarms upon start up. 
   #Assign them as appropriate. We only want the most
   #recent state of an active-alarm. 
   def InitState(self) :
      consumer = self.kafkaconsumer
      
      
      #Don't wait forever to obtain the initial state
      count = self.initcount
      max = self.initmax     
   
      #While the set of topics has not completed loading, we are 
      #still initiating
      while (not consumer.TopicsLoaded()) :
         if (self.initcount > max) :
            raise RuntimeError(
               "Timeout: taking too long to obtain initial state")
         try :
            #Access the producer message
            msg = consumer.GetMessage(True)
            
         except SerializerError as e:
            print("Message deserialization failed for {}".format(e))
            raise 
         
         #No message yet.
         if (msg is None) :
            self.initcount = self.initcount + 1
            continue
         
         #Have topic message
        # (msg,alarmname,topic) = message
         
         if (msg.error()) :
            print("Continuing {}: {}".format(msg, msg.error()))
            continue
         
         #If it's not an error, use the info to create an alarm
         alarm = self.CreateAlarm(msg)
         topic = consumer.GetTopic(msg)
         #Assign this alarm to the topic/alarmname.
         #subsequent states of this alarmname will overwrite.
         #leaving us with the most recent
         self.initalarms[topic][alarm.GetName()] = alarm
         
         #Topic has finished loading.
         if (msg.offset() + 1 == consumer.GetHighOffsets(topic)) :
            consumer.topicloaded[topic] = True
         
         #Keep the GUI responsive
         #root.update_idletasks()
   
   def IsRegistered(self,alarmname) :
      registered = True
      
      alarm = FindRegAlarm(alarmname) 
      if (alarm != None) :
         definition = alarm.definition
         if (definition is None) :
            registered = False
      #else :
       
       #  print(alarmname, "NOT REGISERED!!")
      return(registered)
   
   #Once all topics are loaded. We have the most recent
   #state for each topic, each alarmname.
   def InitAlarms(self) :
      
      #Activate each alarm in the 'active-alarms' topic
      active = self.initalarms['active-alarms']         
      
      for alarmname in active.keys() :
         registered = self.IsRegistered(alarmname)
         alarm = active[alarmname]
         
         if (not registered) :
            print("NOT REG:",alarm) ###NOT SURE IF WE NEED THIS YET
         
         if (registered and alarm.GetStatus()) :
            
            alarm.Activate()
            
        # else :
         #   print("INIT",alarmname,alarm.GetPriority(),alarm.GetLastPriority())
      
      shelved = self.initalarms['shelved-alarms']
      for alarmname in shelved.keys() :
         alarm = shelved[alarmname]
         if (alarm.GetShelfStatus() != None) :
            alarm.Shelve()
      
   
   def GetAlarms(self) :
      msg = None
      consumer = self.kafkaconsumer
      
      #Keep the GUI updated
      #root = self.root     
      try :         
         msg = consumer.GetMessage() 
      except :
         print("Message deserialization failed for {}".format(e))
         return
      
      return(msg)
   
   def ProcessAlarms(self,msg) :
      consumer = self.kafkaconsumer
     
      
      topic = consumer.GetTopic(msg)
            
      alarm = self.CreateAlarm(msg)
      #If an active-alarm, activate it.
      if (topic == "active-alarms") :               
         print("GOING TOACTIVET",alarm.GetName(),alarm)
         alarm.Activate()
      elif (topic == "shelved-alarms") :
         if (alarm.GetShelfStatus() != None) :
            alarm.Shelve()
      elif (topic == "registered-alarms") :
         if (consumer.DecodeMessage(msg) == None) :
            alarm.Remove()
   
   #We have received a message from the "active-alarms" topic
   def ActiveAlarm(self,msg) :
      kafkaconsumer = self.kafkaconsumer
      
      
      #When an alarm is activated, the msg contains the alarm status
      (alarmname,status,msgtype) = kafkaconsumer.DecodeMessage(msg)     
      timestamp = kafkaconsumer.DecodeTimeStamp(msg)
      
      
      #Is this alarm registered? If so, we will not create a 
      #new one,simply reconfigure this one.
      alarm = FindAlarm(alarmname) 
     
      #Can't find an alarm, create a new one. Notice that it's not
      #completely defined. The active-alarm came in before the registered-alarm
      #that contains the definition. We still need to figure out the type
      #of the alarm to create. We can do this with the msgtype.      
      if (alarm == None) :
         type = GetAlarmType(msgtype)
         alarm = MakeAlarm(alarmname,type)
      
      if ("Ack" in msgtype) :
         alarm.SetAck(timestamp,status)
      else :
         #Set the alarm's status             
         alarm.SetStatus(timestamp,status)
      
      #And add it to the master list of active-alarms         
      AddActiveAlarm(alarm)
      return(alarm)
   
   def ShelvedAlarm(self,alarmname,msg) :
      consumer = self.kafkaconsumer
      message = consumer.DecodeMessage(msg)
      timestamp = consumer.DecodeTimeStamp(msg)
      
      alarm = FindAlarm(alarmname)      
      if (alarm == None) :
         alarm = Alarm(alarmname)
      alarm.SetShelvingStatus(timestamp,message)
      AddShelvedAlarm(alarm)
      return(alarm)
      
   #Received a message from the "register-alarms" topic   
   def RegisteredAlarm(self,msg) :
      consumer = self.kafkaconsumer
      
      #When registering an alarm, the msg is the alarm definition
      (alarmname,definition,msgtype) = consumer.DecodeMessage(msg)
      
      #It is possible that an active alarm comes in before it has been
      #registered. 
      alarm = FindAlarm(alarmname)
      
      #Is there already an alarm for this alarmname?
      #If so, reconfigure it.
      if (alarm != None) :
         alarm.Configure(definition)
      else :
         #if not, create a new one.
         alarm = MakeAlarm(alarmname,None,definition)
           
      #Register the alarm. Even if one exists with the same name.
      AddRegAlarm(alarm)
      return(alarm)
   
   
     
