""" 
.. module:: Actions
   :synopsis : Create QActions 
.. moduleauthor::Michele Joyce <erb@jlab.org>
"""

from utils import *
from jlab_jaws_helper.JAWSConnection import *

#Define the Actions class
#Actions can be shared by the tool bars and context menus
class Action(QtWidgets.QAction) :
   """ Define the Actions Class. Actions can be shared by the toolbars and 
       contextmenus
   """
   def __init__(self,parent,*args,**kwargs) :
      super(Action,self).__init__(parent,*args,**kwargs)
      """ Create an action
       
         :param parent: parent widget
         :type parent: QMenu or QToolbar
      
      """    
      #Inherited action passes in configuration information
      self.parent = parent      

      self.setIcon(self.icon)              
      self.setIconText(self.text)      
      self.setToolTip(self.tip)
      
      self.triggered.connect(self.performAction)
      
   #Configure the toolbar actions. 
   #This subroutine can be overwritten by inherited actions.
   def configToolBarAction(self) :
      pass
   
   def getSelectedAlarms(self) :
      """ 
         Get the list of alarms that have been selected on the table
         :returns list of JAWSAlarms
      """      
      return(getTable().getSelectedAlarms())
   
   def getSelectedAlarm(self) :
      """ 
         Get the single selected alarm 
         :returns JAWSAlarm
      """      
      return(getTable().getSelectedAlarm())
      
      
   def addAction(self) :
      """ 
         Add an action. 
         Action may be added to a contextmenu, or toolbarCreate an action
      
      """    

      #If this isn't a menu, add it to the parent and return
      if (not isinstance(self.parent,QtWidgets.QMenu)) :
         self.parent.addAction(self)
         return(self)
      
      #If it is a context menu invoked when alarm(s) are selected
      #need to determine if 1. The action is valid 2. The text of the action
      valid = True
      valid = self.actionValid()
      
      #Only add to the menu if valid
      if (valid) :
         text = self.getText()
         self.parent.addAction(self)
         self.setText(text)
      return(self)
      
   def actionValid(self) :
      """ 
         Default validity check. Valid if at least one alarm is selected.
         NOTE: Can be overridden by children
         
         returns: valid/invalid 
      """
      valid = True
      if (len(self.getSelectedAlarms()) == 0) :
         valid = False
      return(valid)
   
   #Default text depends on the action's "actionword" and
   #the number of alarms selected.
   #Can be overridden by children
   def getText(self) :
      """ 
         Default validity check. Valid if at least one alarm is selected.
         NOTE: Can be overridden by children
      
         returns: menu/button text
      """
      
      actionword = self.actionword
      text = actionword + " Selected"
      alarmlist = self.getSelectedAlarms()
      if (len(self.getSelectedAlarms()) == 1) :
         text = actionword + ": " + self.getSelectedAlarm().get_name()      
      return(text)
  
#Display user preferences. 
#This action is added to the toolbar, as well as the "file" menu
class PrefAction(Action) :
   """ Display user preferences
       NOTE: This action is added to the toolbar as well as the file menu
   """
   
   def __init__(self,parent,*args,**kwargs) :
      """
         Create an instance
         :param parent: parent widget
         :type parent: QMenu or QToolbar
      """
        
      self.icon = QtGui.QIcon("gear.png")
      self.text = "Preferences"
      self.tip = "Preferences"
      
      super(PrefAction,self).__init__(parent,*args,**kwargs)
   
   #Invoke the preferences dialog.
   def performAction(self) :
      """ Display the user preferences dialog """
           
      dialog = getManager().createPrefDialog()
      raiseAndResetDialog(dialog)
      
      
