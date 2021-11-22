""" 
.. currentmodule:: JAWSAlarm
.. autoclass:: JAWSAlarm
   :synopsis : Consolidated alarm object
.. moduleauthor::Michele Joyce <erb@jlab.org>
"""

from jlab_jaws.avro.subject_schemas.entities import *
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
      self.config = {}
      
      #If the msg is from a topic other than registered alarms,
      #create an alarm to be defined when the registered alarm comes in.
      if (msg == None) : 
         return   
      
      self.add_headers(msg)
      
      timestamp = get_msg_timestamp(msg)  
      self.config['type'] = {
         'state' : AlarmStateEnum.Normal, 
         'registered' : timestamp,
         'timeleft'   : None
      }       
      
      self._configure_alarm(get_msg_value(msg).__dict__)
   
   def calc_time_left(self) :
      
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
   
   def _configure_alarm(self,config) :
      """ Configure the alarm with the data from a topic
       
         :param config : alarm configuration from topic
         :type config : dict
      
      """   
      debug = False  
      if (self.get_name() != "alarm1") :
         debug = True
         return
     
      #Assign each key of the incoming configuration, to the
      #alarm. This is how the alarm is built up from any topic.
      if (config != None) :         
         for key in config :
            self.config[key] = config[key]
            if (key == "producer") :
               self.config['trigger'] = self.get_producer()
            if (key == "state") :
               self.config['state'] = self.get_state()
    #  if (self.get_name() != "alarm1") :
         
     #    return
      
      #Debug purposes
      if (self.get_name() != None) :
         print(self.get_name())
      
         for key in self.config :
            print("  ",key,"=>",self.config[key])  
         print("--") 
   
   def print_alarm(self) :
      if (self.get_name() != None) :
         print(self.get_name())
      
         for key in self.config :
            print("  ",key,"=>",self.config[key])  
         print("--") 
  
  
   def update_active(self,msg) :
      """ Update an alarm from the active-alarms topic
       
          :param msg : topic messge
          :type msg: 'cimpl.Message' (can be None) 
      
      """   
      msginfo = get_msg_value(msg) 
      timestamp = get_msg_timestamp(msg) 
      
      #Get severity and stat properties from an the topic
      #If msginfo is None, the alarm has been cleared     
      clear = {
         'sevr' : None,
         'stat' : None
      }
      if (msginfo != None) :
         dict = msginfo.msg.__dict__
         
         #include the time that the state changed.
         dict['statechange'] = timestamp      
      else :
         dict = clear
      
      #Update the alarm's configuration
      self._configure_alarm(dict)
      
   def update_override(self,msg) :
      
      msginfo = get_msg_value(msg) 
      timestamp = get_msg_timestamp(msg)
      key = get_msg_key(msg)
      msginfo = get_msg_value(msg)
      
      clear = {
         'override_date' : None,
         'override_type' : None,   
         'oneshot'       : None,
         'expiration'    : None,
      }
      
      if (msginfo != None) :
         dict = msginfo.msg.__dict__
         dict['override_date'] = timestamp
         dict['override_type'] = key.type.name
         
 
         if ("oneshot" in dict and dict['oneshot']) :
            dict['override_type'] = "Oneshot " + key.type.name
            dict['expiration'] = None
         
         elif ("expiration" in dict) :
            dict['expiration'] = convert_timestamp(dict['expiration'])
         
         headers = self.add_headers(msg)
         dict['overridden_by'] = headers['user']

      else :
         dict = clear
           
      self._configure_alarm(dict)
      
         
   def add_headers(self,msg) :
      
      
      headers = get_headers(msg)
      
      headerdict = {}
      if (headers is not None) :
         for header in headers :
            var = header[0]
            
            if (var == "producer") :
               var = "app"
               
            val = header[1].decode() #bytez.decode()header[1]
            headerdict[var] = val
      return(headerdict)    
   
   
   def update_state(self,msg) :
      """ Update an alarm from the state topic
       
       :param msg : topic messge
       :type msg: 'cimpl.Message' (can be None) 
      
      """     
      msginfo = get_msg_value(msg)     
      timestamp = get_msg_timestamp(msg) 

      dict = msginfo.__dict__
     
      dict['statechange'] = timestamp      
      self._configure_alarm(dict)
    
  
  
   #Update a registered alarm.
   def update_alarm(self,msg) :
      """ Update an alarm from the registered-alarms topic
       
       :param msg : topic messge
       :type msg: 'cimpl.Message' (can be None) 
      
      """  
      
      if (msg == None) : ## ***** NEED TO TEST REMOVE REGISTERED 
         return

      timestamp = get_msg_timestamp(msg)
      
      if (get_msg_value(msg) == None) :
         self.config['removed'] = timestamp
         
         #self.config['type'] = None
         return
      
      
      self.config['registered'] = timestamp
      self._configure_alarm(get_msg_value(msg).__dict__)
   
   def get_name(self) :
      """ Get the name of the alarm       
       :returns: name of the alarm (str)      
      """     
      return(self.name)
   
   #Does the alarm latch? 
   
   def get_latching(self) :    
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
   
   def get_status_summary(self) :
      # returns: state/sevr/latched
      state = self.get_state(name=True)
      sevr = self.get_sevr(name=True)
      latching = self.get_latching()
      
   
   def get_state(self,name=False,value=False) :      
      """ Get the current state of an alarm
          Note: By default this method returns the AlarmStateEnum 
       :param name : return the lower-case string name of the state 
       :param value: return the numeric value of the state
       
      """           
      #val = self.get_val('type')
      val = self.get_property('type',name,value)
      return(val)
   
   def get_state_change(self) :
      """ Get the timestamp of the most recent state change
          
       :returns : timestamp (str)
       
      """           
      return(self.get_property('statechange'))

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