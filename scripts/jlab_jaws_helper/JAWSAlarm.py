""" 
.. currentmodule:: JAWSAlarm
.. autoclass:: JAWSAlarm
   :synopsis : Consolidated alarm object
.. moduleauthor::Michele Joyce <erb@jlab.org>
"""

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
      self.config = {}
      
      #If the msg is from a topic other than registered alarms,
      #create an alarm to be defined when the registered alarm comes in.
      if (msg == None) : 
         return   
      
      print("\n",self.get_name()) 
      print(get_msg_value(msg).__dict__,"\n")
      
      self._add_headers(msg)
      
      timestamp = get_msg_timestamp(msg)  
      #Configure the alarm with the msg information
      self._configure_alarm(get_msg_value(msg).__dict__)
   
   def _add_headers(self,msg) :
      """ Add the msg headers to the alarm
      """
      
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
           
            if (key == "producer") :
               self.config['trigger'] = self.get_producer()
      
 
      self.print_alarm()
      
   
   def update_alarm(self,msg) :
      """ Update the alarm based on the msg topic
      """
      topic = msg.topic()
      
      #Dispense with the alarm as appropriate
      if (topic == 'effective-activations') :        
         self.update_effective_state(msg)
      elif (topic == "alarm-overrides") :
         self.update_override(msg)
      elif (topic == "alarm-activations") :
         self.update_actual_state(msg)
      elif (topic == "effective-alarms") :
         self.update_effective_alarms(msg)
      elif (topic == "alarm-classes") :
         print("NOT IMPLEMENTED YET")
  #    elif (topic == "effective-registrations") :
         
     #    self.update_effective_registration(msg) 
      elif (topic == "alarm-registrations") :
         self.update_registration(msg)
      
      return(None)
   
   def update_effective_state(self,msg) :
      """ The effective state is the state after all potential
          overrides have been applied. 
          Called with the effective-activations topic                 
      """        
      msginfo = get_msg_value(msg)
      timestamp = get_msg_timestamp(msg)
      state_dict = msginfo.__dict__
      
      state_dict['effective_state_change'] = timestamp
      state_dict['effective_state']  = state_dict['state'] #self.get_property(state_dict['state'],name=True)
      
      self.get_actual_state(state_dict['actual'])
        
      self.get_active_overrides(state_dict['overrides'])
      self._configure_alarm(state_dict)
         
   def update_override(self,msg) :
      """Called with the alarm-overrides topic
      """
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
      
   def update_actual_state(self,msg) :
      """ The raw/actual state of the alarm PRIOR to filters
          being applied. 
          Called with the effective-activations topic
      """
      msginfo = get_msg_value(msg)
      timestamp = get_msg_timestamp(msg)
     
      alarm_dict = {}    
      if (msginfo == None) :
         alarm_dict['actual'] = None
      else :         
         alarm_dict = msginfo.__dict__         
         alarm_dict['actual'] = alarm_dict['msg']
         alarm_dict.pop('msg')
      
      alarm_dict['actual_state_change'] = timestamp
      
      self._configure_alarm(alarm_dict)
      
      return
   
   def update_effective_alarms(self,msg) :
      """ NOT IMPLEMENTED YET
      """
      return
   def update_alarm_classes(self,msg) :
      """ NOT IMPLEMENTED NOT SURE IF BELONGS HERE
      """
      return
   
   def update_effective_registration(self,msg) :
      msginfo = get_msg_value(msg)
      msg_dict = msginfo.__dict__
      
     
      actual_dict = msg_dict['actual'].__dict__
      self._configure_alarm(actual_dict)
      
      
      
   def update_registration(self,msg) :
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
   
   def get_actual_state(self,actual) :
      actual_state = {}
      actual_state['sevr'] = None
      actual_state['stat'] = None
      
      if (actual != None) :
         actual_msg = actual.msg
         if ('sevr' in actual_msg.__dict__) :
               actual_state['sevr'] = actual_msg.sevr
               actual_state['stat'] = actual_msg.stat
     
      self._configure_alarm(actual_state)
      
   
   
   
   def get_active_overrides(self,alarm_override_set) :
      """ Helper script unpacks the alarm's override_set
      """
      current_overrides = {}
      
      override_dict = alarm_override_set.__dict__
      for override_type in override_dict :
         #if (override_dict[override_type] != None) :
         current_overrides[override_type] = override_dict[override_type]
      
      self._configure_alarm(current_overrides)   
  
      
   """ Setters and getters for the alarm
   """
   
   def get_name(self) :
      """ Get the name of the alarm       
       :returns: name of the alarm (str)      
      """     
      return(self.name)
      
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
         for key in self.config :
            
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