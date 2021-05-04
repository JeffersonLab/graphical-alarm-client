#NOTE ABOUT METHOD AND VARIABLE NAMES
# --- self.myvariable     -- variable for this application
# --- def MyMethod()      -- method implemented for this application
# --- def libraryMethod() -- method accessed from a python library


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog

from ModelView import *

def GetFilterByName(name) :
   result = None
   filters = GetManager().GetFilters()
   for filter in filters :
      if (filter.GetName() == name) :
         return(filter)
   return(result)
   
   
#All filters inherit from this one.
#example: Category
class Filter(object) :
   def __init__(self,name) : 
   
      #All filters get an "Empty". In case the alarm 
      #has not been defined with the filtered property
      options = ["Empty"]
      
      #The specific filter options ['RF','Misc','BPM']
      filteroptions = self.GetOptions()
      
      #Add this to "Empty"
      options.extend(filteroptions)      
      self.options = options
      
      #The name of the filter ("Category"      
      self.filtername = name
      
      #Whether or not the option is filtered out or not
      self.settings  = {}
      
      #Filter's state
      self.filtered = False
      
      self.InitSettings()

   
   def SaveFilter(self) :
      
      settings = {}
      for option in self.options :
         val = self.GetOptionSetting(option)
         settings[option] = val
 
      return(settings)
   
   #Access to the filter name
   def GetName(self) :
      return(self.filtername)
   
   #Access the filter state
   def IsFiltered(self) :
      return(self.filtered)

   #Set the filter state  
   def SetFiltered(self) :
      #If one option is filtered out, the filter is "filtered"
      filtered = False
      if (not self.settings == None and len(self.settings) > 0) :
         for option in self.settings :
            val = self.GetOptionSetting(option)
            if (val == 0) :
               filtered = True
               break
      self.filtered = filtered
      
   #Get the filter's current settings
   def GetCurrentSettings(self) :     
      return(self.settings)
   
   def InitSettings(self) :
      settings = {}
      
      name = self.GetName()
      settings = {}
      for option in self.options :
         settings[option] = True
      self.settings = settings
      
   
   #Set the setting configuration   
   def SetSettings(self,settings) :
      
      self.settings = settings
      
      #Whenever the settings are set, determine the new
      #filter state
      self.SetFiltered()
      
   #Get the setting of a specific option in the filter
   def GetOptionSetting(self,option) :
      settings = self.GetCurrentSettings()
      
      checked = False
      if (option in settings) :
         val = settings[option]
         checked = val
      
      return(checked)
   
   #Determine whether or not we add the filter icon to
   #the column header.
   def SetHeader(self) :
      #Iterate through each setting.
      #If at least one setting's value is 0,
      #display the filter icon on the header      
      settings = self.GetCurrentSettings()      
      headerfilter = False
      if (not settings == None) :
         for prop in settings :
            if (settings[prop] == 0) :
               headerfilter = True
               break   
                       
      #Call the model with the results
      GetModel().SetHeader(self.GetName(),headerfilter)
      GetManager().GetRemoveFilterAction().SetState()
 
   def SetFilter(self,option,value) :      
      #Get the current setting configuration and set the option's
      #value as appropriate
      settings = self.GetCurrentSettings()
      settings[option] = value
      
      #Warn the the proxymodel that something is going to change
      #and the table needs to redraw...and thus refilter
      GetModel().layoutAboutToBeChanged.emit() 
      
      #Assign the new setting configuration
      self.SetSettings(settings) 
      
      #Let the proxy model know we're done.
      GetModel().layoutChanged.emit()  
   
   #Select all options...basically unfilter the column
   def SelectAll(self,selected) :
      for option in self.options :        
         self.SetFilter(option,selected)
      self.SetHeader()      
      
      
   
   #Apply the filter to the set of alarm data.
   #This is called by the model's "filterAcceptRow" method.
   #Compare the filter configuration to the alarm's value.
   def ApplyFilter(self,alarm) :
      #Assume we'll keep the alarm.
      keepalarm = True
      
      #Access the current configuration.
      settings = self.GetCurrentSettings()
      
      #Go through each filter option
      for option in self.options :
         #Just in case, check that the option is in the 
         #settings configuration.
         if (option in settings) :
            #The desired state of the user. 
            state = settings[option]
          
            #If the state of the setting is 0 or False,
            #Need to check the alarm value.
            if (state == 0 or not state) :
               #access the value of the alarm
               alarmval = self.GetFilterVal(alarm)
               
               #If user doesn't want "empty", and the alarmval is not set
               if (option.lower() == "empty" and alarmval == None) :
                  #Don't want the alarm
                  keepalarm = False
               elif (alarmval != None) :
                  #If the alarm has a value, compare it to the unwanted
                  #option, if it's the same, we will not keep the alarm
                  if (option.lower() == alarmval.lower()) :
                     keepalarm = False
         if (not keepalarm) :
            break
      #return the result.
      return(keepalarm)


