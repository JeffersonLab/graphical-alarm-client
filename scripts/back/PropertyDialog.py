from PyQt5.QtCore import Qt

from utils import *
from Actions import *


#Parent property dialog
#Active Alarms have slightly different properties than Shelved
class PropertyDialog(QtWidgets.QDialog) :
   def __init__(self,alarm,parent=None,*args,**kwargs) :
      super(PropertyDialog,self).__init__(parent,*args,**kwargs)
      
      self.row = None
      self.alarm = alarm
      
      #These properties are common to both types of dialog
      self.propwidgets = {
         'name' : 
            {'widget' : None, 'command' : self.alarm.GetName,
             'label': "Name:", 'static' : True},
         'type' : 
            {'widget' : None, 'command' : self.alarm.GetType,
            'label' : "Alarm Type:", 'static' : True},
         'trigger' :
            {'widget' : None, 'command' : self.alarm.GetTrigger,
            'label' : "Trigger:", 'static' : True},
         'latching' : 
            {'widget' : None, 'command' : self.GetLatching,
            'label' : "Latching:", 'static' : True},
         'location' :
           {'widget' : None, 'command' : self.alarm.GetLocation,
            'label' : "Location:", 'static' : True},
         'category' :
            {'widget' : None, 'command' : self.alarm.GetCategory,
            'label' : "Category:", 'static' : True},
      }
      
      self.setModal(False)
      self.setSizeGripEnabled(True)
      
      layout = QtWidgets.QGridLayout()
      layout.setHorizontalSpacing(10)
      self.layout = layout
      
      #Add these first. The individual dialogs will add their 
      #specialized properties. Then, the parent will add the rest
      #of the common props.
      self.addProperty('name')
      self.addProperty('type')
      self.addSpacer()
      
      groupbox = QtWidgets.QGroupBox(self.alarm.GetName() + " Properties")
      groupbox.setLayout(layout)
      
      vlayout = QtWidgets.QVBoxLayout()
      
      #Don't let the widget be resized
      vlayout.setSizeConstraint(3)
      vlayout.addWidget(groupbox)
     
      buttons = self.MakeButtons()
      vlayout.addWidget(buttons)
                                 
      self.setLayout(vlayout)
      self.setWindowTitle(self.alarm.GetName())
      
      self.show()
   
   #Properties can be static. If that's the case, they
   #will not be updated when the alarm changes state   
   def IsStatic(self,prop) :
      static = False
      if ("static" in self.propwidgets[prop]) :
         static = True
      return(static)
   
   #Add a simple property widget.
   #Comprised of a label for the property name
   #and a label displaying the value.
   #The value label is returned to be updated if applicable
   def addProperty(self,prop) :
      
      row = self.NextRow()
      layout = self.layout
      
      propconfig = self.propwidgets[prop]
      text = propconfig['label']
      command = propconfig['command']
      format = False
      if ("format" in propconfig) :
         format = True
      
      #The property name   
      label = MakeLabel(text)
      layout.addWidget(label,row,0) 
      
      #Call the command defined in the propwidgets dictionary for this property
      val = command()
      
      #If it is a time value, it needs to be formatted before display
      if (format) :
         val = FormatTime(val)
      
      label = QtWidgets.QLabel(val)
      layout.addWidget(label,row,1)
      return(label)
    
   #Update dynamic properties and buttons
   def ConfigureProperties(self) :
      for prop in self.propwidgets :
         if (not self.IsStatic(prop)) :
            self.updateProperty(prop)
      self.UpdateButtons()
      
   def UpdateButtons(self) :
      pass
      
   #Update the property if its value changes.
   def updateProperty(self,prop) :
      widget = self.propwidgets[prop]['widget']    
      if (widget ==  None) :
         return     
      command = self.propwidgets[prop]['command'] 
      val = command() 
      if ("format" in self.propwidgets[prop]) :
         val = FormatTime(val)         
      widget.setText(val)

   #Common properties to add to the PropertyDialog
   def AddProperties(self) :
      layout = self.layout
       
      self.addSpacer()
      self.addProperty('trigger')
      self.addProperty('latching')
  
      self.addSpacer()
      
      self.addProperty('location')
      self.addProperty('category')
      self.addSpacer()
      
      #These are special widgets
      self.addURL()
      self.addScreen()
   
   #Spacer widget to insert blank row   
   def addSpacer(self) :
      row = self.NextRow()
      layout = self.layout
      spacer = QtWidgets.QLabel()
      layout.addWidget(spacer,row,0)
   
   #Little utility so that it's not necessary to keep track
   #of the rows in case more/less are needed.
   def NextRow(self) :
      row = self.row
      if (row != None) :
        row = row + 1
      else :
         row = 0
      self.row = row
      return(row)
   
   #Does the alarm latch? 
   #Translate the bool into a string for display
   def GetLatching(self) :    
      islatching = self.alarm.IsLatching()
      if (islatching) :
         islatching = "True"
      else :
         islatching = "False"
      return(islatching)
   
   #The following are specialized widgets
  
   #EDM screen assigned to alarm
   def addScreen(self) :
      row=self.NextRow()
      layout = self.layout
      label = MakeLabel("Screen:")
      layout.addWidget(label,row,0)
      
      screenpath = self.alarm.GetScreenPath()
      screenpath = "Push for your screen"
      screenbutton = QtWidgets.QPushButton(screenpath)
      layout.addWidget(screenbutton,row,1)
   
   #Reference url  
   def addURL(self) :
      row = self.NextRow()
      layout = self.layout
      
      label = MakeLabel("Documentation:")
      layout.addWidget(label,row,0)
      
      docurl = self.alarm.GetURL()
      urllabel = QtWidgets.QLabel()
      
      urllabel.setText(
         "<a href=\"http://jlab.org/\">Alarm wiki for " + 
            self.alarm.GetName() + "</a>")
      urllabel.setTextFormat(Qt.RichText)
      urllabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
      urllabel.setOpenExternalLinks(True)
      layout.addWidget(urllabel,row,1)
   
   #Close the dialog
   def Close(self) :
      self.close()
   
   #Ability to shelve an alarm is common to all dialogs
   def ShelveAlarm(self) :
     
      self.shelfaction.PerformAction()
      self.shelfbutton.setEnabled(False)

      
