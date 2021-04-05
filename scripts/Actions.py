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


class PrefAction(Action) :
   def __init__(self,parent,*args,**kwargs) :
      self.icon = QtGui.QIcon("gear.png")
      self.text = "Preferences"
      self.tip = "Preferences"
      
      super(PrefAction,self).__init__(parent,*args,**kwargs)
   
   def PerformAction(self) :
      #Has a shelfdialog already been created?
      dialog = GetManager().prefDialog
      
      #If not, create one.
      if (dialog == None) :
         dialog = GetManager().PrefDialog()      
      else :
         dialog.Reset()
      #pop
      RaiseDialog(dialog)      
      #dialog.Reset()
      GetManager().prefDialog = dialog

      
#ShelfAction 
#Display the shelving configuration dialog.
class ShelfAction(Action) :
   def __init__(self,parent,text="Shelve Selected",*args,**kwargs) :
      #Define the action's configuration       
      self.icon = QtGui.QIcon("address-book--plus.png")
      self.text = "Shelve Alarms"
      self.tip = "Shelve Alarms"
      
      super(ShelfAction,self).__init__(parent,*args,**kwargs)
   
   #Create/show the ShelfDialog
   def PerformAction(self) :
      
      #Has a shelfdialog already been created?
      dialog = GetManager().shelfDialog
      
      #If not, create one.
      if (dialog == None) :
         dialog = GetManager().ShelfDialog()      
      #pop
      RaiseDialog(dialog)      
      dialog.Reset()     
      GetManager().shelfDialog = dialog
   
   #Configure the tool bar
   def ConfigToolBarAction(self) :
      return
      alarmlist = GetSelectedAlarms()      
     
      if (len(alarmlist) == 0) :
         self.setEnabled(False)
      else :
         self.setEnabled(True)
 
#Filter action         
class FilterAction(Action) :
   def __init__(self,parent,*args,**kwargs) :
      
      self.icon = QtGui.QIcon("funnel--plus.png")
      self.text = "Filter"
      self.tip = "Filter alarms"
      super(FilterAction,self).__init__(parent,*args,**kwargs)
   
   #Create/display the filter dialog
   def PerformAction(self) :
      dialog = GetManager().filterDialog      
      if (dialog == None) :
         dialog = GetManager().FilterDialog()
      
      RaiseDialog(dialog)      
      GetManager().filterDialog = dialog
   
        
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

#Acknowledge Action      
class AckAction(Action) :
   def __init__(self,parent,text="Acknowledge Alarms",*args,**kwargs) :
      
      self.icon = QtGui.QIcon("tick-circle-frame.png")
      self.text = text
      self.tip = "Acknowledge"
      
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

#Get the list of alarms that have been selected on the table
def GetSelectedAlarms() :
   alarmlist = []
   proxymodel = GetTable().model()      
   sourcemodel = proxymodel.sourceModel()
         
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
   GetManager().toolbar.ConfigToolBar()
      



