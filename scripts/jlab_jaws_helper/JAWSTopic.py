"""! @brief Create a JAWSTopic

##
# @file JAWSTopic.py
# @brief A JAWSTopic deciphers the messages from kafka topics
# @details Inherit from the JAWSTopic to implement new topics.
"""

import sys

from jlab_jaws_helper.JAWSProcessor import *
#from jlab_jaws_helper.topics.py import *
import configparser
import importlib

#Create the JAWSTopic.
#Each topic has is created as a child of JAWSTopic
#Topic names and JAWSTopic types are kept in the jaws_helper.cfg 
#file. JAWSTopic can be further extended if additional topics need to
#be implemented.
def create_JAWS_topic(subscriber,topic,init_msgs,
      update_msgs, monitor, *args,**kwargs) :
   
   """! This method creates JAWSTopic of the correct type
   @details Each topic has is created as a child of JAWSTopic 
   Topic names and JAWSTopic types are kept in the jaws_helper.cfg 
   file. JAWSTopic can be further extended if additional topics need to
   be implemented.
  
   @param topic The name of the topic (str)    
   @param subscriber Name of app or user subscribed to topic (str)
   @param init_state Callback providing initial state
   @param update_state Callback providing updated state
   @param monitor True/False continue to monitor after connection
   @return a JAWSTopic of the appropriate type
      
   """
   
   
   #The following bit of code, allows us to create the 
   #correct JAWSTopic type, using a string from the config
   #file. 

   jaws_topic = None   
   
   topic_config = _get_config(topic)
   
   if (topic_config == None) :
      return(jaws_topic)
  
   #topic_type is one of the attributes
   topic_type = topic_config['topic_type']
   module_name = __name__
   module = sys.modules[module_name]
   jaws_topic = \
         getattr(module,topic_type)(subscriber,init_msgs,update_msgs,monitor)

   return(jaws_topic)

def get_config(topic=None) :
   print("GET_CONFIG")
   
def _get_config(topic=None) :
   """! This library includes a file that defines topic definitions for this library. 
   @param topic Name of the topic. If None, all topics are return.
   @return Map between the topic name and the configuration file definitions
       example:
         [effective-registrations]
         topic_type    : EffectiveRegistrationsTopic 
         consumer_type : EffectiveRegistrationsConsumer
         description   : ""
      
   """        
   #Reads the configuration file.
   config = configparser.ConfigParser()
   config.read("/scripts/jlab_jaws_helper/jaws_helper.cfg")
     
   config_sections = config.__dict__['_sections']  
   if (topic != None and not topic in config_sections) :
      return(None)   
   if (topic == None) :
      topic_cfg = config_sections
   else :
      topic_cfg = config_sections[topic]   
   return(topic_cfg)

def get_implemented_topics() :
   """! Get the list of topics that have been implemented
   @return List of valid topic names
   """
   return(list(_get_config()))

def get_topic_defs() :
   return(_get_config())
   
           