#OverrideAction 
#Display the override configuration dialog.
class OverrideAction(Action) :
   def __init__(self,parent,text="Override Selected",*args,**kwargs) :
      #Define the action's configuration       
      self.icon = QtGui.QIcon("ssh")
      self.text = "Override Alarms"
      self.tip = "Override Alarms"
      
      self.actionword = "Override"
      super(OverrideAction,self).__init__(parent,*args,**kwargs)
   
   def configToolBarAction(self) :
      """  The action is only available,if at least one alarm is 
           being displayed
      """        
      if (self.actionValid()) :
         self.setEnabled(True)
      else :
         self.setEnabled(False)
   
   def actionValid(self) :
      """ 
         Valid if at least one alarm is displayed
         returns: valid/invalid 
      """
      valid = True ### TESTING
      #if (getModel().rowCount(0) == 0) :
      #   valid = False
      return(valid)
   
   #Create/show the OverrideDialog
   def performAction(self) :
      
      #Has a overridedialog already been created?
      dialog = getManager().createOverrideDialog()
       
      #pop
      raiseAndResetDialog(dialog)      
      
class RemoveFilterAction(Action) :
   """
      For visual hint of filtered data, this toolbar button is checked 
      automatically if a filter on any column has been applied
      If the user DESELECTS the button, all column filters will be removed.  
      The button is disabled if there are no filters applied to the table
   """
   def __init__(self,parent=None,*args,**kwargs) :
      
      self.icon = QtGui.QIcon("funnel--minus.png")
      self.text = "Remove Filters"
      self.tip = "Remove all Filters"
      self.parent = parent
      self.filters = getManager().getFilters()
      
      super(RemoveFilterAction,self).__init__(parent,*args,**kwargs)
      self.setCheckable(True)
   
 
   def setState(self) :
      """
         State of buttons depends on all filters.
         If a filter has been removed, need to check all other filters 
         to determine state
      """
      
      #Assume that there are no filters on the table
      filtered = self.getFilterState()
     
      self.setEnabled(filtered)
      self.setChecked(filtered)
      
      #The Preference Dialog (if has been created) should also be 
      #configured.
      prefdialog = getManager().getPrefDialog()
      if (prefdialog != None) :        
         prefdialog.configureDialog()
         
   def getFilterState(self) :
      """
         Are any filters applied?
         :returns boolean
      """      
      filtered = False          
      for filter in self.filters :
         #if one filter is applied, the manager is filtered
         if (filter.isFiltered()) :
            filtered = True
            break       
      return(filtered)
   
   def removeAllFilters(self) :
      """ Remove all of the filters """
      for filter in self.filters :
         filter.selectAll(True)
      self.setState()
               
   def performAction(self) :     
      """ Called when the Filter tool bar button is pushed """
      removefilters = not self.isChecked()
      if (removefilters) :
         self.removeAllFilters()
 
class PropertyAction(Action) :
   
   """ Display the properties of an alarm """
   
   def __init__(self,parent,text="Properties",*args,**kwargs) :
      """ 
         Create an instance
         :param parent: parent widget
         :type parent: QMenu or QToolbar
         :param text: Text to be displayed on the parent
         :type text: string (default = "Properties")
     
      """
      #Define the action's configuration          
      self.icon = QtGui.QIcon("application-list.png")
      self.text = "Properties"
      self.tip = "Alarm Properties"
      
      #Now call the parent.
      super(PropertyAction,self).__init__(parent,*args,**kwargs)
   
  
   def configToolBarAction(self) :
      """  The action is only available, if ONE alarm is selected. """        
      alarmlist = self.getSelectedAlarms()
      if (len(alarmlist) == 1) :
         self.setEnabled(True)
      else :
         self.setEnabled(False)
   
   def performAction(self) :
      """ Show the alarm's property dialog """
      alarm = self.getSelectedAlarms()[0]
      dialog = getManager().createPropertyDialog(alarm)
      #pop
      raiseAndResetDialog(dialog)      

  
   def actionValid(self) :
      """ Action only valid if one, and only one alarm has been selected. """      
      valid = True
      num = len(self.getSelectedAlarms())
      if (num != 1) :
         valid = False
      return(valid)
   
   def getText(self) :
      """ Text for menu item  """
      text = "Properties: " + self.getSelectedAlarm().get_name()
      return(text)

