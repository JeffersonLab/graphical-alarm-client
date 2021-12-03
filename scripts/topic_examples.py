#!/usr/bin/env python3
""" 
This simple example 
1: connects to the user's topic(s) of choice.
2. builds the alarm based on the information provided by each topic
3. displays the resulting alarm configurations 

examples:
topic_examples.py -list_topics  #list the value

NOTE: This example script can only *monitor* one topic at a time. 
Monitoring of multiple topics are best with threads. 


"""
import os
import sys
import argparse

from jlab_jaws_helper.JAWSAlarm import *
from jlab_jaws_helper.JAWSProcessor import JAWSProcessor
from jlab_jaws_helper.JAWSConsumers import *

""" Map between JAWSConsumer and alarm topic
"""
TOPICS = {
   'alarm-registrations'   : { 'consumer_type' : AlarmRegistrationsConsumer,
      'description' : "Topic contains current set of registered alarms" },
   'effective-activations' : { 'consumer_type' :EffectiveActivationsConsumer,
      'description' : "Topic provides an alarm's effective state"},
   'alarm-activations'     : {'consumer_type' : AlarmActivationsConsumer,
      'description' : "Topic provides alarm's actual state"},
   'effective-alarms' : {'consumer_type' : EffectiveAlarmConsumer,
      'description' : ""},
   'alarm-overrides' : { 'consumer_type' : AlarmOverrideConsumer,
      'description' : "Topic containing override information"},
   'alarm-classes' : {'consumer_type' : AlarmClassConsumer,'description': ""},
   'effective-registrations' : {'consumer_type' : EffectiveRegistrationsConsumer,
      'description' : ""}
}

   
def init_messages(msglist) :
   """
      The subroutine passed to the consumer upon creation.
      It processes events already in the topics queue with
      the consumer subscribes. 
      
      ARGS:         msglist : 'cimpl.Message' list
   """   
   for msg in msglist.values() :
      show_alarms(msg)

def update_messages(msg) :
   """
      The subroutine passed to the consumer upon creation.
      It processes new incoming messages for the topic
      ARGS:
         msg : 'cimpl.Message'
   """   
   show_alarms(msg)  


def show_alarms(msg) :
   """
      Process the message, and create and
      the JAWS Alarm, and display resulting configuration. 
      ARGS:
         msg : 'cimpl.Message'
   """
   alarm = jaws_processor.process_alarm(msg)
     
  # if (alarm != None) :
   #   alarm.print_alarm()


def create_consumer(topic,monitor) :
   """
      Create a consumer for the topic
      ARGS:
         topic : topic 
         monitor : True/False
      NOTE:
         When a consumer is created, pass it the initializ
   """
   requestor = 'simple_example.py' #Identify the requestor
   
   consumer = TOPICS[topic]['consumer_type'](requestor,init_messages,update_messages,monitor) 
   return(consumer)



parser = argparse.ArgumentParser()
parser.add_argument('-topic',help="Topic(s) to access.",nargs='+')
parser.add_argument('-monitor',help="Monitor topic. Not implemented for multiple topics",
   action="store_true")
parser.add_argument('-list_topics',help="List valid topics",action="store_true")
args = parser.parse_args()

if (args.monitor and len(args.topic) > 1) :
   print("\n Sorry. This script can only monitor one topic at a time\n")
   quit()
   
def check_topics(topiclist) :
   """ check that *all* topics in the list are valid
   """
   valid = True
   for topic in topiclist :
      if (not topic in TOPICS) :
         valid = False
   return(valid)

def list_topics() :
   """ List the valid topics
   """
   print("\nVALID TOPICS:")
   print("---")
   for topic in TOPICS :
      print("  ",topic," : ",TOPICS[topic]['description'])
   print("\n")

if (args.list_topics) :
   """ User requested list of valid topics
   """
   list_topics()
   quit()

#Check that the topics passed in are valid
topics_valid = check_topics(args.topic)
if (not topics_valid) :
   list_topics()
   quit()

topic_list = args.topic

#Create the processor.
jaws_processor = JAWSProcessor(topic_list)   #Process incoming messages

#And a consumer for each requested topic
for topic in topic_list :
   consumer = create_consumer(topic,args.monitor)
   consumer.start()
   


   