from ActiveAlarm import *

from KafkaConnection import *

#Figure out what type of alarm we're dealing with.
def ExtractAlarmType(definition) :
   type = "StreamRuleAlarm"     
   producer = definition['producer']  
   if ('pv' in producer) :
      type = "DirectCAAlarm"   
   return(type)

#Create an alarm of the correct type
def MakeAlarm(alarmname,type=None,params=None) :
   alarm = None
   
   if (type == None) :
      type = ExtractAlarmType(params)
   if (type == "DirectCAAlarm") :
      alarm = EpicsAlarm(alarmname,params)
   elif (type == "StreamRuleAlarm") :
      alarm = StreamRuleAlarm(alarmname,params)
   elif (type == None) :
      alarm = Alarm(alarmname,params) 
      
   return(alarm)

#This is the parent message processor for AlarmProcessor and ShelfProcessor      
class Processor(object) :
   def __init__(self) :      
                 
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
         alarm = self.CreateAlarm(msg,init=True)
         
         #Assign this alarm to the topic/alarmname.
         #subsequent states of this alarmname will overwrite.
         #leaving us with the most recent
         self.initalarms[topic][alarm.GetName()] = alarm
         #Topic has finished loading.
         if (msg.offset() + 1 == consumer.GetHighOffsets(topic)) :
            consumer.topicloaded[topic] = True
   
   #Process the initial set of alarms.
   #This is implemented by the inherited classes
   def InitProcess(self) :
      pass
   
   #This is the worker thread that periodically checks for messages
   #after initial startup
   def GetAlarms(self) :
      msg = None
      consumer = self.kafkaconsumer
      try :         
         msg = consumer.GetMessage() 
      except :
         print("Message deserialization failed for {}".format(e))
         return
      
      return(msg)
   
   #Process the alarms as they come in.
   #Implemented by inherited classes
   def ProcessAlarms(self,msg) :
      pass
            
   #Create the new alarm as appropriate to the topic
   def CreateAlarm(self,msg,init=False) :
      topic = msg.topic()
      alarm = None      
      
      if (topic == "registered-alarms") :            
         alarm = self.RegisteredAlarm(msg)              
      if (topic == "active-alarms") :            
         alarm = self.ActiveAlarm(msg)         
      elif (topic == "shelved-alarms") :               
         alarm = self.ShelvedAlarm(msg)     
      return(alarm) 
        
   #We have received a message from the "active-alarms" topic
   def ActiveAlarm(self,msg,init=False) :
      
      kafkaconsumer = self.kafkaconsumer
      alarmname = kafkaconsumer.DecodeAlarmName(msg)
      msgtype = kafkaconsumer.DecodeMsgType(msg)
      
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
                     
      #And add it to the master list of active-alarms         
      AddActiveAlarm(alarm)
      return(alarm)
      
   #Received a message from the shelving topic. 
   def ShelvedAlarm(self,msg) :
      consumer = self.kafkaconsumer
      
      #When shelving an alarm, the msg is the alarm definition
      definition = consumer.DecodeMsgValue(msg)
      alarmname = consumer.DecodeAlarmName(msg)
      
      #It is possible that a shelved alarm comes in before it has been
      #registered. 
      alarm = FindAlarm(alarmname)
      
      #If the alarm has not been registered, create an empty one.
      if (alarm == None) :
         alarm = Alarm(alarmname,'shelved')
      
      #None, on the shelving topic = removed from shelf.          
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
 
      #Register the alarm. Even if one exists with the same name.
      AddRegAlarm(alarm)
      return(alarm)
   
   #STILL HAVEN'T DECIDED IF THIS IS NEEDED
   def IsRegistered(self,alarmname) :
      registered = True
      
      registered = False
      alarm = FindRegAlarm(alarmname) 
      if (alarm != None) :
         definition = alarm.definition
         if (definition is None) :
            registered = False
      
      return(registered)
       
