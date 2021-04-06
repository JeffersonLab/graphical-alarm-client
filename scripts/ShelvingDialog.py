from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog

from utils import *
from Actions import GetSelectedAlarms
from TableView import *

#Dialog that is invoked when the user wants to shelve alarms.
class ShelfDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(ShelfDialog,self).__init__(parent,*args,**kwargs)
      
      self.setModal(0)
      self.setSizeGripEnabled(True)
      
      #Layout is a simple VBox
      mainlayout = QtWidgets.QVBoxLayout()
      
      #The reason for shelving the alarm
      self.reasoncombo = ShelfReasonCombo(self)
      mainlayout.addWidget(self.reasoncombo,0,Qt.AlignCenter)
      
      #Dial widget allowing the user to set the shelflife of the alarm.
      self.shelflife = ShelfLife(self)
      mainlayout.addWidget(self.shelflife,0,Qt.AlignCenter)
      
      #Remove the alarm entirely from service
      self.remove = RemoveFromService(self)
      mainlayout.addWidget(self.remove,0,Qt.AlignCenter)
      
      #Optional comments 
      commentswidget = ShelvingCommentsWidget(self)
      mainlayout.addWidget(commentswidget)
      self.commentswidget = commentswidget
      
      #Buttons for the dialog
      buttonwidget = self.MakeButtons()
      mainlayout.addWidget(buttonwidget)
      
      self.setLayout(mainlayout)
      self.setWindowTitle("Shelving")
      self.show()
      
   #Create the buttons associated with this dialog
   def MakeButtons(self) :
      buttonwidget = QtWidgets.QWidget()
      buttonlayout = QtWidgets.QHBoxLayout()
      buttonwidget.setLayout(buttonlayout)
      
      button = QtWidgets.QPushButton("Cancel")
      buttonlayout.addWidget(button)
      button.clicked.connect(self.Close)
      
      button = QtWidgets.QPushButton("OK")
      buttonlayout.addWidget(button)
      button.clicked.connect(self.CheckShelfConfig)
      return(buttonwidget)
   
   #Access the dialog's subwidgets, and methods
   #All actions pertaining to the subwidgets, are handled through the
   #dialog.
   
   #Reason
   def GetReason(self) :
      return(self.reasoncombo.GetReason())
   
   def SetReason(self,index=0) :
      self.reasoncombo.SetReason(index)
   
   #Remove from service
   def GetRemoveState(self) :
      return(self.remove.GetRemoveState())

   def SetRemoveState(self,remove) :
      self.remove.SetRemoveState(remove)
      
   #Shelflife 
   
   #Disable the ShelfLife widget when "Remove from Service" is selected.     
   def DisableShelfLife(self,disable) :
      self.shelflife.DisableShelfLife(disable)
      
   #Set the shelflife dial
   def SetDial(self,value=None) :
      self.shelflife.SetDial(value)
      
   #Calculate the shelflife
   def CalculateShelfLife(self) :
      return(self.shelflife.CalculateShelfLife())
   
   #Comments      
   def GetComments(self) :
      return(self.commentswidget.GetComments())  
   
   def ClearComments(self) :
      self.commentswidget.ClearComments()   
   
   #If dialog re-opened, clear out old info.
   def Reset(self) :
      self.SetReason(0)
      self.SetRemoveState(False)
      self.SetDial()
      self.ClearComments()
    
   #Close the dialog           
   def Close(self) :
      self.close()
    
   #Shelve the selected alarms  
   #******NEED TO DEAL WITH REMOVED FROM SERVICE      
   
   #Has the user filled out the the required information?
   def CheckShelfConfig(self) :
      ok = True
      message = None
      
      #Have any alarms been selected?
      numselected = GetSelectedAlarms()
      if (len(numselected) == 0) :
         ok = False
         message = "Select an alarm to shelve"
           
      else :
         reason = self.GetReason()         
         if ("reason" in reason.lower()) :
            ok = False
            message = "Need a reason"      
      
      #Inform the user 
      if (message != None) :

         msgBox = QtWidgets.QMessageBox()
         msgBox.setIcon(QtWidgets.QMessageBox.Warning)
         msgBox.setText(message)
         msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
         reply = msgBox.exec()
         return
      
      self.ShelveAlarms()
      self.Close()
   
   #Shelve the selected alarms
   def ShelveAlarms(self) :
      
      alarmlist = GetSelectedAlarms()
      confirmed = ConfirmAlarms(alarmlist)
      if (not confirmed) :
         return         
      
      
      reason = self.GetReason()
      duration = self.CalculateShelfLife()       
      for alarm in alarmlist :
         alarm.ShelveRequest(reason,duration)

         
#####  Shelf Dialog's subwidgets

#Reason for shelving. 
class ShelfReasonCombo(QtWidgets.QComboBox) :
   def __init__(self,parent=None, *args,**kwargs) :
      super(ShelfReasonCombo,self).__init__(parent,*args,**kwargs)
      
      #Waiting for official list from Ops
      reasonlist = ["Reason for Shelving", 'Nuisance', 'Broken', 'Maintenance']        
      for reason in reasonlist :
         self.addItem(reason)  
      
      #Have to do this little dance in order to make the
      #text centered. 
      self.setEditable(True)
      lineedit = self.lineEdit()      
      lineedit.setAlignment(Qt.AlignCenter)
      lineedit.setReadOnly(True)
      
      #Make sure the width is reasonable.
      self.setFixedWidth(200)
   
   #Setter and getter
   def SetReason(self,index) :
      self.setCurrentIndex(index)
      
   def GetReason(self) :
      return(self.currentText())  