#A CategoryFilter 
#Users can display/hide alarms according to category
class CategoryFilter(Filter) :
   
   def __init__(self) :
      super(CategoryFilter,self).__init__("category")
           
   #Each category type has its own set of options   
   def GetOptions(self) :
      
      return(list(GetConsumer().GetCategories()))
   
   #Access the alarm's category         
   def GetFilterVal(self,alarm) :
      return(alarm.GetCategory())

#A LocationFilter
#Users can display/hide alarms based on location
class LocationFilter(Filter) :
   def __init__(self) :
      super(LocationFilter,self).__init__("location")
      
   #Get the valid locations from Kafka           
   def GetOptions(self) :
      return(list(GetConsumer().GetLocations()))   
      
   #Access the alarm's location
   def GetFilterVal(self,alarm) :
      return(alarm.GetLocation())

#Choices for the status filter          
class StatusFilter(Filter) :  
   def __init__(self) :      
      super(StatusFilter,self).__init__('status')
      self.options.remove("Empty")
   
   def GetOptions(self) :
      return(['LATCHED','MAJOR','MINOR'] )
   
   #A little more processing on the return value.
   ### THIS MAY HAVE TO BE REVISITED ##      
   def GetFilterVal(self,alarm) :
      return(alarm.GetStatus())
     

#Type of alarm (epics,nagios,smart)
class TypeFilter(Filter) :
   def __init__(self) :      
      super(TypeFilter,self).__init__('type')
   
   def GetOptions(self) :
      return(['epics'])      
   
   def GetFilterVal(self, alarm) :
      return(alarm.GetType())

#Alarm priority      
class PriorityFilter(Filter) :
   def __init__(self) :
      self.options = ['P1','P2','P3']
      
      super(PriorityFilter,self).__init__('priority')
      
      
   def GetOptions(self) :
      return(['P1','P2','P3'])
        
   def GetFilterVal(self,alarm) :
      alarm.GetPriority()

