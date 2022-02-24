""" 
.. currentmodule:: JAWSAlarm
.. autoclass:: JAWSAlarm
   :synopsis : Consolidated alarm object
.. moduleauthor::Michele Joyce <erb@jlab.org>
"""

import collections 
from jlab_jaws.avro.entities import *
from jlab_jaws_helper.JAWSConnection import *

class JAWSAlarm(object) :
   """ This class encapulates properties from all topics 
   """

   def __init__(self,name,msg=None) :
      
      """ 
         .. automethod:: __init__
         .. rubric:: Methods
         
         Create a JAWSAlarm instance
         Parameters: 
            name (str) : name of the alarm
            msg ('cimpl.Message'/None) : topic message
      
      """      
      self.name = name  
      
      headers = self._add_headers(msg)
      self.config = self._add_headers(msg)
      
      #Configure the alarm with the msg information
      self._configure_alarm(get_msg_value(msg).__dict__)
   
   def _add_headers(self,msg) :
      """ Add the msg headers to the alarm
      """
      headers = get_headers(msg)
      
      headerdict = collections.OrderedDict()
      if (headers is not None) :
         for header in headers :
            var = header[0]
            
            if (var == "producer") :
               var = "app"
               
            val = header[1].decode() #bytez.decode()header[1]
            headerdict[var] = val
      return(headerdict)    
   

   def _configure_alarm(self,config) :
      """ Configure the alarm with the data from a topic
       
         :param config : alarm configuration from topic
         :type config : dict
      
      """    
      #Assign each key of the incoming configuration, to the
      #alarm. This is how the alarm is built up from any topic.
      if (config != None) :         
         for key in config :            
            self.config[key] = config[key]
      
      return
      if (self.get_name() == "alarm1") :
         self.print_alarm()
  
  
   def update_alarm(self,config) :
      """ Update the alarm with new configuration
         :param config : alarm configuration from topic
         :type config : dict
      """
      self._configure_alarm(config)
   
   
   """ Setters and getters for the alarm
   """
   

      
  
   
   def get_name(self) :
      """ Get the name of the alarm       
       :returns: name of the alarm (str)      
      """     
      return(self.name)
   
  
   def get_latch_state(self) :
      latched = self.get_property('latched');
      return(latched)
   
   def get_latching(self) :    
      """ Is the alarm a "latching" alarm?       
       :returns: True/False
      """           
      latching = self.get_property('latching')
      
      islatching = True
      if (latching == None or not latching) :
         islatching = False
      return(islatching)

   def get_producer(self) :
      """ Get the producer for the alarm
       :returns: producer definition
      """
      
      producer = self.get_val('producer')
      if (isinstance(producer,EPICSProducer)) :
         return(producer.pv)
      
      if (isinstance(producer,CALCProducer)) :
         return(producer.expresssion)
      
      return(str(producer))
      
   def get_state(self,name=False,value=False) :      
      """ Get the current state of an alarm
          Note: By default this method returns the AlarmStateEnum 
       :param name : return the lower-case string name of the state 
       :param value: return the numeric value of the state
       
      """           
      #val = self.get_val('type')
      val = self.get_property('state',name,value)
      return(val)
   
   def get_state_change(self) :
      """ Get the timestamp of the most recent state change
          
       :returns : timestamp (str)
       
      """           
      return(self.get_property('statechange'))
   
                           
   def get_actual_state(self) :      
      """ Get the 'actual_state' (raw/unprocessed) state of the alarm
      """
      return(self.get_property('actual_state'))
        
     
   def get_effective_state(self) :
      """ Get the 'effective_state' (processed) state of the alarm
      """ 
      state = self.get_property('effective_state')
      return(self.get_property('effective_state').name)
   
                                 
   def get_sevr(self,name=False,value=False) :
      """ Get the severity of an alarm - if SEVR is not 
          applicable, returns "ALARM" 
          Note: By default this method returns the EPICSSEVR.
          
       :param name : return the name of the severity
       :param value: return the numeric value of the severity
       
      """           
      state = self.get_state(name=True)
      
      val = self.get_property('sevr',name,value)
      if (val == None and not "normal" in state) :
         val = "ALARM"
      return(val)
      
    
   def get_property(self,alarmproperty,name=False,value=False) :
      """ Generic fetcher for property
                    
       :param property : property of interest
       :type property: string
       :param name : return the string name of the property
       :param value: return the numeric value of the property
       
      """         
      
      debug = False
      val = self.get_val(alarmproperty)
      if (val != None) :
         if (isinstance(val,str) or isinstance(val,int) or isinstance(val,dict)) :
        
            return(val)
         if (name) :
            return(val.name)
         elif (value) :
            return(val.value)
      return(val)        
  
   def get_val(self,alarmproperty) :
      """ Generic fetcher for property
                    
       :param property : property of interest
       :type property: string
       
      """ 
               
      val = None
      
      if (alarmproperty == "name") :
         return(self.get_name())
      if (self.config != None and alarmproperty in self.config) :
         val = self.config[alarmproperty]
      
      
      return(val)
      
   def print_alarm(self) :
      """ Print the current configuration of the alarm
      """
      if (self.get_name() != None) :
         print(self.get_name())
         for key in sorted(self.config.keys()) :
            
            print("  ",key,"=>",self.config[key])  
         print("--") 
   
   def calc_time_left(self) :
      """ Calculate the amount of time left for a shelved alarm
      """
      alarm = self
      timeleft = None
      exp = self.get_property("expiration")
      if (exp != None) :
         now = convert_timestamp(int(time.time()) * 1000)
         if (now < exp) :
            timeleft = exp - now
      
      self._set_time_left(timeleft)
     
      return(self)
   
   def _set_time_left(self,timeleft) :
      self.config['timeleft'] = timeleft