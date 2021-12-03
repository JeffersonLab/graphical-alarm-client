from jlab_jaws_helper.JAWSConnection import *

class JAWSConsumer(JAWSConnection) :
   """ JAWSConnection that subscribes to topics and consumes messages 
   """
   
   def __init__(self,topic,name,init_state,update_state,monitor=True) :
      
      """ Create a JAWSConsumer instance
          
          :param topic: Name of topic
          :type topic: string
          :param init_state: Callback providing initial state
          :type init_state: (callable(dict))
          :param update_state: Callback providing updated state
          :type update_state: (callable(dict))
          :param name: Name of consumer
          :type name: string
          :param monitor : Continue monitoring
          :type monitor: boolean
      """
            
      super(JAWSConsumer,self).__init__(topic)
  
      self.name = name
      self.topic = topic
      self.monitor = monitor
      self.init_state = init_state
      self.update_state = update_state
   
   def _create_event_table(self) :
      ts = time.time()

      consumer_config = {
         'topic': self.topic,
         'monitor' : self.monitor,
         'bootstrap.servers'  : self.bootstrap_servers,
         'key.deserializer'   : self.key_deserializer,
         'value.deserializer' : self.value_deserializer,
         'group.id' : self.name + " " + str(ts)
      }
      
      self.event_table = \
         EventSourceTable(consumer_config,self.init_state,self.update_state)
  
   def start(self) :
      """ Start the event_table monitoring
      """
      
      self.event_table.start()
                
   def stop(self) :
      """ Stop the event_table
      """
      self.event_table.stop()


class EffectiveRegistrationsConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(EffectiveRegistrationsConsumer,self).__init__('effective-registrations',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         EffectiveRegistrationSerde.deserializer(self.schema_registry)
        
      self._create_event_table()

class AlarmClassConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(AlarmClassConsumer,self).__init__('alarm-classes',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         AlarmClassSerde.deserializer(self.schema_registry)
         
      self._create_event_table()

 
class AlarmOverrideConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(AlarmOverrideConsumer,self).__init__('alarm-overrides',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = AlarmOverrideKeySerde.deserializer(self.schema_registry)
      self.value_deserializer = \
         AlarmOverrideUnionSerde.deserializer(self.schema_registry)
         
      self._create_event_table()


class EffectiveAlarmConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(EffectiveAlarmConsumer,self).__init__('effective-alarms',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         EffectiveAlarmSerde.deserializer(self.schema_registry)
         
      self._create_event_table()

class EffectiveActivationsConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(EffectiveActivationsConsumer,self).__init__('effective-activations',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         EffectiveActivationSerde.deserializer(self.schema_registry)
         
      self._create_event_table()

class ActivationsConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(ActivationsConsumer,self).__init__('alarm-activations',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         EffectiveActivationSerde.deserializer(self.schema_registry)
         
      self._create_event_table()

class AlarmRegistrationsConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      super(AlarmRegistrationsConsumer,self).__init__('alarm-registrations',name,
         init_state,update_state,monitor)
      
      if (init_state == None and update_state == None) :
         monitor = False
         
      self.key_deserializer = StringDeserializer('utf_8')
      self.value_deserializer = \
          AlarmRegistrationSerde.deserializer(self.schema_registry)
      self._create_event_table()


class AlarmActivationsConsumer(JAWSConsumer) :
   def __init__(self,name,init_state=None,update_state=None,monitor=True) :
      
      super(AlarmActivationsConsumer,self).__init__('alarm-activations',name,
         init_state,update_state,monitor)
      
      self.key_deserializer = StringDeserializer()
      self.value_deserializer = \
         AlarmActivationUnionSerde.deserializer(self.schema_registry)

      self._create_event_table()