#Popup context menu assigned to header columns
class FilterMenu(QtWidgets.QMenu) :
   def __init__(self,filter,parent=None) :
      super(FilterMenu,self).__init__("Filters",parent)
      
      self.parent = parent
      self.filter = filter
      
      #Keep a list of the option checkbox widgets to configure
      #as a whole
      self.checkboxlist = []
      
      #Each filter has a checkbox for "All"
      self.allcheckbox = None
      
      self.setTearOffEnabled(True) 
      title = filter.GetName().capitalize() + " Filters"   
      self.addSection(title)
            
      #Create the options for this filter
      self.MakeOptions()
      
   #Add the filter options to the menu.      
   def MakeOptions(self) :
      
      #First create an option for "All"
      widget = self.OptionWidget("All")
      action = QtWidgets.QWidgetAction(self)
      action.setDefaultWidget(widget)
      self.addAction(action)
                  
      self.addSeparator()
      
      #Create an "option widget" for each option in the 
      #filter. Have to create widget to work around unwanted contextmenu 
      #behavior -- automatically closing when a checkbox is selected/deselected
      #We want the user to be able to select/deselect more than one...
      filter = self.filter
      for status in filter.options :
         widget = self.OptionWidget(status)
         action = QtWidgets.QWidgetAction(self)
         action.setDefaultWidget(widget)
         self.addAction(action)
      
      #Determine the state of the "All" option
      self.ConfigAllOption()
      
      return
   
   #Create an "option widget" 
   #Have to create widget to work around unwanted contextmenu 
   #behavior -- automatically closing when a checkbox is selected/deselected
   #We want the user to be able to select/deselect more than one...
   def OptionWidget(self,option) :
      filter = self.filter
      
      #Can't just add a checkbox, because the margins are too small.
      #Instead, we'll create a layout/widget so we can adjust them
      layout = QtWidgets.QHBoxLayout()
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
      
      #Have to reduce the top and bottom margins 
      margins = layout.contentsMargins()
      margins.setBottom(0)
      margins.setTop(0)
      layout.setContentsMargins(margins)   
      
      checkbox = QtWidgets.QCheckBox(option,self)
      layout.addWidget(checkbox) 
      
      #What is the current value of the option.
      #Filter option values can be set by the user's preference file
      #at start up.
      val = filter.GetOptionSetting(option)  
      
      checkbox.setChecked(val) 
      
      #Bindings are a little different for the "All" checkbox and 
      #the option checkbox   
      if (option.lower() != "all") :
         self.checkboxlist.append(checkbox)          
         checkbox.clicked.connect(self.Trigger)
      elif (option.lower() == "all") :
         self.allcheckbox = checkbox
         checkbox.clicked.connect(self.SelectAll)
      return(widget)
   
   #Called when a filter option is selected/deselected      
   def Trigger(self,value) :
      #The sender will be the checkbox from which the signal came
      sender = self.sender()  
      option = sender.text()    
      
      #Actually set the filter 
      self.filter.SetFilter(option,value)
      
      #Redetermine the value of the "all" option
      self.ConfigAllOption()
      
      #Set the column header based on the new state
      self.filter.SetHeader()
      

   #Called when the "All" option is selected/deselected 
   def SelectAll(self,selected) :      
      #select/unselect each check box
      filter = self.filter
      for checkbox in self.checkboxlist :       
         checkbox.setChecked(selected)
         #apply the filter for the option
         option = checkbox.text()
         val = checkbox.isChecked()
         filter.SetFilter(option,val)
      #Set the header icon
      filter.SetHeader()
      
   #Configure the "All" checkbox based on whether or not
   #all or some of the options have been selected  
   def ConfigAllOption(self) :
      filter = self.filter
      
      #The maximum number of boxes to be checked (+1 for "empty")
      maxchecked = len(filter.options) 
      #Count the number that have been selected
      numchecked = self.CountSelected()
      
      #Set the checkbox as appropriate      
      allaction = self.allcheckbox
      
      #If all of the options have been checked, check the "all" action
      if (numchecked == maxchecked) :
         allaction.setChecked(True)
      else :
         #otherwise, uncheck it.
         allaction.setChecked(False)
           
   #Count the number of checkboxes have been checked  
   def CountSelected(self) :
      num = 0
      for checkbox in self.checkboxlist :
         if (checkbox.isChecked()) :              
            num = num + 1           
      return(num)
      
       
        
            
class DateTimeFilter(QtWidgets.QWidget) :
   def __init__(self,label,parent=None,*args,**kwargs) :
      super(DateTimeFilter,self).__init__(parent,*args,**kwargs)
      
      layout = QtWidgets.QHBoxLayout()
      self.setLayout(layout)
      
      label = QtWidgets.QLabel(label)
      font = QtGui.QFont()
      font.setBold(True)
      label.setFont(font)
      layout.addWidget(label,0,Qt.AlignLeft)
      
      edit = QtWidgets.QDateTimeEdit(calendarPopup=True)
      edit.setDateTime(QtCore.QDateTime.currentDateTime())
      edit.setDisplayFormat("MMM-dd-yyyy hh:mm:ss")
      edit.dateChanged.connect(parent.DateChanged)
      layout.addWidget(edit,0,Qt.AlignLeft)
      
   def ApplyFilters(self) :
      print("APPLY FILTER:",self)
            