class OneShotAction(Action) :
   def __init__(self,parent,text="One Shot Shelved",*args,**kwargs) :
      self.icon = QtGui.QIcon("hourglass--arrow.png")
      self.text = text
      self.tip = "OneShot"
      self.actionword = "OneShot Shelve"
      super(OneShotAction,self).__init__(parent,*args,**args)
      
   
   def performAction(self) :            
      """ One Shot """
      producer = JAWSProducer('active-alarms',getManager().type)
      
      alarmlist = self.getAlarmsToBeAcknowledged()
      print("ALARMS:",alarmlist)
      for alarm in alarmlist :
         #self.acknowledgeAlarm(alarm.get_name(),producer)
         producer.ack_message(alarm.get_name())


#Acknowledge Action      
class AckAction(Action) :
   """ Acknowledge alarms """
   
   def __init__(self,parent,text="Acknowledge Alarms",*args,**kwargs) :
      """ 
         Create an instance
         :param parent: parent widget
         :type parent: QMenu or QToolbar
         :param text: Text to be displayed on the parent
         :type text: string (default = "Acknowledge Alarms")
     
      """
   
      self.icon = QtGui.QIcon("tick-circle-frame.png")
      self.text = text
      self.tip = "Acknowledge"
      
      self.actionword = "Ack"
      super(AckAction,self).__init__(parent,*args,**kwargs)
     
   
   def getAlarmsToBeAcknowledged(self) :
      """ Determine which selected alarms need to be acknowledged """
      alarmlist = self.getSelectedAlarms()
      
      #Only those with a latch severity make the cut
      needsack = []
      for alarm in alarmlist :
         if ("latched" in alarm.get_state(name=True).lower())  :
            needsack.append(alarm)
      return(needsack) 
   
   
   def actionValid(self) :
      """ Action is only valid if there is at least one alarm that
          needs to be acknowledged
      """
      valid = False
      needsack = self.getAlarmsToBeAcknowledged()
      
      if (len(needsack) > 0) :
         valid = True
      return(valid)
   
   def configToolBarAction(self) :
      """ Configure the toolbar button as appropriate """
      alarmlist = self.getAlarmsToBeAcknowledged()
      
      if (len(alarmlist) == 0) :
         self.setEnabled(False)
      else :
         self.setEnabled(True)
   
   def performAction(self) :            
      """ Acknowledge the list of alarms """
      producer = JAWSProducer('active-alarms',getManager().type)
      
      alarmlist = self.getAlarmsToBeAcknowledged()
    
      for alarm in alarmlist :
         #self.acknowledgeAlarm(alarm.get_name(),producer)
         producer.ack_message(alarm.get_name())
   
   def acknowledgeAlarm(self,alarmname,producer=None) :
      if (producer == None) :
         producer = JAWSProducer('active-alarms',getManager().type)
         
         ##### FOR TESTING PURPOSES ONLY Until active-alarms, alarm-state 
      
      producer.ack_message(alarmname)
      
   
#UnShelve selected alarm/alarms      
class UnShelveAction(Action) :
   def __init__(self,parent,*args,**kwargs) :
                  
      self.icon = QtGui.QIcon("address-book--minus.png")
      self.text = "Shelf Manager"
      self.tip = "Shelf Manager"
      
      self.actionword = "Unshelve"
      
      super(UnShelveAction,self).__init__(parent,*args,**kwargs)

   #Configure the toolbar as appropriate
   def configToolBarAction(self) :
      alarmlist = self.getSelectedAlarms()
      
      if (len(alarmlist) == 0) :
         self.setEnabled(False)
      else :
         self.setEnabled(True)
   
 
   #Unshelve the selected alarms      
   def performAction(self) :
      alarmlist = self.getSelectedAlarms() 
      
      message = None
      if (len(alarmlist) == 0) :
         message = "Select an alarm remove from shelf"
            
         msgBox = QtWidgets.QMessageBox()
         msgBox.setIcon(QtWidgets.QMessageBox.Warning)
         msgBox.setText(message)
         msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
         reply = msgBox.exec()
         return
      
      confirm = confirmAlarms(alarmlist,"Unshelve")
      if (not confirm) :
         return
      
      for alarm in alarmlist :
         alarm.UnShelveRequest()


