import os
import pwd
import types
import pytz
import time
import json

from utils import *
from datetime import datetime

# We can't use AvroProducer since it doesn't support string keys, see: https://github.com/confluentinc/confluent-kafka-python/issues/428
from confluent_kafka import avro, Producer, Consumer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.avro.serializer.message_serializer import MessageSerializer as AvroSerde

from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka import OFFSET_BEGINNING
from avro.schema import Field


def ConvertTimeStamp(seconds) :
      #Work in utc time, then convert to local time zone.
    
      ts = datetime.fromtimestamp(seconds//1000)
      utc_ts = pytz.utc.localize(ts)
      #Finally convert to EST.
      est_ts = utc_ts.astimezone(pytz.timezone("America/New_York"))
      return(est_ts)

class KafkaConnection(object) :
   def __init__(self) :
       
      self.categories = None
      self.locations = None
     
      self.topics = ['registered-alarms','active-alarms','shelved-alarms']
      self.schemamap = {}
      
      #Magic Kafka configuration
      bootstrap_servers = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
      self.bootstrap_servers = bootstrap_servers
      
      conf = {'url': os.environ.get('SCHEMA_REGISTRY', 'http://localhost:8081')}
      schema_registry = CachedSchemaRegistryClient(conf)
      
      
      self.avro_serde = AvroSerde(schema_registry)
      self.params = types.SimpleNamespace()
    
      #Access the latest schema
      for topic in self.topics :
         if (topic in self.schemamap) :
            continue
         
         self.schemamap[topic] = {}
         self.schemamap[topic]['value'] = None
         self.schemamap[topic]['key'] = None
         
         valueschema = topic + "-value"
         keyschema = topic + "-key" 
         try :          
           
            self.schemamap[topic]['value'] = \
               schema_registry.get_latest_schema(valueschema)[1]
            
            #Only "key schema" right now is the "active-alarms"
            if ("active" in topic) :
               self.schemamap[topic]['key'] = \
               schema_registry.get_latest_schema(keyschema)[1]
         
         except :
            print(topic,"FAILED!***")
            pass     
      
      
      latest_schema = self.schemamap['registered-alarms']['value']
      
      categories = latest_schema.fields[2].type.symbols
      locations = latest_schema.fields[1].type.symbols
      
      self.categories = categories
      self.locations = locations
   

      
   #Accessors
   def GetCategories(self) :
      return(self.categories)
      
   def GetLocations(self) :
      return(self.locations)
         
   def GetTopic(self,msg) :
      return(msg.topic())
         
   def GetTopics(self) :
      return(self.topics) 

#Create a KafkaProducer. This is a KafkaConnection that
#PRODUCES and sends messages NOTE: Most of this has been
#stolen from Ryan's examples
class KafkaProducer(KafkaConnection) :
   def __init__(self,topic=None) :
      super(KafkaProducer,self).__init__()
      
      self.serialize_avro = self.avro_serde.encode_record_with_schema
      self.topic = topic
      
      self.producer = Producer({
         'bootstrap.servers': self.bootstrap_servers,
         'on_delivery': self.delivery_report})
      self.hdrs = [('user', pwd.getpwuid(os.getuid()).pw_name),
         ('producer','AlarmManager'),('host',os.uname().nodename)]
   
   #Report success or errors
   def delivery_report(self,err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered')
   
   def UnShelveRequest(self,name) :
      params = self.params
      params.key =  name
      params.value = None
   
      self.SendShelfMessage()
      
   def ShelveMessage(self,name,reason,expiration) :
      params = self.params
      params.key = name
      params.value = {"expiration":expiration,"reason":reason}
      self.SendShelfMessage()
   
   #Create an acknowledge message
   def AckMessage(self,name,ack) :
      if (not "ACK" in ack) :
         ack = ack + "_ACK"         
     
      params = self.params
      params.key = {"name": name, "type": "EPICSAck"}
      params.value = {"msg": {"ack": ack}}
      
      self.SendAckMessage()
   
   def SendShelfMessage(self) :
      params = self.params
      topic = self.topic
      value_schema = self.schemamap[topic]['value']
      
      val_payload = None
      if (params.value != None) :
         val_payload = self.serialize_avro(topic,value_schema,params.value,
            is_key=False)
      self.producer.produce(topic=topic,value=val_payload,key=params.key,
         headers = self.hdrs)
      self.producer.flush()
      
   #Send a message
   def SendAckMessage(self) :
      params = self.params
      topic = self.topic
      
      value_schema = self.schemamap[topic]['value']
      key_schema = self.schemamap[topic]['key']
      
      if (params.value is None) :
         val_payload = None
      else:        
         val_payload = self.serialize_avro(topic, 
            value_schema, params.value, is_key=False)
      
      #Not all topics have an associated "key_schema"
      #If it doesn't, use the params.key
     
      key_payload = self.serialize_avro(topic, key_schema, params.key, 
            is_key=True)     
          
      self.producer.produce(topic=topic, value=val_payload, key=key_payload, 
         headers=self.hdrs)
      self.producer.flush()
   
   def GetConnection(self) :
      return(self.producer)


#Create a KafkaConsumer. A KafkaConnection that subscribes and
#receives messages. Again, most stolen from Ryan's examples        
class KafkaConsumer(KafkaConnection) :
   def __init__(self) :
      super(KafkaConsumer,self).__init__()
      
      #Make ourselves a consumer
      ts = time.time()
      self.consumer = Consumer({'bootstrap.servers': self.bootstrap_servers,
         'group.id': 'AlarmManager' + str(ts)})
      
      #And subscribe to the list of topics
      self.consumer.subscribe(self.topics,on_assign=self.my_on_assign)
      
      #Initialize variables
      self.topicloaded = {}  #lets us know when a topic has been loaded.
      self.initalarms = {}   #initial set of alarms
      self.highoffsets = {}  #? 
      
      #initialize topic dependent variables
      for topic in self.topics :
         self.topicloaded[topic] = False 
         self.initalarms[topic] = {}
      
      self.msgstate = {
         'registered-alarms' : {},
         'Alarming' : {},
         'Ack' : {},
         'AlarmingEPICS' : {},
         'AckEPICS' : {},
         'shelved-alarms' : {}
      }
 
   #We are assuming one partition, otherwise low/high would each be array and 
   #checking against high water mark would probably not work since other 
   #partitions could still contain unread messages. RYAN's MAGIC
   def my_on_assign(self,consumer, partitions):           
      for p in partitions:
         p.offset = OFFSET_BEGINNING
         low, high = consumer.get_watermark_offsets(p)
         self.highoffsets[p.topic] = high         
         if (high == 0) :          
            self.topicloaded[p.topic] = True
         consumer.assign(partitions)
   
   def GetHighOffsets(self,topic) :
      return(self.highoffsets[topic])
      
   def GetConnection(self) :
      return(self.consumer)
   
   #Get the next message from the producer
   def GetMessage(self,init=False) :
      consumer = self.GetConnection() 
      
      polltime = 0.25
      if (init) :
         polltime = 1.0
      msg = consumer.poll(polltime) 
      return(msg)
   
   #Decode the topic message.
   def DecodeMessage(self,msg) :
      
      topic = msg.topic()
      
      if (topic == "active-alarms") :
         key = self.avro_serde.decode_message(msg.key())  
         alarmname = key['name']
         msgtype = key['type']
         
      else :
         key = msg.key().decode('utf-8') 
         alarmname = key
         msgtype = topic
      
      value = self.avro_serde.decode_message(msg.value())
      timestamp = self.DecodeTimeStamp(msg)
      
      return(alarmname,value,msgtype)
   
   def DecodeMsgValue(self,msg) :
      value = self.avro_serde.decode_message(msg.value())
      return(value)
      
   def DecodeMsgType(self,msg) :
      topic = msg.topic()
      
      if (topic == "active-alarms") :
         key = self.avro_serde.decode_message(msg.key())  
         msgtype = key['type']
      else :
         msgtype = topic 
      return(msgtype)
      
      
   def DecodeAlarmName(self,msg) :
      topic = msg.topic()
      if (topic == "active-alarms") :
         key = self.avro_serde.decode_message(msg.key())  
         alarmname = key['name']
      else :  
         key = msg.key().decode('utf-8') 
         alarmname = key
      return(alarmname)
      

   #Convert the timestamp into something readable
   def DecodeTimeStamp(self,msg) :
      #timestamp from Kafka is in UTC
      timestamp = msg.timestamp()
      
      return(ConvertTimeStamp(timestamp[1]))
      #Work in utc time, then convert to local time zone.
      ts = datetime.fromtimestamp(timestamp[1]//1000)
      utc_ts = pytz.utc.localize(ts)
      
      #Finally convert to EST.
      est_ts = utc_ts.astimezone(pytz.timezone("America/New_York"))
  
      return(est_ts)
  
   #Determine if all topics have completed loading.
   def TopicsLoaded(self) :
      loaded = True
      for topic in self.topics :
         if (not self.topicloaded[topic]) :
            loaded = False
      return(loaded)

