import tkinter as tk 
from  tkinter import * 


from utils import *

#Alarm Properties widget
class AlarmProperties(tk.Frame) :
   def __init__(self,alarm,parent=None) :
      
      self.alarm = alarm
      self.timestamp = alarm.timestamp
      self.ackbutton = None
      
      latching = "False"
      if (alarm.GetLatching()) :
         latching = "True"
 
      parent = Toplevel()
      
      self.propwidget = parent
      Frame.__init__(self,parent)
            
      outerframe = Frame(parent,bd=5)
      outerframe.pack(side='top',anchor='nw',fill='both',expand=True)
      self.outerframe = outerframe
      
      color = GetPriorityColor(alarm.GetPriority())
      if (color != None) :
         outerframe['background'] = color
      
      
      innerframe = Frame(outerframe,bg='white')
      innerframe.pack(side='top',fill='both',expand=True)
      
      nameframe = Frame(innerframe,bg='white')
      nameframe.pack(side='top',anchor='nw',fill='x')
      
      Label(nameframe,text="Device:",width=15,anchor='w',
         bg='white').pack(side='left',anchor='nw')
      Label(nameframe,text=alarm.GetName(),width=25,
         bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
      
      lastframe = Frame(innerframe,bg='white')
      lastframe.pack(side='top',anchor='nw',fill='x')      
      Label(lastframe,text="Last Alarm:",bg='white',
         width=15,anchor='w').pack(side='left',anchor='nw')
      Label(lastframe,textvariable=alarm.timestamp,
         bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
      
      if (latching == "True") :
         ackframe = Frame(innerframe,bg='white')
         ackframe.pack(side='top',anchor='nw',fill='x')      
         Label(ackframe,text="Acknowledged:",bg='white',
            width=15,anchor='w').pack(side='left',anchor='nw')
         Label(ackframe,textvariable=alarm.acktime,
            bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
      
      Frame(innerframe,height=15,bg='white').pack(side='top',
         fill='x',anchor='n')
      
      
      triggerframe = Frame(innerframe,bg='white')
      triggerframe.pack(side='top',anchor='nw',fill='x')      
      Label(triggerframe,font=SMALL,text="Trigger:",bg='white',
         anchor='w',width=15).pack(side='left',anchor='nw')     
      Label(triggerframe,font=SMALL,text=alarm.GetTrigger(),
         bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
      
      latchframe = Frame(innerframe,bg='white')
      latchframe.pack(side='top',anchor='nw',fill='x')
      Label(latchframe,font=SMALL,text="Latching:",bg='white',
         anchor='w',width=15).pack(side='left',anchor='nw')
      Label(latchframe,font=SMALL,text=latching,
         bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
      
      locationframe = Frame(innerframe,bg='white')
      locationframe.pack(side='top',anchor='nw',fill='x')
      Label(locationframe,font=SMALL,text="Location:",bg='white',
         anchor='w',width=15).pack(side='left',anchor='nw')     
      Label(locationframe,font=SMALL,text=alarm.GetParam('location'),
         bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
         
      categoryframe = Frame(innerframe,bg='white')
      categoryframe.pack(side='top',anchor='nw',fill='x')
      Label(categoryframe,font=SMALL,text="Category:",bg='white',
         anchor='w',width=15).pack(side='left',anchor='nw')     
      Label(categoryframe,font=SMALL,text=alarm.GetParam('category'),
         bg='white').pack(side='left',anchor='nw',fill='x',expand=True)
      
      Frame(innerframe,height=15,bg='white').pack(side='top',
         fill='x',anchor='n')
      
      
      urlframe = Frame(innerframe,bg='white')
      urlframe.pack(side='top',anchor='nw',fill='x')
      Label(urlframe,font=SMALL,text="Info:",bg='white',
         anchor='w',width=15).pack(side='left',anchor='nw')     
      Label(urlframe,font=SMALL,text=alarm.GetParam('docurl'),
         bg='white',fg='blue').pack(side='left',anchor='nw',fill='x',expand=True)

      edmframe = Frame(innerframe,bg='white')
      edmframe.pack(side='top',anchor='nw',fill='x')
      Label(edmframe,font=SMALL,text="Screen:",bg='white',
         anchor='w',width=15).pack(side='left',anchor='nw')     
      Label(edmframe,font=SMALL,text=alarm.GetParam('edmpath'),
         bg='white',fg='blue').pack(side='left',anchor='nw',fill='x',expand=True)
      
      Frame(innerframe,height=15,bg='white').pack(side='top',fill='x',
         anchor='n')
      
      buttonframe = Frame(innerframe,bg='white')
      buttonframe.pack(side='top')
      
      
      if (latching == "True") :
         ackbutton = Button(buttonframe,text="Ack",relief='flat',
            command=self.AckAlarm)
         ackbutton.pack(side='left',anchor='center')
         self.ackbutton = ackbutton
      
      Button(buttonframe,text="Close",relief='flat',bg='white',
         command=self.Close).pack(side='left',anchor='center')
      Button(buttonframe,text="Shelve/Disable",
         relief='flat',bg='white').pack(side='left',anchor='center')
      
      
      self.ConfigProperties(alarm.GetPriority())
   
   def AckAlarm(self) :
      alarm = self.alarm 
      alarm.AcknowledgeAlarm()
  
   def Close(self) :
      self.propwidget.destroy()
         
   
   def ConfigProperties(self,priority) :
      alarm = self.alarm
      
      color = GetPriorityColor(priority)
      if (color != None) :
         self.outerframe['background'] = color
       
      
      if (self.ackbutton != None) :
         state = 'normal'
         bg = color
         if (alarm.GetAcknowledged()) :
            state = 'disabled'
            bg = 'white'
         self.ackbutton['background'] = bg
         self.ackbutton['state'] = state
         
         
         
 