class JAWSTopic(object) :
   """! Encapsulate a JAWSTopic.  
   """   
   def __init__(self,subscriber,topic,init_messages,
      update_messages, monitor, *args,**kwargs) :
               
      """! Create a JAWSTopic 
      @param subscriber (str)     : Name of application/user subscribing to topic
      @param topic (str)          : Name of topic
      @param init_messages   : Callback providing initial state of the topic
      @param update_messages : Callback providing updated state
      @param monitor         : whether or not to monitor the topic
      
      @return a JAWSTopic of correct type
      """ 
      self.init_messages = init_messages
      self.update_messages = update_messages
      self.subscriber = subscriber 
      self.topic_name = topic
      self.monitor = monitor
      
      #configuration data for the topic
      self.topic_def = _get_config(topic)     
      self.description = self.topic_def['description']
      self.consumer = self._create_consumer()
       
   def _create_consumer(self) :
      """! Create the the kafka-consumer type for the topic.
      @note this is defined in the topic_def 
      @return JAWSConsumer
      """
      subscriber = self.subscriber
      topic = self.topic_name
      init_msgs = self.init_messages
      update_msgs = self.update_messages
      monitor = self.monitor
      
      #This allows us to change "consumer_type", a string,
      #into the appropriate class object
      module_name = "jlab_jaws_helper.JAWSConsumers"    
      consumer_type = self.topic_def['consumer_type']
      module = importlib.import_module(module_name)
      
      #Create the consumer
      consumer = \
         getattr(module,consumer_type)(subscriber,init_msgs,update_msgs,monitor)
      return(consumer)
 
   def start_monitor(self) :
      """! Start the JAWSConsumer
      @note Even if monitor = False, need to start the topic to get the
      first set of messages
      """
      self.consumer.start()

   def get_topic_name(self) :
      """! Access the name of the topic
      """
      return(self.topic_name)
           
   def get_consumer(self) :
      """! Access the topic's kafka-consumer 
      """
      return(self.consumer)
      
   def _unpack_message(self,msg) :
      """! Convert a generic message to a dictionary
      @param message : kafka-topic message
      @return dictionary of unpacked message
      """
      message_cfg = {}
      if (msg != None) :
         message_info = msg.__dict__
         for key in message_info :
            message_cfg[key] = message_info[key]    
      return(message_cfg)
   
   def _message_timestamp(self,msg) :     
      """! Add a message timestamp to definition
      @param msg : kafka-topic message
      @return updated configuration
      """
      msg_time = {}
      if (msg == None) :
          msg_time[self.topic_name + "-topic"] = None
      else :
         timestamp = get_msg_timestamp(msg)
         msg_time[self.topic_name + "-topic"] = timestamp
      
      return(msg_time)
   
   def get_header(self,msg,header_attr) :
      """! Get a value for a specific header attribute
      @param message : kafka-topic message
      @param header_attr (str) : requested header attribute
      """
      headers = self.add_headers(msg)
      val = None
      if (header_attr in headers) :
         return(headers[header_attr])
      
   def add_headers(self,msg) :
      """! Add the msg headers to the topic configuration
      @param msg : kafka-topic message
      """
      headerdict = {}
      if (msg == None) :
         return(headerdict)
      headers = get_headers(msg)            
      if (headers is not None) :
         for header in headers :
            var = header[0]
                  
            if (var == "producer") :
               var = "app"            
            val = header[1].decode() #bytez.decode()header[1]
            headerdict[var] = val
      
      return(headerdict)  
   
   def unpack_topic(self,msg=None) :
      """! Update the topic cfg with the information common to all topics
      @param msg kafka-topic message
      @return topic configuration extracted from message
      """
      topic_cfg = {}
      #Add the header topics     
      headers = self.add_headers(msg)
      topic_cfg.update(headers)
         
      #Add a topic time stamp to the topic_cfg
      topic_cfg.update(self._message_timestamp(msg))
      return(topic_cfg)
  
class RegistrationTopic(JAWSTopic) :
   """! Common parent of the Active and Effective Registrations topics
   """
   def __init__(self,subscriber,topic,init_messages,
      update_messages, monitor=False, *args,**kwargs) :
      """! Create a RegistrationTopic
      
      @param subscriber Name of app or user sending the message (str)  
      @param topic The name of the topic (str)        
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return a RegistrationTopic
      """ 
      super(RegistrationTopic,self).__init__(
         subscriber,topic,init_messages,update_messages,monitor,*args,**kwargs)
   
   def unpack_topic(self,msg=None) :
      """! Update the topic cfg with the information common RegistrationTopics
      @param msg kafka-topic message
      @return topic configuration extracted from message
      """
      
      #Initialize the topic configuration 
      topic_cfg = super().unpack_topic(msg)           
      if (msg == None) :
         return(topic_cfg)
            
      timestamp = get_msg_timestamp(msg)
      msg_value = get_msg_value(msg)
      
      #The alarm has been removed
      if (msg_value == None) :        
         topic_cfg['removed'] = timestamp
      else :
         #alarm has been added or edited
         topic_cfg.update(get_msg_value(msg).__dict__)
         topic_cfg['registered'] = timestamp    
      return(topic_cfg)

