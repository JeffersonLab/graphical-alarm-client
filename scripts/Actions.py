from utils import *

#Define the Actions class
#Actions can be shared by the tool bars and context menus
class Action(QtWidgets.QAction) :
   def __init__(self,parent,*args,**kwargs) :
      super(Action,self).__init__(parent,*args,**kwargs)
      
      #Inherited action passes in configuration information
      self.parent = parent      

      self.setIcon(self.icon)              
      self.setIconText(self.text)      
      self.setToolTip(self.tip)
      
      self.triggered.connect(self.PerformAction)
      
   #Configure the toolbar actions. 
   #This subroutine can be overwritten by inherited actions.
   def ConfigToolBarAction(self) :
      pass
   
   #Add an action. Action may be added to a contextmenu, or toolbar
   def AddAction(self) :
      
      #If this isn't a menu, add it to the parent and return
      if (not isinstance(self.parent,QtWidgets.QMenu)) :
         self.parent.addAction(self)
         return(self)
      
      #If it is a context menu invoked when alarm(s) are selected
      #need to determine if 1. The action is valid 2. The text of the action
      valid = True
      valid = self.ActionValid()
      
      #Only add to the menu if valid
      if (valid) :
         text = self.GetText()
         self.parent.addAction(self)
         self.setText(text)
      return(self)
   
   #Default validity check. Valid if at least one alarm is selected.
   #Can be overridden by children
   def ActionValid(self) :
      valid = True
      if (len(GetSelectedAlarms()) == 0) :
         valid = False
      return(valid)
   
   #Default text depends on the action's "actionword" and
   #the number of alarms selected.
   #Can be overridden by children
   def GetText(self) :
      actionword = self.actionword
      text = actionword + " Selected"
      alarmlist = GetSelectedAlarms()
      if (len(GetSelectedAlarms()) == 1) :
         text = actionword + ": " + GetSelectedAlarm().GetName()      
      return(text)
  
#Display user preferences. 
#This action is added to the toolbar, as well as the "file" menu
class PrefAction(Action) :
   def __init__(self,parent,*args,**kwargs) :
      
      self.icon = QtGui.QIcon("gear.png")
      self.text = "Preferences"
      self.tip = "Preferences"
      
      super(PrefAction,self).__init__(parent,*args,**kwargs)
   
   #Invoke the preferences dialog.
   def PerformAction(self) :
      #Has a prefdialog already been created?
      dialog = GetManager().prefdialog
      
      #If not, create one.
      if (dialog == None) :
         dialog = GetManager().PrefDialog()      
      else :
         #otherwise reset it with the current configuration
         dialog.Reset()    
      #pop
      RaiseDialog(dialog)      
      GetManager().prefdialog = dialog

      
#ShelfAction 
#Display the shelving configuration dialog.
class ShelfAction(Action) :
   def __init__(self,parent,text="Shelve Selected",*args,**kwargs) :
      #Define the action's configuration       
      self.icon = QtGui.QIcon("address-book--plus.png")
      self.text = "Shelve Alarms"
      self.tip = "Shelve Alarms"
      
      self.actionword = "Shelve"
      super(ShelfAction,self).__init__(parent,*args,**kwargs)
         
   #Create/show the ShelfDialog
   def PerformAction(self) :
      
      #Has a shelfdialog already been created?
      dialog = GetManager().shelfdialog
      
      #If not, create one.
      if (dialog == None) :
         dialog = GetManager().ShelfDialog()      
      else :
         dialog.Reset()    
      #pop
      RaiseDialog(dialog)      
      GetManager().shelfdialog = dialog
   
 
#RemoveFilter action 
#For visual hint of filtered data, this toolbar button is checked 
#automatically if a filter on any column has been applied
#If the user DESELECTS the button, all column filters will be removed.  
#The button is disabled if there are no filters applied to the table
class RemoveFilterAction(Action) :
   def __init__(self,parent=None,*args,**kwargs) :
      
      self.icon = QtGui.QIcon("funnel--minus.png")
      self.text = "Remove Filters"
      self.tip = "Remove all Filters"
      self.parent = parent
      self.filters = GetManager().GetFilters()
      #self.prefdialog = None
      
      super(RemoveFilterAction,self).__init__(parent,*args,**kwargs)
      self.setCheckable(True)
   
   #State of buttons depends on all filters.
   #If a filter has been removed, need to check all other filters 
   #to determine state
   def SetState(self) :
      
      #Assume that there are no filters on the table
      filtered = self.GetFilterState()
     
      self.setEnabled(filtered)
      self.setChecked(filtered)
      
      #The Preference Dialog (if has been created) should also be 
      #configured.
      prefdialog = GetManager().GetPrefDialog()
      if (prefdialog != None) :        
         prefdialog.Configure()
         
   #Are any filters applied? 
   def GetFilterState(self) :
      filtered = False          
      for filter in self.filters :
         #if one filter is applied, the manager is filterd
         if (filter.IsFiltered()) :
            filtered = True
            break       
      return(filtered)
   
   #Remove all of the filters    
   def RemoveAllFilters(self) :
      for filter in self.filters :
         filter.SelectAll(True)
      self.SetState()
            
   #Called when the Filter tool bar button is pushed
   def PerformAction(self) :
      removefilters = not self.isChecked()
      if (removefilters) :
         self.RemoveAllFilters()

      
