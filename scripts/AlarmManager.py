#! /Library/Frameworks/Python.framework/Versions/3.8/bin/python3
import tkinter as tk
from tkinter import *
from tkinter import ttk

from utils import *
from AlarmPane import *
from AlarmMonitor import *

#This is the main GUI for the Kafka Alarm System (JAWS)
class GUI(tk.Frame) :
   
   def __init__(self,master=None) :
      
      #For general access
      SetRoot(master)
      
      #Simple frame holding active alarms. 
      Frame.__init__(self,master,bg='white')
      
      master.title("JAWS - Alarm Manager")
      if (GetTest()) :
         master.title("JAWS - Alarm Manager - Debug")
      
      bg = 'white'
      mainframe = Frame(master,bg=bg)
      mainframe.pack(side='top',fill='both',anchor='nw',pady=5,expand=True)
     
      title = Label(mainframe,text="JAWS - Alarm Manager",font=BIGBOLD,bg=bg)
      title.pack(side='top',fill='x',anchor='nw',padx=10)
      line = Frame(mainframe,height=2,bg='red',relief='solid',width=250)
      line.pack(side='top',anchor='n',pady=2)
      
      Frame(mainframe,height=10).pack(side='top')
      
      height = 200
      panedframe = Frame(mainframe,height=height)
      panedframe.pack(side='top',anchor='nw',fill='both',expand=True)
      
    #  activeframe = Frame(panedframe,bg='blue')
     # activeframe.pack(side='left')
      activepane =  ActivePane(panedframe)     
      #activepane = ShelvedPane(panedframe)
      
      print("ACTIVEPANE",activepane)
    #  activepane.pack(side='left',anchor='nw',fill='both',expand=True)
      self.activepane = activepane
      
     # return
      #shelvedpane = AlarmPane(panedframe,"shelved")      
      
   #   shelvedpane.pack(side='left',anchor='nw',fill='both',expand=True)
      #self.shelvedpane = shelvedpane
      #print(self.shelvedpane.winfo_parent())
      SetMain(self)
      monitor = AlarmMonitor(master) 

   def GetActivePane(self) :
      return(self.activepane)
   def GetShelvedPane(self) :
      return(self.shelvedpane.pane)

      
root = tk.Tk()
     
gui = GUI(root)
gui.mainloop()