class AlarmRegistrationsTopic(RegistrationTopic) :
   """ Bare definition of an alarm. Without having applied meta-data
   """
   def __init__(self,subscriber,init_messages,
      update_messages, monitor=False, *args,**kwargs) :
      """! Create an AlarmRegistrationTopic
      
      @param subscriber Name of app or user sending the message (str)  
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return an AlarmRegistrationTopic
      """     
      super(AlarmRegistrationsTopic,self).__init__(
         subscriber,"alarm-registrations", init_messages,
         update_messages, monitor,*args,**kwargs)
    
   def unpack_topic(self,msg=None) :
      """! Unpack the topic's message. 
      @param msg kafka-topic message
      @return topic_info key=>value dictionary
      """
      #Initialize the topic configuration 
      topic_cfg = super().unpack_topic(msg)           
      if (msg == None) :
         return(topic_cfg)
            
      timestamp = get_msg_timestamp(msg)
      msg_value = get_msg_value(msg)
      
      #The alarm has been removed
      if (msg_value == None) :        
         topic_cfg['removed'] = timestamp
      else :
         #alarm has been added or edited
         topic_cfg.update(get_msg_value(msg).__dict__)
         topic_cfg['registered'] = timestamp    
      
      return(topic_cfg)
  
      
class EffectiveRegistrationsTopic(RegistrationTopic) :
   """! The processed registration topic
   @note The effective-registrations topic is the best topic
         to subscribe to for a complete alarm definition
   """
   def __init__(self,subscriber,init_messages,
      update_messages, monitor, *args,**kwargs) :
      """! Create an EffectiveRegistrationsTopic
      
      @param subscriber Name of app or user sending the message (str)  
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      @param registration - specific 
      @return an EffectiveRegistrationTopic
      """     
      super(EffectiveRegistrationsTopic,self).__init__(
         subscriber,"effective-registrations",init_messages,
         update_messages, monitor, *args,**kwargs)
   
 
   def unpack_topic(self,msg=None,registration_name='calculated') :  
      """! Unpack the topic's message. 
      @param msg kafka-topic message
      @param registration_name Name of specific registration
      @return topic_info key=>value dictionary
      """
      topic_cfg = super().unpack_topic(msg)
      #If the alarm is being removed from the system, the update to the
      #alarm will be different.
      if (msg != None) :
         msg_value = get_msg_value(msg)       
         if (msg_value != None) :
            topic_cfg.update(get_msg_value(msg).__dict__)
            
            #Use the "calculated" attribute of the msg
            reg_cfg = topic_cfg[registration_name]
            reg_info = self.unpack_registration(reg_cfg)
            
            topic_cfg.update(reg_info)
      
      #self._unpack_class(topic_cfg['alarm_class'])
      return(topic_cfg)
   
  
   def unpack_registration(self,reg_definition) :
      """! Unpack one of the registration definitions in the message
      @note: There are three sets of "registrations" in the 
          EffectiveRegistration topic messages. 
          Use the "calculated" attribute for the finalized
          registration -- after all logic applied
      @param reg_cfg (jlab_jaws.avro.entities.AlarmRegistration)
      @return : dictionary with registration unpacked
         
      """
      
      reg_cfg = {}
      
      if (reg_definition != None) :        
         reg_info = self._unpack_message(reg_definition)
         reg_cfg.update(reg_info)
         
         producer = reg_info['producer']      
         producer_info = self._unpack_producer(producer)
 
         reg_cfg.update(producer_info)                      
      
      return(reg_cfg)

   def _unpack_producer(self,producer) :
      """! Unpack the producer information in the registration.
      @details Extracts the 'trigger' attribute from the producer object
      @param jlab_jaws_producer
      @return dictionary with producer unpacked 
      """
      producer_cfg = {}
      if (producer != None) :
         
         producer_cfg['trigger'] = None
         if (isinstance(producer,EPICSProducer)) :
            producer_cfg['trigger'] = producer.pv
         elif (isinstance(producer,CALCProducer)) :
            producer_cfg['trigger'] = producer.expression
      return(producer_cfg)
     

