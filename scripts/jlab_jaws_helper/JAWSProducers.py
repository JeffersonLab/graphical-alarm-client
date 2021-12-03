from jlab_jaws_helper.JAWSConnection import *

class JAWSProducer(JAWSConnection) :
   """ JAWSConnection that PRODUCES and sends messages 
       
   """
   #NOTE: Most of this has been stolen from Ryan's examples
   def __init__(self,managername,topic) :
      """ Create a JAWSProducer instance
          
          :param topic: Name of topic
          :type topic: string
          :param name: name of producer
          :type name: string
      """
      super(JAWSProducer,self).__init__(topic)

      topic = self.topic
            
      self.hdrs = [('user', pwd.getpwuid(os.getuid()).pw_name),
         ('producer',managername),('host',os.uname().nodename)]

   def _create_producer(self) :
      config = None
           
      producer_config = {
                'bootstrap.servers'  : self.bootstrap_servers,
                'key.serializer'   : self.key_serializer,
                'value.serializer' : self.value_serializer,
                
               }
      producer = SerializingProducer(producer_config)
      return(producer)
      
   def send_message(self,params) :
      """ Send a message to a topic 
          :param params: message content
          :type params: types.SimpleNamespace()
          
          params must include:
            params.key (name of alarm)
            params.topic (topic to send message)
            params.value
            
      """
      
      producer = self.producer 
      
      producer.produce(topic=params.topic,value=params.value,key=params.key,
         headers=self.hdrs,on_delivery=self.delivery_report)
      producer.flush()
   
      

   #Create an acknowledge message
   def ack_message(self,name) :
      """ Create an acknowledgement message
          
          :param name: name of alarm
          :type name: string
  
      """
      #Build the message to pass to producer. 
      params = types.SimpleNamespace()
      params.value = None
      params.key = name
      params.topic = self.topic
      
      ### FOR TESTING PURPOSES ###
      ### Until active-alarms/alarm-state/latching works
      #params.value = AlarmStateValue(AlarmStateEnum['Active'])
      #print("VAL",params.value)
      #return
      #params.topic = "alarm-state"
      
      self.send_message(params)

   #Report success or errors
   def delivery_report(self,err, msg):
      
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered')
   
   
   
class OverrideProducer(JAWSProducer) :
   def __init__(self,managername,overridetype) :
      
      super(OverrideProducer,self).__init__(managername,'alarm-overrides')
      self.topic = 'alarm-overrides'
      self.key_serializer = \
         AlarmOverrideKeySerde.serializer(self.schema_registry)
      self.value_serializer = \
         AlarmOverrideUnionSerde.serializer(self.schema_registry)
      
      
      self.overridetype = OverriddenAlarmType[overridetype]
      
      self.params = types.SimpleNamespace()
      self.params.topic = self.topic
      
      
      self.producer = self._create_producer()
         
   def _get_params_value(self,msg) :
      value = AlarmOverrideUnion(msg)
      return(value)
   
   def _get_params_key(self,name) :
      key = AlarmOverrideKey(name,self.overridetype)
      print("KEY:",name)
      print("KEY:",self.overridetype)
      print("KEY:",key)
      return(key)

   def disable_message(self,name,comment) :
     
      msg = DisabledOverride(comment)
      self.params.key = self._get_params_key(name)
      self.params.value = self._get_params_value(msg) 
      self.send_message()
     
  
  
   def oneshot_message(self,name,reason,comments) :
      """ Create OneShot shelving message        
          :param name: name of alarm
          :type name: string
  
      """
      msg = ShelvedOverride(1,comments,ShelvedReason[reason],True)
      self.params.key = self._get_params_key(name)
      self.params.value = self._get_params_value(msg) 
      self.send_message()
   
   def shelve_message(self,name,expseconds,reason,comments=None) :
      
      now = int(time.time())
      timestampseconds  = now + expseconds
      
      timestampmillies = int(timestampseconds * 1000)
      
      msg = ShelvedOverride(timestampmillies,comments,ShelvedReason[reason],False)
      self.params.key = self._get_params_key(name)
      self.params.value = self._get_params_value(msg) 
      
      self.send_message()
      
      
   #Create an acknowledge message
   def ack_message(self,name) :
      """ Create an acknowledgement message
          
          :param name: name of alarm
          :type name: string
  
      """
      
      #self.params.key = OverriddenAlarmKey(name,self.overridetype)
      #Build the message to pass to producer. 
      self.params.key = self._get_params_key(name)
      self.params.value = None
      self.send_message()

   
   def send_message(self) :
         
      params = self.params
      print("KEY:",self.params.key)
      print("VAL:",self.params.value)
      print("TOP:",self.topic)
      print("HEA:",self.hdrs)
     # print("MSG:",params.value)
      #self.producer = SerializingProducer(producer_config)
      #self.send_message(params)
      producer = self.producer 
      
      producer.produce(topic=params.topic,value=params.value,key=params.key,
         headers=self.hdrs,on_delivery=self.delivery_report)
      producer.flush()
