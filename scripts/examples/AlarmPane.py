import tkinter as tk
from tkinter import *
from tkinter import ttk

from utils import *
from AlarmMenu import *

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

   

   
      
      
   
#The main alarm display
class AlarmPane(tk.Frame) :
   
   def __init__(self,master=None,which=None) :
      
      #Various ways to sort the data. Most assigned "reverse=True"
      #so first switch is reverse=False
      self.sorttypes = {
         "status"  : {'function' : self.SortStatus, 'reverse' : False},
         "name"    : {'function' : self.SortName,   'reverse' : True},
         "time"    : {'function' : self.SortTime,   'reverse' : True},
         "category" : {'function' : self.SortCat,   'reverse' : True},
         "area"    : {'function' : self.SortArea, 'reverse' : True}
      }
      
      self.allalarms = []
      self.statusmap = {}
      for status in ALARMSTATUS:         
         self.statusmap[status] = []       

      #This is part of the bug-fix for Treeview background in this
      #specific version of tkinter
      style = ttk.Style()     
      style.map('Treeview', foreground=fixed_map('foreground',style),
         background=fixed_map('background',style))
      style.configure('Treeview',rowheight=25)
                
      Frame.__init__(self,master)
      
      label = Label(master,text=which.capitalize() + " Alarms",font=SMALLBOLD)
      label.pack(side='top',fill='x',anchor='nw')
      
      #Create the AlarmPane. The alarmpane Treeview widget with
      #columns containing the information pertinent to the type of AlarmPane
      alarmpane = ttk.Treeview(master,selectmode='extended')
      alarmpane.pack(side='top',anchor='nw',fill='both',expand=True)
      self.alarmpane = alarmpane
      
      self.ColumnConfigure()
      self.TagConfigure()
      #User 3rd-mouse/right-mouse/or control-clicks the alarm,
      #the context menu is displayed.
      alarmpane.tag_bind("bindmenu","<Button-3>",self.ContextMenu)
      alarmpane.tag_bind("bindcontrol","<Control-Button-1>",self.ContextMenu)
      
      #Double clicking on the alarm brings up the alarm property widget
      alarmpane.tag_bind("props","<Double-Button-1>",self.ShowProperties)
      
      #Default set of tagbindings to be bound to the alarm items.
      self.tags = ['bindmenu','bindcontrol','props']
      
      
      #The list of items in the Treeview
      self.items = []
      
      #The popup context menu
      self.alarmmenu = None
      
      #The frame in which to put the alarm items.
      self.alarmpane = alarmpane
   
   #Common columns between active and shelved columns
   def ColumnConfigure(self) :
      alarmpane = self.alarmpane
      
      alarmpane['columns'] = ("area","category","alarmname","timestamp")
      alarmpane.column("#0",width=50,stretch=False,anchor='w')
      alarmpane.column("#1",width=100,anchor='center')
      alarmpane.column("#2",width=100,anchor='center')
      alarmpane.column("#3",width=200,anchor='center')
      alarmpane.column("#4",width=200,anchor='center')
      
      #Configure the headings to sort the data.
      #Subsequent click sorts in reverse.
      alarmpane.heading("#0", 
         command = lambda: self.SwitchSort("status"))      
      #This stretch=False doesn't seem to work. No answer from 
      #StackOverflow.      
      
      alarmpane.heading("#1",text="Area",
         command = lambda: self.SwitchSort("area"))
      alarmpane.heading("#2",text="Category",
         command = lambda: self.SwitchSort("category"))
      alarmpane.heading("#3",text="AlarmName",
         command = lambda: self.SwitchSort("name"))
      

   #The user has clicked on one of the column headings, and requested
   #to sort by that column (type)
   def SwitchSort(self,type) :
      #Declare that this is the new sort method (until changed)
      self.sortmethod = type
      
      #Gain access to the sortypes definition
      sorttype = self.sorttypes[type]
      
      #Toggle back and forth reverse=True, reverse=False 
      reverse = sorttype['reverse']      
      if (sorttype['reverse']) :
         sorttype['reverse'] = False
      else :
         sorttype['reverse'] = True
      
      #Call the sort type's function to do the sort.  
      sorttype['function']()
   
   #Sort by status  
   def SortStatus(self) :
      
      #Sort direction. !reverse = P1-P4 , reverse = P4-P1 
      reverse = self.sorttypes['status']['reverse']
      
      statuslist = ALARMSTATUS.keys()
      if (reverse) :
         statuslist = sorted(statuslist,reverse=reverse)
      
      #empty out the 'all' list. It will be filled while going through the
      #status lists.
      self.allalarms = []
      
      #Sort each list in the statuslist, and add it to the
      #'all' list for gridding.
      for status in statuslist :
         #Add alarm to the list for that status
         list = self.statusmap[status]
         
         #Sort the status list by the time stamp
         list = sorted(list,reverse=reverse,
            key=lambda alarm:alarm.GetTimeStamp())
         
         self.statusmap[status] = list
         self.allalarms.extend(list)
      
      #Add the alarms to the tree.
      self.AddToTree()
      

   #Sort by name
   def SortName(self) :
      #Sort direction: !reverse = A-Z, reverse = Z-A
      reverse = self.sorttypes['name']['reverse']
     
      #Use the 'all' list
      list = self.allalarms
      list = sorted(list,reverse=reverse,key=lambda alarm:alarm.GetName())   
      self.allalarms = list
      
      #Add the alarms to the tree
      self.AddToTree()
   
   #Sort by active time.
   def SortTime(self) :
     
      #Sort direction: !reverse = oldest-newest reverse=newest-oldest
      reverse = self.sorttypes['time']['reverse']
     
      list = self.allalarms
      list = sorted(list,reverse=reverse,key=lambda alarm:alarm.GetTimeStamp())
      self.allalarms = list
      self.AddToTree()
               
   def SortCat(self) :
      #Sort direction: !reverse = [A-Z], reverse = [Z-A]
      reverse = self.sorttypes['category']['reverse']
     
      list = self.allalarms
      list = sorted(list,reverse=reverse,key=lambda alarm:alarm.GetCategory())
      self.allalarms = list
      self.AddToTree()

   
   def SortArea(self) :
   
     #Sort direction: !reverse = [A-Z], reverse = [Z-A]
     reverse = self.sorttypes['area']['reverse']
     list = self.allalarms
     
     list = sorted(list,reverse=reverse,key=lambda alarm:alarm.GetLocation())
     self.allalarms = list
     self.AddToTree() 
   
      
   #Remove this alarm from all lists, it can only be in one at a time
   def RemoveFromLists(self,alarm) :
      if (alarm in self.allalarms) :
         self.allalarms.remove(alarm)
         
      for status in ALARMSTATUS.keys() :
         if (alarm in self.statusmap[status]) :
            self.statusmap[status].remove(alarm)
   
   #Remove the alarm from the pane
   def RemoveAlarm(self,alarm) :
      #Remove from the status lists
      self.RemoveFromLists(alarm)
      #And then the grid
      self.RemoveFromTree(alarm)

   #Remove the alarm's widgets from the pane.
   def RemoveFromTree(self,alarm) :
      name = alarm.GetName()
      if (name in self.items) :
         self.alarmpane.delete(name)
         self.items.remove(name)
      return
   
   #Display the alarm properties. binding on double-click on the treeitem.
   def ShowProperties(self,event=None) :
      if (event is None) :
         return
      #what alarm has been selected? 
      selection = self.alarmpane.selection()
      #Ignore if more than one selected.
      if (len(selection) > 1) :
         return
      #Get the alarm object associated with this selection
      alarm = FindAlarm(selection[0])
      #Show the alarm properties.
      alarm.ShowProperties()

   #Display context menu. bindings on control-click,3rd/right-mouse/ button         
   def ContextMenu(self,event=None) :
      if (event == None) :
         return
      #Create an alarm for the selections. Can be multiple
      selections = self.alarmpane.selection()
      if (self.alarmmenu != None) :
         self.alarmmenu.menu.destroy()
      self.alarmmenu = AlarmMenu(selections)
      
      #Pop up the alarm where the mouse is.
      self.alarmmenu.PopUp(event.x_root,event.y_root)

   #Add an alarm to the pane
   def AddAlarm(self,alarm) :
      
      #An alarm can only be in one status list at a time.
      #Remove them from all lists, and then add back before putting
      #on grid      
      
      self.RemoveFromLists(alarm)
      
      #What is the alarm status? 
      status = alarm.GetStatus()
      
      #Nothing to do here. 
      if (not status) :
         return
      
      #Made it to here because a latching alarm has cleared BEFORE
      #it was acknowledged. Use the laststatus for display
   #   elif (status == None) :
    #     status = laststatus
      
      #Add the alarm to the 'all' alarms list.
      allalarms = self.allalarms      
      if (not alarm in allalarms) :
         allalarms.append(alarm)
      
      #Add the alarm to the appropriate status list.
      list = self.statusmap[status]
      
      if (not alarm in list) :
         list.append(alarm)      
      
      #How is the data sorted? By default, by status.
      sorttype = self.sortmethod
      self.sorttypes[sorttype]['function']()  
      
      
   
   def AddToTree(self) :
      
      #Keep track of the rows. Don't just want to keep adding to the
      #end. We'll redraw all of them each time. 
      row = 0
      alarmlist = self.allalarms
      for alarm in alarmlist :
         name = alarm.GetName()
         
         area = alarm.GetLocation()
         category = alarm.GetCategory()
         #Display the time when the alarm became active.
         timestamp = alarm.GetTimeStamp()
         
         #What image (status indicator) will we use?
         image = self.GetDisplayIndicator(alarm)
         
         #What set of tags will be assigned. This set will include
         #the back ground color
         tags = self.GetDisplayTags(alarm)
         #Make sure that if the alarm is on the tree already, it is 
         #removed. It won't necessarily stay in the same spot.
         if (name in self.items) :
            self.alarmpane.delete(name)
            self.items.remove(name)
         values = (area,category,name,timestamp)     
         #Insert the alarm into the tree
         item= self.alarmpane.insert('',row,image=image,iid=alarm.GetName(),
            text='',values=values,tags=tags)           
         self.items.append(name)
         row = row + 1

