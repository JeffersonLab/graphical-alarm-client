####! /Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import tkinter as tk
from tkinter import *
from tkinter import ttk


#Work around...
def fixed_map(option,style):
   
   # Fix for setting text colour for Tkinter 8.6.9
   # From: https://core.tcl.tk/tk/info/509cafafae
   #
   # Returns the style map for 'option' with any styles starting with
   # ('!disabled', '!selected', ...) filtered out.

   # style.map() returns an empty list for missing options, so this
   # should be future-safe.
   return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]

class GUI2(tk.Frame) :
  
   def __init__(self,master=None) :
      self.mixlistmenu = None
      
      Frame.__init__(self,master)
      
      bar = PanedWindow(master,showhandle=True)
      bar.pack(side='top',fill='both',expand=True,anchor='nw',padx=10)
      font = '-*-helvetica-bold-r-bold-*-14-*-*-*-*-*-*-*'
      label = Label(master,text="Results",font=font)
      label.pack(side='top',fill='x',anchor='nw')
      
      listfont = "-*-helvetica-normal-r-normal-*-14-*-*-*-*-*-*-*"
       
      resultframe = ttk.Treeview(master)   
      resultframe['columns'] = ("name") 
      resultframe.column("name",width=15)
     # resultframe.bind("<<TreeviewSelect>>",self.ShowSummary)
      resultframe.pack(side='top',expand=True,fill='both',anchor='nw')
      bar.add(resultframe)
      image = tk.PhotoImage(file="./red-ball.png")
      
      for i in range(20) :
         resultframe.insert('','end',text="RECIPE" + str(i), image=image)
      
      
class GUI(tk.Frame) :

   
   def __init__(self,master=None) :
      
      style = ttk.Style()
     
      style.map('Treeview', foreground=fixed_map('foreground',style),
         background=fixed_map('background',style))
      style.configure('Treeview',rowheight=25)
      
     # master = tk.Toplevel()
      Frame.__init__(self,master)
      bar = PanedWindow(master,showhandle=True)
   #   bar.pack(side='top',fill='both',expand=True,anchor='nw',padx=10)
      label = Label(master,text="Alarms")
      label.pack(side='top',fill='x',anchor='nw')
      
      alarmframe = ttk.Treeview(master,selectmode="extended")
      
      alarmframe['columns'] = ("alarmname","timestamp")
      alarmframe.pack(side='top',anchor='nw',fill='both',expand=True)
      
      alarmframe.heading("#1",text="AlarmName")
      alarmframe.heading("#2",text="TimeStamp")
      alarmframe.column("#0",width=50,stretch=False,anchor='w')
      alarmframe.column("#1",anchor='center')
      alarmframe.column("#2",anchor='center')
      #bar.add(alarmframe)
      
      image = tk.PhotoImage(file="./red-ball.png")
      for i in range(20) :
         print(image)
         item= alarmframe.insert('','end',image=image,
            text=i,values=("NAME","TIME"))
  
root = tk.Tk()
print(root.tk.call('info', 'patchlevel'))
gui = GUI(root)
gui.mainloop()