class AlarmOverrideTopic(JAWSTopic) :
   """! Implementation of the AlarmOverrideTopic
   """
   def __init__(self,subscriber,init_messages,
      update_messages,monitor=False,*args,**kwargs) :
      """! Create an AlarmOverrideTopic
      
      @param subscriber Name of app or user sending the message (str)  
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return an AlarmOverrideTopic
      """     
      super(AlarmOverrideTopic,self).__init__(subscriber,"alarm-overrides",init_messages,
         update_messages,monitor,*args,**kwargs)
   
      
   def unpack_topic(self,msg=None) :
      """! Unpack the topic's message. 
      @param msg kafka-topic message
      @return topic_info key=>value dictionary
      """

      topic_cfg = super().unpack_topic(msg)
      if (msg == None) :
         return(topic_cfg)
      
      msg_info = get_msg_value(msg)
      timestamp = get_msg_timestamp(msg)
      key_info = get_msg_key(msg)
      
      clear_override = {
         'override_date' : None,
         'override_type' : None,   
         'oneshot'       : None,
         'expiration'    : None,
         'overridden_by' : None
      }
   
      #Unpack the override information 
      if (msg_info != None) :         
         topic_cfg = msg_info.__dict__
         topic_cfg['override_date'] = timestamp
         
         override_type = self.get_override_type(key_info)
         topic_cfg['override_type'] = override_type
         
         if ('oneshot' in topic_cfg and topic_cfg['oneshot']) :
            topic_cfg['override_type'] = "Oneshot " + override_type
            topic_cfg['expiration'] = None
            
         elif ('expiration' in topic_cfg) :
            exp_seconds = topic_cfg['expiration']         
            topic_cfg['expiration'] = convert_timestamp(exp_seconds)
                
         headers = self.add_headers(msg)
         if (headers != None) :
            topic_cfg.update(headers)
         topic_cfg['overridden_by'] = self.get_header(msg,'user')
      
      else :
         topic_cfg = clear_override
      
      return(topic_cfg)
    
             
   def get_override_type(self,override_key) :
      """ Decipher the override type
      """
      override_type = override_key.type.name


class AlarmClassTopic(JAWSTopic) :
   """ Implement "alarm-classes" topic
   """
   def __init__(self,subscriber,init_messages,
      update_messages,monitor=False,*args,**kwargs) :
      """! Create an AlarmClassTopic 
      @details Alarm class defaults are applied to individual alarms
      
      @param subscriber Name of app or user sending the message (str)  
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return an AlarmClassTopic
      """     
      super(AlarmClassTopic,self).__init__(subscriber,"alarm-classes",
         init_messages,update_messages,monitor,*args,**kwargs)
      
      #Keep a list of class names
      self.classnames = []
      
   def unpack_topic(self,msg=None) :
      """! Unpack the topic's message. 
      @param msg kafka-topic message
      @return topic_info key=>value dictionary
      """
      topic_cfg = super().unpack_topic()
      
      if (msg != None) :
         class_name = get_msg_key(msg)
         
         class_info = get_msg_value(msg).__dict__
         
         class_info['alarm_class_name'] = class_name
         topic_cfg.update(class_info)
        
         self.classnames.append(class_name)
         
      return(topic_cfg)
   
   def get_classname_list(self) : 
      
      
      classnames = self.classnames
      
      return(classnames)
   
   
   
class ActivationsTopic(JAWSTopic) :
   """ Common parent of the Alarm and Effective Activations
   """ 
   def __init__(self,subscriber,topic,init_messages,
      update_messages, monitor=False, *args,**kwargs) :
      """! Create an Activations
      @details Alarm class defaults are applied to individual alarms
      
      @param subscriber Name of app or user sending the message (str)  
      @param topic Name of activations topic
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return an ActivationsTopic
      """      
      super(ActivationsTopic,self).__init__(
         subscriber,topic,init_messages,update_messages,monitor,*args,**kwargs)
   
  
   def unpack_topic(self,msg,topic_key=None,source_key=None) :
      """! Update the topic cfg with the information common ActivationTopics
      @param msg kafka-topic message
      @param topic_key  The name of the topic_cfg key that will be set
      @param source_key The name of the source key 
      @return topic configuration extracted from message
      
      topic_cfg = super().unpack_topic(msg,'actual_state_change','msg')
      """    
      topic_cfg = super().unpack_topic(msg)
      topic_cfg.update(self._unpack_actual())
      
      #Assign the timestamp and state
      if (msg != None) :
         timestamp = get_msg_timestamp(msg)
         topic_cfg[topic_key] = timestamp
         alarm_msg = get_msg_value(msg)
         
         if (alarm_msg != None) :
            topic_cfg.update(get_msg_value(msg).__dict__)
            actual = topic_cfg[source_key]        
            actual_info = self._unpack_actual(actual)
            topic_cfg.update(actual_info)
   
      return(topic_cfg)

   def _unpack_actual(self,actual=None) :
      """! Initialize the actual_cfg dictionary
      @param actual The actual state of 
      @return topic configuration extracted from the "actual" object
      """
      actual_cfg = {}
      actual_cfg['actual_state'] = actual
      actual_cfg['actual_state_change'] = None
      actual_cfg['sevr'] = None
      actual_cfg['stat'] = None
      
      return(actual_cfg)