#PropertyAction 
#Display the properties for an alarm.  
class PropertyAction(Action) :
   def __init__(self,parent,text="Properties",*args,**kwargs) :
      
      #Define the action's configuration          
      self.icon = QtGui.QIcon("application-list.png")
      self.text = "Properties"
      self.tip = "Alarm Properties"
      
      #Now call the parent.
      super(PropertyAction,self).__init__(parent,*args,**kwargs)
   
   #The action is only available, if ONE alarm
   #is selected.   
   def ConfigToolBarAction(self) :
      alarmlist = GetSelectedAlarms()
      if (len(alarmlist) == 1) :
         self.setEnabled(True)
      else :
         self.setEnabled(False)
   
   #Show the alarm's property
   def PerformAction(self) :
      alarm = GetSelectedAlarms()[0]
      alarm.ShowProperties()
   
   #Action only valid if one, and only one alarm has been selected.
   def ActionValid(self) :
      valid = True
      num = len(GetSelectedAlarms())
      if (num != 1) :
         valid = False
      return(valid)
   
   #Text for menu item   
   def GetText(self) :
      text = "Properties: " + GetSelectedAlarm().GetName()
      return(text)

#Acknowledge Action      
class AckAction(Action) :
   def __init__(self,parent,text="Acknowledge Alarms",*args,**kwargs) :
      
      self.icon = QtGui.QIcon("tick-circle-frame.png")
      self.text = text
      self.tip = "Acknowledge"
      
      self.actionword = "Ack"
      super(AckAction,self).__init__(parent,*args,**kwargs)
     
   #Determine which selected alarms need to be acknowledged
   def GetAlarmsToBeAcknowledged(self) :
      alarmlist = GetSelectedAlarms()
      
      #Only those with a latch severity make the cut
      needsack = []
      for alarm in alarmlist :
         if (alarm.GetLatchSevr() != None and
            not "NO_ALARM" in alarm.GetLatchSevr()) :
            needsack.append(alarm)
      return(needsack) 
   
   #Action is only valid if there is at least one alarm that
   #needs to be acknowledged
   def ActionValid(self) :
      valid = False
      needsack = self.GetAlarmsToBeAcknowledged()
      if (len(needsack) > 0) :
         valid = True
      return(valid)
   
   #Configure the toolbar button as appropriate
   def ConfigToolBarAction(self) :
      alarmlist = self.GetAlarmsToBeAcknowledged()
      
      if (len(alarmlist) == 0) :
         self.setEnabled(False)
      else :
         self.setEnabled(True)
   
   #Acknowledge the list of alarms  
   def PerformAction(self) :      
      alarmlist = self.GetAlarmsToBeAcknowledged()
      for alarm in alarmlist :
         alarm.AcknowledgeAlarm()

#UnShelve selected alarm/alarms      
class UnShelveAction(Action) :
   def __init__(self,parent,*args,**kwargs) :
                  
      self.icon = QtGui.QIcon("address-book--minus.png")
      self.text = "Shelf Manager"
      self.tip = "Shelf Manager"
      
      self.actionword = "Unshelve"
      
      super(UnShelveAction,self).__init__(parent,*args,**kwargs)

   #Configure the toolbar as appropriate
   def ConfigToolBarAction(self) :
      alarmlist = GetSelectedAlarms()
      
      if (len(alarmlist) == 0) :
         self.setEnabled(False)
      else :
         self.setEnabled(True)
   
 
   #Unshelve the selected alarms      
   def PerformAction(self) :
      alarmlist = GetSelectedAlarms() 
      
      message = None
      if (len(alarmlist) == 0) :
         message = "Select an alarm remove from shelf"
            
         msgBox = QtWidgets.QMessageBox()
         msgBox.setIcon(QtWidgets.QMessageBox.Warning)
         msgBox.setText(message)
         msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
         reply = msgBox.exec()
         return
      
      confirm = ConfirmAlarms(alarmlist,"Unshelve")
      if (not confirm) :
         return
      
      for alarm in alarmlist :
         alarm.UnShelveRequest()

#Get the single alarm that is selected.
def GetSelectedAlarm() :
   alarmlist = GetSelectedAlarms()

   alarm = None
   if (len(alarmlist) > 0) :
      alarm = alarmlist[0]
   return(alarm)
        

#Get the list of alarms that have been selected on the table
def GetSelectedAlarms() :
   alarmlist = []
   
   #Access both the proxy model and the sourcemodel
   proxymodel = GetProxy() 
   sourcemodel = GetModel()     
   
   #The indices returned are that of the proxymodel, which is what 
   #the table LOOKS like. We need the source model index to identify the
   #actual selected alarm.
   indices = GetTable().selectedIndexes()
   
   for index in indices :
      proxy_index = index
      #convert the proxy_index into a source_index, 
      #and find the row that is associated with the selected alarm(s)
      source_row = proxymodel.mapToSource(proxy_index).row()
      alarm = sourcemodel.data[source_row]         
      alarmlist.append(alarm)
   return(alarmlist)

#If a row is selected, configure tool bar as appropriate.
def RowSelected() :
   GetManager().GetToolBar().Configure()
      



