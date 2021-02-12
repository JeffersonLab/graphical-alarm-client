from Alarm import *
from KafkaConnection import *


      

      
class Processor(object) :
   def __init__(self,root=None) :      
      self.root = root
           
      #Create the KafkaConsumer. To listen for messages.
      self.kafkaconsumer = KafkaConsumer()
      SetConsumer(self.kafkaconsumer)

      self.topicloaded = {}
      self.initalarms = {}
      
      #The topics to which we will subscribe
      self.topics = self.kafkaconsumer.GetTopics()
      #initialize topic dependent variables
      for topic in self.topics :
         self.topicloaded[topic] = False 
         self.initalarms[topic] = {}
         
      #only wait so long for startup alarms      
      self.initcount = 0
      self.initmax = 10

      #Get and create the first batch of alarms upon connection
      self.InitState()
      self.InitProcess()

                   
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
         
         if (msg.error()) :
            print("Continuing {}: {}".format(msg, msg.error()))
            continue
         
         #If it's not an error, use the info to create an alarm
         
         topic = consumer.GetTopic(msg)
         alarm = self.CreateAlarm(msg)
          #Assign this alarm to the topic/alarmname.
         #subsequent states of this alarmname will overwrite.
         #leaving us with the most recent
         self.initalarms[topic][alarm.GetName()] = alarm
         #Topic has finished loading.
         if (msg.offset() + 1 == consumer.GetHighOffsets(topic)) :
            consumer.topicloaded[topic] = True
   
   def IsRegistered(self,alarmname) :
      registered = True
      
      registered = False
      alarm = FindRegAlarm(alarmname) 
      if (alarm != None) :
         definition = alarm.definition
         if (definition is None) :
            registered = False
      
      return(registered)
   
   
  
   def InitShelf(self) :
      shelved = self.initalarms['shelved-alarms']
      for alarmname in shelved.keys() :
         
         alarm = shelved[alarmname]
         
         if (alarm.IsShelved()) :
            alarm.Shelve()
         
  
   
   #Once all topics are loaded. We have the most recent
   #state for each topic, each alarmname.
   def InitAlarms(self) :
      
      #Activate each alarm in the 'active-alarms' topic
      active = self.initalarms['active-alarms']         
      
      for alarmname in active.keys() :
         
         alarm = active[alarmname]   
         alarm.Activate()         

   #Create the alarm as appropriate to the topic
   def CreateAlarm(self,msg) :
      topic = msg.topic()
      alarm = None
            
      if (topic == "registered-alarms") :  
            
         alarm = self.RegisteredAlarm(msg)    
         alarm.Activate()    
      
      if (topic == "active-alarms") :   
         
         alarm = self.ActiveAlarm(msg)
         
      elif (topic == "shelved-alarms") :       
         
         alarm = self.ShelvedAlarm(msg)          
      return(alarm) 
   
   
   def GetAlarms(self) :
      msg = None
      consumer = self.kafkaconsumer
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
         
         alarm.Activate()        
      elif (topic == "shelved-alarms") :
         
         if (alarm.IsShelved() or alarm.GetSevr() == "NO_ALARM") :
            alarm.Remove()
         else :            
            alarm.Activate()            
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
      
   
   def ShelvedAlarm(self,msg) :
      consumer = self.kafkaconsumer

      #When registering an alarm, the msg is the alarm definition
      (alarmname,definition,msgtype) = consumer.DecodeMessage(msg)
      
      #It is possible that an active alarm comes in before it has been
      #registered. 
      alarm = FindAlarm(alarmname)
      if (alarm == None) :
         alarm = Alarm(alarmname,'shelved')
      
      if (definition == None) :
         alarm.UnShelve()
      else :
         alarm.Shelve()
      
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
      
   #   alarm.Activate()
      #Register the alarm. Even if one exists with the same name.
      AddRegAlarm(alarm)
      return(alarm)



      
#This class subscribes to the kafka alarm system(s) 
class AlarmProcessor(Processor) :
   def __init__(self,root=None) :      
      super(AlarmProcessor,self).__init__(root)  
   
   def InitProcess(self) :
      self.InitShelf()   
      self.InitAlarms()
      
   ####WORKS FOR ALARM MANAGER
   def ProcessAlarms(self,msg) :
      consumer = self.kafkaconsumer      
      topic = consumer.GetTopic(msg)
      
      alarm = self.CreateAlarm(msg)
      
      #If an active-alarm, activate it.
      if (topic == "active-alarms") :               
         
         alarm.Activate()        
      elif (topic == "shelved-alarms") :
         
         if (alarm.IsShelved() or alarm.GetSevr() == "NO_ALARM") :
            alarm.Remove()
         else :            
            alarm.Activate()            
      elif (topic == "registered-alarms") :         
         if (consumer.DecodeMessage(msg) == None) :
            alarm.Remove()

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
         
         if (msg.error()) :
            print("Continuing {}: {}".format(msg, msg.error()))
            continue
         
         #If it's not an error, use the info to create an alarm
         #############################################ALARM MANAGER
         topic = consumer.GetTopic(msg)
         alarm = self.CreateAlarm(msg)
          #Assign this alarm to the topic/alarmname.
         #subsequent states of this alarmname will overwrite.
         #leaving us with the most recent
         self.initalarms[topic][alarm.GetName()] = alarm
         #Topic has finished loading.
         if (msg.offset() + 1 == consumer.GetHighOffsets(topic)) :
            consumer.topicloaded[topic] = True
   
   ##############################ALARM MANAGER
   def InitShelf(self) :
      shelved = self.initalarms['shelved-alarms']
      for alarmname in shelved.keys() :
         
         alarm = shelved[alarmname]
         
         if (alarm.IsShelved()) :
            alarm.Shelve()
 
   