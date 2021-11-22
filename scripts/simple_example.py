""" 
This simple example connects to the user's topic of choice.
"""
import os
import sys
import argparse


from jlab_jaws_helper.JAWSAlarm import *
from jlab_jaws_helper.JAWSProcessor import JAWSProcessor
from jlab_jaws_helper.JAWSConnection import *


def init_messages(msglist) :
   """
      Called to initialize messages already
      in the topic. 
      ARGS:
         msglist : 'cimpl.Message' list
   """
   for msg in msglist.values() :
      update_alarms(msg)

def update_messages(msg) :
   """
      Called to process incoming messages
      ARGS:
         msg : 'cimpl.Message'
   """
   
   update_alarms(msg)  


def update_alarms(msg) :
   """
      Process the message, and create
      the JAWS Alarm.
      ARGS:
         msg : 'cimpl.Message'
   """

   alarm = jaws_processor.process_alarm(msg)
   alarm.print_alarm()


def create_consumer(topic,monitor) :
   """
      Create a consumer for the topic
      ARGS:
         topic : topic 
         monitor : True/False
      NOTE:
         When a consumer is created, pass it the initializ
   """
   requestor = 'simple_example.py' #Identify the request
   consumer = None
   
   #Create the appropriate consumer based on the topic
   if (topic == "registered-alarms") :      
      consumer = RegisteredAlarmsConsumer(requestor,
         init_messages,update_messages,monitor)
   elif (topic == "active-alarms") :
      consumer = ActiveAlarmsConsumer(requestor,
         init_messages,update_messages,monitor)
   elif (topic == "alarm-state") :
      consumer = AlarmStateConsumer(requestor,
         init_messages,update_messages,monitor)
   return(consumer)

parser = argparse.ArgumentParser()
parser.add_argument('-topic',help="Topic to access")
parser.add_argument('-monitor',help="Monitor topic",action="store_true")
args = parser.parse_args()

topiclist = [args.topic]
jaws_processor = JAWSProcessor(topiclist)   #Process incoming messages
consumer = create_consumer(args.topic,args.monitor)
consumer.start()