class AlarmActivationsTopic(ActivationsTopic) :
   """! Implement the AlarmActivationsTopic (actual state)
   """
   def __init__(self,subscriber,init_messages,
      update_messages, monitor=False, *args,**kwargs) :
      """! Create an AlarmActivationsTopic
      
      @details The alarm-activations topic provides the "actual state" 
      Which may be different than the "effective-activation state" - 
      the state of the alarm after filters/shelving/delays have been applied.
           
      @param subscriber Name of app or user sending the message (str)  
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return an ActivationsTopic
      """      
      super(AlarmActivationsTopic,self).__init__(
         subscriber,"alarm-activations",init_messages,
         update_messages, monitor, *args,**kwargs)    
   
   def _unpack_actual(self,actual=None) :
      """! Unpack the actual alarm state
      @param actual The message portion associated with the actual alarm state
      @return topic configuration extracted from message
      """
      actual_cfg = super()._unpack_actual(actual)
      
      if (actual != None) :
         
         expand = self._unpack_message(actual)
         
         if (expand != None) :
            actual_cfg.update(expand)
               
      #if there is a "msg" attribute in the topic_cfg, replace
      #with an unambiguous name ('actual_state')
      if ('msg' in actual_cfg) :
         actual_cfg.pop('msg')

      return(actual_cfg)  

   def unpack_topic(self,msg) :
      """! Unpack the topic's message. 
      @param msg kafka-topic message
      @return topic_info key=>value dictionary
      """     
      topic_cfg = super().unpack_topic(msg,'actual_state_change','msg')
      return(topic_cfg)

class EffectiveActivationsTopic(ActivationsTopic) :
   """ Implement the EffectiveActivationsTopic (effective state)
   """
   
   def __init__(self,subscriber,init_messages,
      update_messages, monitor=False, *args,**kwargs) :
      """! Create an EffectiveActivationsTopic
      
      @details The effective-activations topic provides the "effective-state" 
      of an alarm after filters/shelving/delays have been applied.  
      
      @note The effective-activations topic messages also contain the information 
      about the "actual_state" 
           
      @param subscriber Name of app or user sending the message (str)  
      @param init_state Callback providing initial state
      @param update_state Callback providing updated state
      @param monitor True/False continue to monitor after connection
      
      @return an EffectiveActivationsTopic
      """      
      super(EffectiveActivationsTopic,self).__init__(
         subscriber,"effective-activations",init_messages,
         update_messages, monitor, *args,**kwargs)    
   
   def unpack_topic(self,msg=None) :
      """! Unpack the topic's message. 
      @param msg kafka-topic message
      @return topic_info key=>value dictionary
      """     
      topic_cfg = super().unpack_topic(msg,'effective_state_change','actual')
      
      #What is the "effective_state?" In "none" -- effective state is clear
      eff_state = None
      if ('state' in topic_cfg) :
         eff_state = topic_cfg['state']
      
      topic_cfg['effective_state'] = eff_state
      
      #Unpack the override information contained in the message
      overrides = topic_cfg['overrides']
      override_info = self._unpack_message(overrides)
      if (override_info != None) :
         topic_cfg.update(override_info)
      
      
      #Update the topic with the latest info from the message
      return(topic_cfg)
   
   def _unpack_actual(self,actual=None) :
      """! Unpack the actual alarm state
      @param actual The message portion associated with the actual alarm state
      @return topic configuration extracted from message
      """
      actual_cfg = super()._unpack_actual(actual)
       
      if (actual != None) :
         actual_info = actual.__dict__
         actual_msg = actual_info['msg']
         if (isinstance(actual_msg,SimpleAlarming)) :
            actual_cfg['actual_state'] = "ALARM"
         elif (isinstance(actual_msg,EPICSAlarming)) :
            actual_cfg['actual_state'] = "ALARM"
         expand = self._unpack_message(actual_msg)
         actual_cfg.update(expand)
   
      return(actual_cfg)
 