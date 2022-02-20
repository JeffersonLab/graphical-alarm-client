""" ! @brief Create a JAWSProducer

##
#  @file JAWSProducers.py
#  @brief A JAWSProducer sends messages to the kafka-topic
#  @details Inherit from the JAWSProducer to send messages
#  @author Michele Joyce (erb@jlab.org)

"""

from jlab_jaws_helper.JAWSConnection import *

class JAWSProducer(JAWSConnection) :
   """! JAWSConnection that produces and sends messages to a topic        
   """
   #NOTE: Most of this has been stolen from Ryan's examples
   def __init__(self,subscriber,topic) :
      """! Create a JAWSProducer instance
      @param subscriber Name of app or user sending the message (str)
      @param topic The name of the topic (str)
      @return A JAWSProducer
      """
      super(JAWSProducer,self).__init__(topic)

      topic = self.topic            
      self._hdrs = [('user', pwd.getpwuid(os.getuid()).pw_name),
         ('producer',subscriber),('host',os.uname().nodename)]

   def _create_producer(self) :
      """! Create the kafka producer
      @return SerializingProducer
      """
      config = None
           
      producer_config = {
                'bootstrap.servers'  : self.bootstrap_servers,
                'key.serializer'   : self.key_serializer,
                'value.serializer' : self.value_serializer,               
      }
      producer = SerializingProducer(producer_config)
      return(producer)
      
   def send_message(self,params) :
      """! Send a message to a topic 
      @params params Message content
      @details At a minimum, params must include:
            params.key (name of alarm)
            params.topic (topic to send message)
            params.value           
      """    
      producer = self.producer      
      producer.produce(topic=params.topic,value=params.value,key=params.key,
         headers=self._hdrs,on_delivery=self.delivery_report)
      producer.flush()
   
   
   #Report success or errors
   def delivery_report(self,err, msg):      
      #Called once for each message produced to indicate delivery result.
      #Triggered by poll() or flush().
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered')
  
   
   
class OverrideProducer(JAWSProducer) :
   """! @brief Sends messages to the "alarm-overrides" topic
   """
   def __init__(self,subscriber,overridetype) :
      """! Create an OverrideProducer to send messages to the alarm-overrides topic
      @param subscriber Name of app or user sending the message
      @overridetype Type of override *** list values
      @return OverrideProducer
      """ 
      super(OverrideProducer,self).__init__(subscriber,'alarm-overrides')
      self.topic = 'alarm-overrides'
      self.key_serializer = \
         AlarmOverrideKeySerde.serializer(self.schema_registry)
      self.value_serializer = \
         AlarmOverrideUnionSerde.serializer(self.schema_registry)
      
      #OverriddenAlarmType(s) are part of the kafka-confluent message system
      self.overridetype = OverriddenAlarmType[overridetype]
      
      self.params = types.SimpleNamespace()
      self.params.topic = self.topic
      self.producer = self._create_producer()
         
   def _get_params_value(self,msg) :
      """! The override message value
      @param msg The kafka-confluent message
      @return AlarmOverrideUnion
      """
      value = AlarmOverrideUnion(msg)
      return(value)
   
   def _get_params_key(self,name) :
      """! Create the AlarmOverrideKey
      @param name The alarm name
      @return AlarmOverridekey
      """
      key = AlarmOverrideKey(name,self.overridetype)      
      return(key)

   def disable_message(self,name,comment) :
      """! Disable an alarm
      @param name The name of the alarm
      @param comment The reason/comment for disabling
      """
      msg = DisabledOverride(comment)
      self.params.key = self._get_params_key(name)
      self.params.value = self._get_params_value(msg) 
      self.send_message()

   def oneshot_message(self,name,reason,comments=None) :
      """! Create OneShot shelving message        
      @param name The name of the alarm
      @param reason The reason for the one_shot shelve
      @param comments Additional comments (can be None)
      """
      msg = ShelvedOverride(1,comments,ShelvedReason[reason],True)
      self.params.key = self._get_params_key(name)
      self.params.value = self._get_params_value(msg) 
      self.send_message()
   
   def shelve_message(self,name,expseconds,reason,comments=None) :
      """! Shelve alarm with expiration time
      @param name The name of the alarm
      @param expseconds The number of seconds before expiration
      @param reason The reason for the timed shelve
      """
      now = int(time.time())
      timestampseconds  = now + expseconds
      
      timestampmillies = int(timestampseconds * 1000)
      
      msg = ShelvedOverride(timestampmillies,comments,ShelvedReason[reason],False)
      self.params.key = self._get_params_key(name)
      self.params.value = self._get_params_value(msg) 
      
      self.send_message()
      
   def ack_message(self,name) :
      """! Create an acknowledgement message for a latched alarm
      @param name Name of the alarm
  
      """      
      #Build the message to pass to producer. 
      self.params.key = self._get_params_key(name)
      self.params.value = None
      self.send_message()

   
   def send_message(self) :
      """! Send the message to the topic
      """
      params = self.params
      producer = self.producer 
      
      producer.produce(topic=params.topic,value=params.value,key=params.key,
         headers=self._hdrs,on_delivery=self.delivery_report)
      producer.flush()
