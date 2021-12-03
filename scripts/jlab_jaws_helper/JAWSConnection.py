""" 
.. module:: JAWSConnection
   :synopsis : Create JAWS kafka producers and consumers
   :notes : This module simplifies interaction with Kafka
.. moduleauthor::Michele Joyce <erb@jlab.org>
"""

import os
import pwd
import types
import pytz
import time

from datetime import datetime

# We can't use AvroProducer since it doesn't support string keys, see: https://github.com/confluentinc/confluent-kafka-python/issues/428

#  COMMON/GENERAL
from confluent_kafka.schema_registry import SchemaRegistryClient

from confluent_kafka import SerializingProducer

from jlab_jaws.avro.entities import *

from jlab_jaws.avro.serde import AlarmRegistrationSerde
from jlab_jaws.avro.serde import AlarmActivationUnionSerde
from jlab_jaws.avro.serde import EffectiveActivationSerde
from jlab_jaws.avro.serde import EffectiveAlarmSerde
from jlab_jaws.avro.serde import AlarmOverrideKeySerde, AlarmOverrideUnionSerde
from jlab_jaws.avro.serde import AlarmClassSerde
from jlab_jaws.avro.serde import EffectiveRegistrationSerde

#  CONSUMER
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from jlab_jaws.eventsource.table import EventSourceTable

def convert_timestamp(seconds) :
   """ Convert the message timestamp to local timezone.
       
       :param seconds : number of seconds
       :type seconds : int
       :returns date string for local timezone      
   """     
   #Work in utc time, then convert to local time zone.    
   ts = datetime.fromtimestamp(seconds//1000)
   utc_ts = pytz.utc.localize(ts)
   #Finally convert to EST.
   est_ts = utc_ts.astimezone(pytz.timezone("America/New_York"))
   return(est_ts)


#Convert the timestamp into something readable
def get_msg_timestamp(msg) :
   """ Get timestamp of message
       
       :param msg : topic messge
       :type msg: 'cimpl.Message'
       :returns timestamp in local time zone
   """        
   
   #timestamp from Kafka is in UTC
   timestamp = msg.timestamp()
#   print(msg.topic(),"GETMSGTIMESTAMP",convert_timestamp(timestamp[1]),"\n")
   return(convert_timestamp(timestamp[1]))

def get_headers(msg) :
   """ Get message headers
       
       :param msg : topic messge
       :type msg: 'cimpl.Message'
       :returns list of headers
   """           
   headers = msg.headers()
   return(headers)  
 
def get_alarmname(msg) :
   name = msg.key()
   
   if (not isinstance(name,str)) :
      name_dict = name.__dict__
      if ('name' in name_dict) :
         name = name_dict['name']
   return(name)

def get_msg_key(msg) :
   """ Get message key. 
       
       :param msg : topic messge
       :type msg: 'cimpl.Message'
       :returns key       
   """   
   key = msg.key()
#   topic = msg.topic()
 #  if (topic in CONSUMERS) :
  #    consumer = CONSUMERS[topic]
   #   key = consumer.get_msg_key(msg)         
   
   return(key)
 
def get_msg_value(msg) :
   """ Get message key. 
       
       :param msg : topic messge
       :type msg: 'cimpl.Message'
       :returns value object      
   """           
  
 #  print(msg.topic(),"GETMSGVALUE",msg.value(),"\n")
   return(msg.value())

def get_msg_topic(msg) :
   """ Get message topic
       
       :param msg : topic messge
       :type msg: 'cimpl.Message'
       :returns topic     
   """           
   return(msg.topic())   

def get_alarm_class_list() :
   """ Get list of valid alarm class names 
       
       :returns list AlarmClass member names
   """  
   return(AlarmClass._member_names_)
   
def get_location_list() :
   """ Get list of valid locations
       
       :returns list AlarmLocation member names       
   """     
   return(AlarmLocation._member_names_)
   
def get_category_list() :
   """ Get list of valid categories
       
       :returns list AlarmCategory member names
   """    
   return(AlarmCategory._member_names_)

def get_priority_list() :
   """ Get list of valid priorities
       
       :returns list AlarmPriority member names
   """     
   return(AlarmPriority._member_names_)

def get_override_reasons() :
   return(ShelvedReason._member_names_)
 
def get_override_types() :
   return(OverriddenAlarmType._member_names_)  
   
   
class JAWSConnection(object) :
   """ This class sets up the kafka connection for creating consumers and
       producers
   """
   def __init__(self,topic) :
      """ Create a kafkaconnection for the topic
       
       :param topic: Name of topic
       :type topic: string
      
      """           
      self.topic = topic
      
      #Magic Kafka configuration
      bootstrap_servers = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
      self.bootstrap_servers = bootstrap_servers
      
      conf = {'url': os.environ.get('SCHEMA_REGISTRY', 'http://localhost:8081')}
      self.schema_registry = SchemaRegistryClient(conf)
      self.params = types.SimpleNamespace()
      
      self.key_deserializer = StringDeserializer('utf_8')
      self.key_serializer = StringSerializer()

 
         