#Create a ShelfPropertyDialog for use with the shelf manager 
class ShelfPropertyDialog(PropertyDialog) :
   def __init__(self,parent=None,*args,**kwargs) :   

      super(ShelfPropertyDialog,self).__init__(parent,*args,**kwargs)
     
      #Add specialize shelf properties to the propwidget dictionary
      self.propwidgets['shelftime'] = \
                     {'widget' : None, 'command' : self.alarm.GetShelfTime,
                     'format' : True, 'label' : "Date Shelved:"}
      self.propwidgets['exptime'] = \
                      {'widget' : None, 
                      'command' : self.alarm.GetShelfExpiration,
                      'format' : True, 'label' : "Expires:"}      
      self.AddProperties()
    
   #Static/common properties will be created by the parent dialog
   def AddProperties(self) :
      
      for prop in self.propwidgets :
         if (not self.IsStatic(prop)) :
            widget = self.addProperty(prop)
            self.propwidgets[prop]['widget'] = widget
         
      super().AddProperties()
      self.ConfigureProperties()
   
   #Create the buttons appropriate for the ShelfProperty
   def MakeButtons(self) :
      layout = QtWidgets.QHBoxLayout()
      
      self.unshelveaction = UnShelveAction(self)
      button = QtWidgets.QPushButton("Un-Shelve")
      button.clicked.connect(self.UnShelveAlarm)
      layout.addWidget(button)
      self.unshelvebutton = button
 
      button = QtWidgets.QPushButton("Close")
      layout.addWidget(button)
      button.clicked.connect(self.Close)
      
      self.shelfaction = ShelfAction(self)
      button = QtWidgets.QPushButton("Shelve")
      button.clicked.connect(self.ShelveAlarm)      
      layout.addWidget(button)
      self.shelfbutton = button
     
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
      return(widget)     
   
   #Unshelve the alarm
   def UnShelveAlarm(self) :
             
      self.unshelveaction.PerformAction()
      self.unshelvebutton.setEnabled(False)
   
   #Update the "un-shelve" button if shelf state changes 
   def UpdateButtons(self) :
      self.unshelvebutton.setEnabled(True)
      if (not self.alarm.IsShelved()) :
         self.unshelvebutton.setEnabled(False)


#ActiveAlarm specific property dialog            
class AlarmPropertyDialog(PropertyDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      
      self.ackbutton = None
      self.shelfbutton = None
      super(AlarmPropertyDialog,self).__init__(parent,*args,**kwargs)
      
      #Add specialize shelf properties to the propwidget dictionary
      self.propwidgets['lastalarm'] = \
                     {'widget' : None, 'command' : self.alarm.GetTimeStamp,
                     'format' : True, 'label' : "Last Alarm:"}
      self.propwidgets['acktime'] = \
                      {'widget' : None, 
                      'command' : self.alarm.GetAckTime,
                      'format' : True, 'label' : "Last Ack:"}
            
      self.AddProperties()

   #Active alarms have fields for "last alarm" and "last ack'd" times.
   def AddProperties(self) :
      self.propwidgets['lastalarm']['widget'] = self.addProperty('lastalarm')     
      if (self.alarm.IsLatching()) :
         self.propwidgets['acktime']['widget'] = self.addProperty('acktime')
      
      #Add the common properties defined in PropertyDialog
      super().AddProperties()
      
      #They will be re-configured if changed
      self.ConfigureProperties()
   
   #Update dynamic properties
   def ConfigureProperties(self) :
      super().ConfigureProperties()
      
      #Updating the border is specialized
      self.UpdateBorder()
      self.UpdateButtons()
   
   #Configure buttons based on current state
   def UpdateButtons(self) :
      self.shelfbutton.setEnabled(True)
      
      if (self.ackbutton == None) :
         return
      if (self.alarm.GetLatchSevr() == None) :         
         self.ackbutton.setEnabled(False)
      else :
         self.ackbutton.setEnabled(True)
                  
   #Update the border based on the alarm's severity
   def UpdateBorder(self) :
      color = GetStatusColor(self.alarm.GetSevr())
      
      border = "border: 5px solid " + color
      stylesheet = self.styleSheet()
      style = "QDialog" + "{" + "border: 5px solid " + color + ";" +  "}"      
      self.setStyleSheet(style)

      
   #Create the buttons appropriate for the AlarmProperty
   def MakeButtons(self) :
      layout = QtWidgets.QHBoxLayout()
      
      if (self.alarm.IsLatching()) :
         button = QtWidgets.QPushButton("Acknowledge")
         layout.addWidget(button)
         self.ackbutton = button
         button.clicked.connect(self.alarm.AcknowledgeAlarm)
      
      
      button = QtWidgets.QPushButton("Close")
      layout.addWidget(button)
      button.clicked.connect(self.Close)
      
      self.shelfaction = ShelfAction(self)
      self.shelfbutton = QtWidgets.QPushButton("Shelve")
      self.shelfbutton.clicked.connect(self.ShelveAlarm)
      
      layout.addWidget(self.shelfbutton)
           
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
      return(widget)  
