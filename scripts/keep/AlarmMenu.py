from utils import *
import os

#Context menu displayed when user right-clicks on a selection
class AlarmMenu(tk.Frame) :
   def __init__(self,selection,parent=None) :
      
      Frame.__init__(self,parent)     
      self.menu = Menu(parent,tearoff=0)
      
      #User can select multiple alarms.
      #The selection will be the NAMES of the alarms, not alarm 
      #objects. We want the objects.
      self.alarmlist = self.MakeAlarmList(selection)     
      self.CreateMenu()
   
   #Take the list of selected alarm names, and create 
   #a list of their alarm objects
   def MakeAlarmList(self,selection) :      
      alarmlist = []
      for item in selection :
         alarm = FindAlarm(item)
         if (alarm != None) :
            alarmlist.append(alarm)
      return(alarmlist)
    
   #If at least one of the alarms needs acknowledgement, we will
   #give the option.
   def CreateMenu(self) :
      #At least one to acknowledge?
      ackneeded = self.AckNeeded()
      
      #assuming multiple alarms need acknowledging
      ackstate = 'normal'
      acktext = "Acknowledge Selected"
      
      #If nothing needs acknowledgement, disable the selection,
      #but give the user a hint about what they're missing
      if (len(ackneeded) == 0) :
         ackstate = 'disabled'
         acktext = "Acknowledge"
      #Only one alarm needs acknowledging, specify the name on the
      #menu selection
      elif (len(ackneeded) == 1) :
         acktext = "Acknowledge " + ackneeded[0].GetName()
      
      #menu item has been configured as applicable
      self.menu.add_command(label=acktext,state=ackstate,
         command=self.AcknowledgeAlarms)
      
      self.ackneeded = ackneeded
   
   #Do any of the selected alarms need acknowledging?
   def AckNeeded(self) :
      ackneeded = []
      for alarm in self.alarmlist :
         ack = alarm.GetAcknowledged()
         if (not ack) :
            ackneeded.append(alarm)         
      return(ackneeded)
   
   #Acknowledge the alarm through the alarm object
   def AcknowledgeAlarms(self) :
      ackneeded = self.AckNeeded()
      for alarm in ackneeded :
         alarm.AcknowledgeAlarm()
   
   #Display the context menu      
   def PopUp(self,x,y) :
      try:
         self.menu.tk_popup(x,y)
      finally:
         self.menu.grab_release()   


