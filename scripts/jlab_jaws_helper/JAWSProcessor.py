""" 
.. module:: JAWSProcessor
   :synopsis : Module to process incoming JAWSAlarms
.. moduleauthor::Michele Joyce <erb@jlab.org>
"""

from jlab_jaws_helper.JAWSAlarm import *
from jlab_jaws_helper.JAWSConsumers import *


class JAWSProcessor(object) :
   """ This class provides the means to process an alarm from any topic 
   """
   def __init__(self,topics) :
      """ Create a processor instance
       
       :param topics: list of topics to process
       :type topics : list
       
      """   
      self.topics = topics
      self.alarm_list = {}
      self.classname_list = []
   
   def get_topics(self) :
      """ Access the subscribed topics
         :returns: list of topics
      """
      return(self.topics)
      
   def _add_alarm(self,alarm) :
      """Add alarm to the processor's list of alarms
         :param alarm: alarm to add
         :type alarm : JAWSAlarm (or derivative)
         
      """
      self.alarm_list[alarm.get_name()] = alarm
      
   def _remove_alarm(self,alarmname) :
      """Remove an alarm from the processor's list of alarms
         :param alarmname: name of the alarm
         :type alarmname: str
      """
      if (alarmname in self.alarm_list) :
         del self.alarm_list[alarmname]
 
   def find_alarm(self,alarmname) :  
      """Find an alarm in the processor's list of alarms
         :param alarmname: name of the alarm
         :type alarmname: str
         :returns: JAWSAlarm | None
      """
      found = None
      
      if (alarmname in self.alarm_list) :
         found = self.alarm_list[alarmname] 
      return(found)
   
   def get_classname_list(self) :
      return(self.classname_list)
      
   def process_alarm(self,msg) :
      """ Process and incoming alarm
         :param msg: message from topic
         :type msg: 'cimpl.Message'
         :returns: JAWSAlarm
      """
      
      #The topic will indicate how to proceed
      topic = get_msg_topic(msg)
      topic_obj = self.topics[topic]
      topic_cfg = topic_obj.unpack_topic(msg)
      
      if ("class" in topic) :
         classname = topic_cfg['alarm_class_name']
         if (not classname in self.classname_list) :
            self.classname_list.append(classname)
         return(None)
   
      #The msg key is the name of the alarm
      name = get_alarmname(msg) 
      
      #Does the alarm already exist?
      alarm = self.find_alarm(name) 
      if (alarm is None) :
         alarm = JAWSAlarm(name,msg)
         self._add_alarm(alarm)
      
      alarm.update_alarm(topic_cfg)
      return(alarm)
 