class ActivePane(AlarmPane) :
   def __init__(self,master=None) :
      super(ActivePane,self).__init__(master,"Active") 
      
      #The default sortmethod
      self.sortmethod = "status"
      
   
   def ColumnConfigure(self) :
      AlarmPane.ColumnConfigure(self)
      self.alarmpane.heading("#4",text="TimeStamp",
         command = lambda: self.SwitchSort("time"))

   def TagConfigure(self) :
      alarmpane = self.alarmpane
      #Initialize the "statusmap" lists. 
      #By default, the alarms will be sorted by status (P1-P4) and within a 
      #status, sorted by time (most recent first)
      #Therefore, we keep a separate list for each status.
      
      for status in ALARMSTATUS:               
         #At the same time, create a tag that changes the background of
         #the alarm to the associated status color
         color = GetStatusColor(status)
         alarmpane.tag_configure(status,background = color)
             
   #Determine the complete set of display tags to use on the tree item
   def GetDisplayTags(self,alarm) :
      
      #The initial list consists of the bind_tags that all alarms
      #get.
      tags = self.tags[:]
      
      #The background of the alarm item is based on the 
      #current status, the last status, and its acknowledge state
      status = alarm.GetStatus()
      ack = alarm.GetAcknowledged()
      
      if (status and ack) :
         tag = "ACK"
      elif (status and not ack) :
         tag = status
      elif (not status and not ack) :
         tag = "ACK"
         
      #Add the tags to the list, and return
      tags.append(tag)
  #    print(alarm.GetName(),"STATUS:<",status,">ACK:<",ack,">",tags)
      return(tags)

      ###########DEALING WITH ACK ##########
      #Active alarm has been acknowledged (or not a latching alarm) 
      if (status != None and ack) :
         #This tag will make the background white
         tag = "ACK"
      
      #Active latched alarm that has not been acknowledged  
      elif (status != None and not ack) :
         #The background will be the color assigned to the status
         tag = status
      
      #Latched alarm is no longer active (status=None) but not acknowledged.
      elif (status == None and laststatus != None) :
         #The background will be the color assigned to the last status
         #before the alarm was cleared.
         tag = laststatus
      
   
   #Determine which image to use as the status indicator
   def GetDisplayIndicator(self,alarm) :
      
      #The image is based on the current status, or
      #if the alarm has cleared, but not been acknowledged.
      image = None
      
      status = alarm.GetStatus()
      ack = alarm.GetAcknowledged()
      #Alarm is active, use the image associated with its current
      #status
      if (status) :
         image = GetStatusImage(status)
      elif (not status and not ack) :
         image = GetStatusImage("ACK")
      #latched alarm is no longer active, but cannot be removed since it 
      #has not been acknowledged. Image will be white.
#      elif (status == None and laststatus != None) :        
 #        image = GetPriorityImage("ACK")
      return(image)
      
class ShelvedPane(AlarmPane) :
   def __init__(self,master=None) :
      return
      super(ShelvedPane,self).__init__(master,"Shelved") 
      
      #The default sortmethod
      self.sortmethod = "time"
      self.tags.append("shelved")
   
   def ColumnConfigure(self) :
      AlarmPane.ColumnConfigure(self)
      self.alarmpane.heading("#4",text="Time Remaining",
         command = lambda: self.SwitchSort("time"))

   def TagConfigure(self) :
      alarmpane = self.alarmpane
      fg = "black"
      bg = "lightgray"
      alarmpane.tag_configure('shelved',background=bg,foreground=fg)

   def GetDisplayTags(self,alarm=None) :
      return(self.tags)
   
   def GetDisplayIndicator(self,alarm) :
      image = None
      status = alarm.GetPriority()
      if (status != None) :
         image = GetShelvedImage(status) 
      elif (status == None) :
         image = GetShelvedImage("NO_ALARM")
      return(image)

