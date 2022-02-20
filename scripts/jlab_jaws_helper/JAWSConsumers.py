"""! @brief Create a JAWSConsumer 

##
# @file JAWSConsumers.py
# @brief A JAWSConsumer subscribes to a specific topic to get updates
# @details Inherit from the JAWSConsumer to create a new consumer type
# for new topics.
"""

from jlab_jaws_helper.JAWSConnection import *
from jlab_jaws_helper.JAWSTopic import *

class JAWSConsumer(JAWSConnection) :
   """! JAWSConnection that subscribes to topics and consumes messages 
   """
   
   def __init__(self,topic,subscriber,init_state,update_state,monitor=True) :
      
      """! Create a JAWSConsumer instance
      @param topic The name of the topic (str)
      @param subscriber Name of app or user sending the message (str)      
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      @return a JAWSConsumer of the appropriate type
      """
            
      super(JAWSConsumer,self).__init__(topic)
  
      self.subscriber = subscriber
      self.topic = topic
      self.monitor = monitor
      self.init_state = init_state
      self.update_state = update_state
   
   def _create_event_table(self) :
      """! Each consumer has an event_table that can be 
          added to a thread to monitor the topic
      """
      ts = time.time()
      
      consumer_config = {
         'topic': self.topic,
         'monitor' : self.monitor,
         'bootstrap.servers'  : self.bootstrap_servers,
         'key.deserializer'   : self.key_deserializer,
         'value.deserializer' : self.value_deserializer,
         'group.id' : self.subscriber + " " + str(ts)
      }
      
      self.event_table = \
         EventSourceTable(consumer_config,self.init_state,self.update_state)
  
   def start(self) :
      """! Start the event_table monitoring
      """
      
      self.event_table.start()
                
   def stop(self) :
      """! Stop the event_table
      """
      self.event_table.stop()


class EffectiveRegistrationsConsumer(JAWSConsumer) :
   """! @brief Consumer for "effective-registrations" topic
   """
   def __init__(self,subscriber,init_state=None,update_state=None,monitor=True) :
      """! @brief Create a consumer for the "effective-registrations" topic
      @param subscriber       Name of application/user subscribing to topic
      @param init_messages    Callback providing initial state of the topic
      @param update_messages  Callback providing updated state
      @param monitor          whether or not to monitor the topic
      
      @return EffectiveRegistrationsConsumer
      """ 
      super(EffectiveRegistrationsConsumer,self).__init__('effective-registrations',
         subscriber,init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         EffectiveRegistrationSerde.deserializer(self.schema_registry)
        
      self._create_event_table()

class AlarmClassConsumer(JAWSConsumer) :
   """! @brief Consumer for "alarm-classes" topic
   """
   def __init__(self,subscriber,init_state=None,update_state=None,monitor=True) :
      """! @brief Consumer for "alarm-classes" topic
      @param subscriber       Name of application/user subscribing to topic
      @param init_messages    Callback providing initial state of the topic
      @param update_messages  Callback providing updated state
      @param monitor          whether or not to monitor the topic
      
      @return AlarmClassConsumer
      """ 
      super(AlarmClassConsumer,self).__init__('alarm-classes',subscriber,
         init_state,update_state,monitor)      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         AlarmClassSerde.deserializer(self.schema_registry)
         
      self._create_event_table()

 
class AlarmOverrideConsumer(JAWSConsumer) :
   """! @brief Consumer for the "alarm-overrides" topic
   """
   def __init__(self,subscriber,init_state=None,update_state=None,monitor=True) :
      """! @brief Consumer for the "alarm-overrides" topic
      @param subscriber       Name of application/user subscribing to topic
      @param init_messages    Callback providing initial state of the topic
      @param update_messages  Callback providing updated state
      @param monitor          whether or not to monitor the topic
      
      @return AlarmOverrideConsumer
      """ 

      super(AlarmOverrideConsumer,self).__init__('alarm-overrides',subscriber,
         init_state,update_state,monitor)
      
      self.key_deserializer = AlarmOverrideKeySerde.deserializer(self.schema_registry)
      self.value_deserializer = \
         AlarmOverrideUnionSerde.deserializer(self.schema_registry)
      
      if (init_state == None or update_state == None) :
         return  
      
      self._create_event_table()
   
   def set_callbacks(init_state,update_state) :
      self.init_state = init_state
      self.update_state = update_state
      self._create_event_table()
   
   def set_update_state(update_state) :
      self.update_state = update_state
      init_state = self.init_state
      if (init_state == None) :
         return
      self._create_event_table()
      
      

class EffectiveActivationsConsumer(JAWSConsumer) :
   """! @brief Consumer for the 'effective-activations' topic
   """   
   def __init__(self,subscriber,init_state=None,update_state=None,monitor=True) :
      """! @brief Consumer for the 'effective-activations' topic
       Args:
         subscriber (str)     : Name of application/user subscribing to topic
         init_messages   : Callback providing initial state of the topic
         update_messages : Callback providing updated state
         monitor         : whether or not to monitor the topic
      """ 

      super(EffectiveActivationsConsumer,self).__init__('effective-activations',subscriber,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         EffectiveActivationSerde.deserializer(self.schema_registry)
         
      self._create_event_table()


class AlarmRegistrationsConsumer(JAWSConsumer) :
   """ Consumer for the "alarm-registrations" topic
   """
   def __init__(self,subscriber,init_state=None,update_state=None,monitor=True) :
      """
       Args:
         subscriber (str)     : Name of application/user subscribing to topic
         init_messages   : Callback providing initial state of the topic
         update_messages : Callback providing updated state
         monitor         : whether or not to monitor the topic
      """ 

      super(AlarmRegistrationsConsumer,self).__init__('alarm-registrations',subscriber,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer('utf_8')
      self.value_deserializer = \
          AlarmRegistrationSerde.deserializer(self.schema_registry)
      self._create_event_table()


class AlarmActivationsConsumer(JAWSConsumer) :
   """ Consumer for the "alarm-activations" topic
       NOTE: This is the "actual" state of an alarm. Use the "effective-activations"
             topic which takes overrides into account
   """
   def __init__(self,subscriber,init_state=None,update_state=None,monitor=True) :
      """
       Args:
         subscriber (str)     : Name of application/user subscribing to topic
         init_messages   : Callback providing initial state of the topic
         update_messages : Callback providing updated state
         monitor         : whether or not to monitor the topic
      """ 

      super(AlarmActivationsConsumer,self).__init__('alarm-activations',subscriber,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         AlarmActivationUnionSerde.deserializer(self.schema_registry)

      self._create_event_table()