#Remove from service option
class RemoveFromService(QtWidgets.QRadioButton) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(RemoveFromService,self).__init__(
         "Remove from Service",parent,*args,**kwargs)
      
      self.parent = parent  
      self.toggled.connect(self.RemoveFromService) 
   
   def SetRemoveState(self,remove = True) :
      self.setChecked(remove)
      
   def GetRemoveState(self) :
      return(self.isChecked())
      
   def RemoveFromService(self,remove) :
      self.parent.DisableShelfLife(remove)

#User selects the amount of time to shelve the alarm.
class ShelfLife(QtWidgets.QWidget) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(ShelfLife,self).__init__(parent,*args,**kwargs)
      
      #5 days in minutes
      self.maxlife = 7200
      self.minlife = 1
      self.defaultlife = 60
      
      #testing
      self.defaultlife = 0.1

      layout = QtWidgets.QGridLayout()
      self.setLayout(layout)
      
      label = QtWidgets.QLabel("Shelf Life")
      layout.addWidget(label,0,0)
      
      #dial readback
      val = QtWidgets.QLineEdit()
      val.setReadOnly(True)
      val.setAlignment(Qt.AlignRight)
      val.setFixedWidth(50)
      val.setText(str(self.defaultlife))
      layout.addWidget(val,0,1)      
      self.lifeval = val
      
      #units will change based on the number of minutes dialed in.
      units = QtWidgets.QLabel("mins")
      units.setFixedWidth(50)
      
      layout.addWidget(units,0,2)
      self.lifeunits = units
      
      #The dial widget
      dial = QtWidgets.QDial()
      dial.setMinimum(1)
      dial.setMaximum(self.maxlife) 
      dial.setValue(self.defaultlife)
      dial.setNotchesVisible(True)
      dial.valueChanged.connect(self.SetShelfLife)
      dial.setSingleStep(10)
      dial.setRange(self.minlife,self.maxlife) 
      layout.addWidget(dial,1,0,1,3)  
      
      self.dial = dial
   
   #Called when the dial is used.
   def SetShelfLife(self) :
      #value will be in minutes
      value = self.dial.value()      
      
      #How many hours and days?  
      hours = value/60
      days = hours/24      
      
      #convert to hours, and change the units
      if (hours > 1 and days < 1) :
         units = "hours"
         value = '{:0.2f}'.format(hours)
      #convert to days and change the units
      elif (days > 1) :
         units = "days"
         value = '{:0.2f}'.format(days)     
      #units are min
      else :      
         units = "mins"
      
      #Update the readback and the units
      self.SetLifeVal(str(value))
      self.SetLifeUnits(units)

   #Disable/enable the widget when 
   #"Remove from Service" selected/deselected
   def DisableShelfLife(self,disable) :
      if (disable) :
         self.SetLifeVal("")
         self.SetLifeUnits("")
         self.SetDialState(False)
      else :
         #If enabling the widget, 
         #call "SetShelfLife" directly.  
         self.SetShelfLife()
         self.SetDialState(True)
   
   #Set the value for the dial readback
   def SetLifeVal(self,value) :
      lifeval = self.lifeval
      lifeval.setText(value)
   
   #update the units for the dial
   def SetLifeUnits(self,units) :
      lifeunits = self.lifeunits
      lifeunits.setText(units)
   
   #enable/disable the dial
   def SetDialState(self,enabled=True) :
      self.dial.setEnabled(enabled)

   #Set the dial explicitly.
   #If a value is not passed in, use the default
   def SetDial(self,value=None) :
      if (value == None) :
         value = self.defaultlife
      self.dial.setValue(value)
               
   #The dial is in minutes, convert to seconds
   def CalculateShelfLife(self) :      
      value = self.dial.value() * 60
      return(value)
    
#Optional user comments. Consists of a label and
#QPlainTextEdit widget
class ShelvingCommentsWidget(QtWidgets.QWidget) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(ShelvingCommentsWidget,self).__init__(parent)
         
      commentslayout = QtWidgets.QHBoxLayout()
      self.setLayout(commentslayout)
      
      label = QtWidgets.QLabel("Comments")
      commentslayout.addWidget(label)
      
      #Inherit from QPlainTextEdit to adjust sizeHint
      comments = ShelvingCommentsEdit(self)
      commentslayout.addWidget(comments)
      comments.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
         QtWidgets.QSizePolicy.MinimumExpanding)
      self.editcomments = comments
   
   #Get the contents of the comment widget   
   def GetComments(self) :
      return(self.editcomments.toPlainText())
   
   #Clear the comments widget  
   def ClearComments(self) :
      self.editcomments.clear()   


#Create subclass in order to override sizeHint     
class ShelvingCommentsEdit(QtWidgets.QPlainTextEdit) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(ShelvingCommentsEdit,self).__init__(parent)
      
      
   #Override the widget's initial size hint
   def sizeHint(self) :
      size = QtCore.QSize()
      height = 1 
      width = 250
      size.setHeight(height)
      size.setWidth(width)      
      return(size)
