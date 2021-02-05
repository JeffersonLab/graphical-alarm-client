import os
import pwd
import types
#import click
import time

# We can't use AvroProducer since it doesn't support string keys, see: https://github.com/confluentinc/confluent-kafka-python/issues/428
from confluent_kafka import avro, Producer, Consumer
from confluent_kafka.avro import CachedSchemaRegistryClient
from confluent_kafka.avro.serializer.message_serializer import MessageSerializer as AvroSerde

from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka import OFFSET_BEGINNING


class KafkaConnection(object) :
   def __init__(self) :
      
      self.value_schema_str = """
{
   "type"      : "record",
   "name"      : "ActiveAlarm",   
   "namespace" : "org.jlab.kafka.alarms",
   "doc"       : "Alarms currently alarming",
   "fields"    : [
     {
       "name"    : "priority",
       "type"    : {
         "type"      : "enum",       
         "name"      : "AlarmPriority",
         "namespace" : "org.jlab.kafka.alarms",
         "doc"       : "Enumeration of possible alarm priorities",
         "symbols"   : ["P1_LIFE","P2_PROPERTY","P3_PRODUCTIVITY", "P4_DIAGNOSTIC"]
       },
       "doc"     : "Alarm severity organized as a way for operators to prioritize which alarms to take action on first"
     },
     {
        "name"    : "acknowledged",
        "type"    : "boolean",
        "doc"     : "Indicates whether this alarm has been explicitly acknowledged - useful for latching alarms which can only be cleared after acknowledgement",
        "default" : false        
     }
  ]
}
"""
      
      self.value_schema = avro.loads(self.value_schema_str)
      #The topics to which we will subscribe
      self.topics = ['registered-alarms','active-alarms','shelved-alarms']
      
      #Magic Kafka configuration
      bootstrap_servers = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
      self.bootstrap_servers = bootstrap_servers
      
      conf = {'url': os.environ.get('SCHEMA_REGISTRY', 'http://localhost:8081')}
      schema_registry = CachedSchemaRegistryClient(conf)
      self.avro_serde = AvroSerde(schema_registry)
      self.params = types.SimpleNamespace()
      
   def GetTopic(self,msg) :
      return(msg.topic())
         
   def GetTopics(self) :
      return(self.topics) 

class KafkaProducer(KafkaConnection) :
   def __init__(self,topic=None) :
      super(KafkaProducer,self).__init__()
      
      self.serialize_avro = self.avro_serde.encode_record_with_schema
      self.topic = topic
      
      self.producer = Producer({
         'bootstrap.servers': self.bootstrap_servers,
         'on_delivery': self.delivery_report})
      
      self.hdrs = [('user',pwd.getpwuid(os.getuid()).pw_name),
     ('producer','set-active.py'),('host' ,os.uname().nodename)]

   
   def delivery_report(self,err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered')
   
   def SendMessage(self) :
      params = self.params
      topic = self.topic
      
      if (params.value is None) :
         val_payload = None
      else:
         val_payload = self.serialize_avro(topic, 
            self.value_schema, params.value, 
         is_key=False)

      self.producer.produce(topic=topic, value=val_payload, key=params.key, 
         headers=self.hdrs)
      self.producer.flush()
   
   def AckMessage(self,name,priority) :
      params = self.params
      params.key = name
      params.value = {"priority": priority,"acknowledged":True}
      self.SendMessage()
      
   def ClearMessage(self,name) :
      params = self.params
      params.key = name
      params.value = None
      self.SendMessage()
      
   def GetConnection(self) :
      return(self.producer)



        
class KafkaConsumer(KafkaConnection) :
   def __init__(self) :
      super(KafkaConsumer,self).__init__()
      #Make ourselves a consumer
      ts = time.time()
      self.consumer = Consumer({'bootstrap.servers': self.bootstrap_servers,
         'group.id': 'AlarmMonitor.py' + str(ts)})
      
      #And subscribe
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
      
      #if (msg is None or msg.error()) :     
       #  return(msg) 
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
   
   #Convert the timestamp into something readable
   def DecodeTimeStamp(self,msg) :
      timestamp = msg.timestamp()
      #comes in ms, so need to convert to seconds
      seconds = timestamp[1]/1000
      ts = time.ctime(seconds)
     
      return(ts)
   
   #Determine if all topics have completed loading.
   def TopicsLoaded(self) :
      loaded = True
      for topic in self.topics :
         if (not self.topicloaded[topic]) :
            loaded = False
      return(loaded)


        







