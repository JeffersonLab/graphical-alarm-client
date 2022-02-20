from PyQt5 import QtCore, QtGui, QtWidgets

from Filters import *

   
class FilterMenu(QtWidgets.QMenu) :
   """ Menu that displays filter options. 
       Parent can be context menu/button
   """  
   def __init__(self,jawsfilter,parent=None) :
      """ Create an instancedoc
          ARGS:
            filter: The filter to which this menu belongs
            parent: The parent of the menu
      """
      super(FilterMenu,self).__init__("Filters",parent)
            
      self.parent = parent
      self.jawsfilter = jawsfilter
      
      #Keep a list of the option checkbox widgets to configure
      #as a whole
      self.checkboxlist = []
      
      #Each filter has a checkbox for "All"
      self.allcheckbox = None
      
      self.setTearOffEnabled(True) 
      title = jawsfilter.getName().capitalize() + " Filters"   
      self.addSection(title)
  
      options = jawsfilter.getFilterOptions()
      self.jawsfilteroptions = options
      #Create the options for this filter
      self.makeOptions()
 
    
   def makeOptions(self) :
      """ Add the filter options to the menu
      """
      jawsfilter = self.jawsfilter
      optionstate = jawsfilter.getCurrentState()

      options = jawsfilter.getFilterOptions()
      
      if (options == None) :
         return
      
      #Create a widget for each fitler option
      for status in options :
         widget = self.optionWidget(status)
         action = QtWidgets.QWidgetAction(self)
         action.setDefaultWidget(widget)
         self.addAction(action)
         if (status.lower() == "all" or status.lower() == "empty") :
            self.addSeparator()
            
      #Determine the state of the "All" option
      self.configAllOption()
      
      return
   
   def optionWidget(self,option=None) :
      """ Create an "option" widget to work around unwanted contextmenu 
          behavior -- automatically closing when a checkbox is selected/deselected
          We want the user to be able to select/deselect more than one...
      """
      
      jawsfilter = self.jawsfilter
      
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
           
      checkbox = self.optionSelectWidget(option) #QtWidgets.QCheckBox(option,self)
      layout.addWidget(checkbox) 
            
      if (option.lower() == "all") :
         self.allcheckbox = checkbox
      
      #What is the current value of the option.
      #Filter option values can be set by the user's preference file
      #at start up.
      val = jawsfilter.getOptionState(option)  
   
      checkbox.setChecked(val) 
      #Bindings are a little different for the "All" checkbox and 
      #the option checkbox   
      if (option != None and option.lower() != "all") :
         self.checkboxlist.append(checkbox)
         checkbox.clicked.connect(self.trigger)
      elif (option != None and option.lower() == "all") :
         checkbox.clicked.connect(self.selectAll)
      return(widget)
   
   
   def optionSelectWidget(self,option=None) :
      """ The widget the user selects from the menu
      """
      widget = QtWidgets.QCheckBox(option,self)
      return(widget)
   
   
   def trigger(self,checked) :
      """  Called when a filter option is selected/deselected    
           ARGS:
            checked : True/False option checkbox checked  
      """
      #The sender will be the checkbox from which the signal came
      sender = self.sender()  
      option = sender.text()    
      print("MENU TRIGGERED",sender,option)
      #Actually set the filter 
      self.jawsfilter.setFilter(option,checked)
     
      #Redetermine the value of the "all" option
      self.configAllOption()
      
      #Set the column header based on the new state
      self.jawsfilter.setHeader()
      
   
   def selectAll(self,checked) :      
      """ Called when the "All" option is selected/deselected 
      """
      #select/unselect each check box
      jawsfilter = self.jawsfilter      
      for checkbox in self.checkboxlist :       
         checkbox.setChecked(checked)
         #apply the filter for the option
         option = checkbox.text()
         jawsfilter.setFilter(option,checked)
      
      #Set the header icon
      jawsfilter.setHeader()
      
   def configAllOption(self) :
      """ Configure the "All" checkbox based on whether or not
          all or some of the options have been selected  
      """
      jawsfilter = self.jawsfilter
      
      #The maximum number of boxes to be checked (+1 for "empty")
      maxchecked = len(jawsfilter.options) 
      if ("All" in jawsfilter.options) :
         maxchecked = maxchecked - 1
      
      #Count the number that have been selected
      numchecked = self.countSelected()
 
      #Set the checkbox as appropriate      
      allaction = self.allcheckbox
      #If all of the options have been checked, check the "all" action
      if (numchecked == maxchecked) :
         allaction.setChecked(True)
      else :
         #otherwise, uncheck it.
         allaction.setChecked(False)
           
   #Count the number of checkboxes have been checked  
   def countSelected(self) :
      """Count the number of checkboxes have been checked  
      """
      num = 0
      filter = self.jawsfilter
 
      for checkbox in self.checkboxlist :
         if (checkbox != self.allcheckbox) :
            if (checkbox.isChecked()) :              
               num = num + 1           
      return(num)
      
class ExclusiveFilterMenu(FilterMenu) :
   def __init__(self,jawsfilter,parent=None) :
      """ Exclusive filter -- only one option can be selected at a time
      """
      super(ExclusiveFilterMenu,self).__init__(jawsfilter,parent)
   
   def makeOptions(self) :
      """ Add the filter options to the menu
      """
      
      #For ExclusiveFilters the options are a set of radiobuttons
      jawsfilter = self.jawsfilter
      optionstate = jawsfilter.getCurrentState()
      options = jawsfilter.getFilterOptions()
      if (options == None) :
         return
 
      widget = self.optionWidget(options)
      action = QtWidgets.QWidgetAction(self)
      action.setDefaultWidget(widget)
      self.addAction(action)
      
      return

   def optionWidget(self,options) :
      #return(super().optionWidget(option))
      """ Option widget is a collection of radiobuttons
      """
        
      jawsfilter = self.jawsfilter
      optionstate = jawsfilter.getCurrentState()
      #Can't just add a checkbox, because the margins are too small.
      #Instead, we'll create a layout/widget so we can adjust them
      layout = QtWidgets.QVBoxLayout()
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
 
      for option in options :
         checkbox = QtWidgets.QRadioButton(option,self)
         val = jawsfilter.getOptionState(option)  
         checkbox.setChecked(val) 
 
         layout.addWidget(checkbox) 
         self.checkboxlist.append(checkbox)
         checkbox.toggled.connect(self.trigger)         
      
      return(widget)
   
   def optionSelectWidget(self,option) :
      """ The widget the user selects from the menu
      """
      widget = QtWidgets.QRadioButton(option, self)
      return(widget)
   
   def selectAll(self,checked) :      
      """ Called when the "All" option is selected/deselected 
          Not applicable for a ExclusiveFilterMenu
      """
      return
   
   def configAllOption(self) :
      """ Called when the "All" option is selected/deselected 
           Not applicable for a ExclusiveFilterMenu
      """
      return
     
      
