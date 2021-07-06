from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog

from CheckableComboBox import *
from utils import *
from Actions import *
from jlab_jaws_helper.JAWSConnection import *
#from TableView import *


class OverrideDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(OverrideDialog,self).__init__(parent,*args,**kwargs)
      
      self.setModal(0)
      self.setSizeGripEnabled(True)
      
      #Layout is a simple Grid
      mainlayout = QtWidgets.QGridLayout()
      
      self.alarmsearch = AlarmSearch(self.getAlarms(),self)
      mainlayout.addWidget(self.alarmsearch,0,0)
      
      self.setLayout(mainlayout)
      self.setWindowTitle("Override Alarms")
      self.show()
   
   def getAlarms(self) :
      alarms = sorted(getAlarmNames())
      
      return(alarms)
   
   def reset(self) :
   
      self.alarmsearch.updateSearch(self.getAlarms())
      
      
#####  Override Dialog's subwidgets
class AlarmSearch(CheckableComboBox) :
   def __init__(self,alarmlist,parent=None) :
      super(AlarmSearch,self).__init__(parent)
      
     # self.setFixedWidth(200)
      self.alarmlist = ["All"]
      self.alarmlist.extend(alarmlist)
      
      self.addItems(self.alarmlist)
      self.lineEdit().setReadOnly(False)
      self.setEditText("Select")
     
      ####GOOD
      self.lineEdit().returnPressed.connect(self.take_item)
      self.textActivated.connect(self.select_item) ###
      #self.view().setMinimumWidth(10000)
   
   
   #Override the widget's initial size hint
   def sizeHint(self) :
      size = QtCore.QSize()
      height = 1 
      width = 250
      size.setHeight(height)
      size.setWidth(width)      
      return(size)

   #GOOD
   def select_item(self,alarmname) :
      if (len(alarmname) == 0) :
         return
      if (alarmname.lower() == "all") :
         return
      itemlist = self.model().findItems(alarmname)
      if (len(itemlist) == 0) :
         return      
      item = itemlist[0]      
      
      if (not item.checkState()) :
         item.setCheckState(Qt.Checked)
      
      if self.closeOnLineEditClick:
         self.hidePopup()
      else:
         self.showPopup()

   #GOOD 
   def select_all(self,allitem) :
      
      state = Qt.Checked
      if (allitem.checkState()) :
         state = Qt.Unchecked
      
      numrows = self.model().rowCount() 
      for row in range(numrows) :
         if (row == 0) :
            continue
         alarm = self.model().item(row)
         alarm.setCheckState(state)
   
   
   #GOOD
   def take_item(self) :      
      alarmname = self.lineEdit().text()  
      if (alarmname.lower() == "all") :
         print("TAKE_ITEM SELECT ALL!!!")
         return
        
      itemlist = self.model().findItems(alarmname)
      if (len(itemlist) == 0) :        
         return    
      
      self.select_item(alarmname)
   
   #GOOD
   def updateSearch(self,alarmlist) :
      
      self.clear()
      self.alarmlist = ["All"]
      self.alarmlist.extend(alarmlist)

      
      count = 0
      for alarmname in self.alarmlist :
         self.addItem(alarmname)
         item = self.model().item(count,0)
     
      completer = QtWidgets.QCompleter(alarmlist)
      completer.setCaseSensitivity(0)
      self.setCompleter(completer)
      #self.setCurrentText("Select")
      self.setEditText("Select")













#Dialog that is invoked when the user wants to shelve alarms.
class OLDOverrideDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(OverrideDialog,self).__init__(parent,*args,**kwargs)
      
      self.setModal(0)
      self.setSizeGripEnabled(True)
      
      #Layout is a simple VBox
      mainlayout = QtWidgets.QVBoxLayout()
      
      #The reason for shelving the alarm
      self.reasoncombo = OverrideReasonCombo(self)
      mainlayout.addWidget(self.reasoncombo,0,Qt.AlignCenter)
      
      #Dial widget allowing the user to set the shelflife of the alarm.
      self.overrideduration = OverrideDuration(self)
      mainlayout.addWidget(self.overrideduration,0,Qt.AlignCenter)
      
      #Remove the alarm entirely from service
      self.remove = RemoveFromService(self)
      mainlayout.addWidget(self.remove,0,Qt.AlignCenter)
      
      #Optional comments 
      commentswidget = OverrideCommentsWidget(self)
      mainlayout.addWidget(commentswidget)
      self.commentswidget = commentswidget
      
      #Buttons for the dialog
      buttonwidget = self.MakeButtons()
      mainlayout.addWidget(buttonwidget)
      
      self.setLayout(mainlayout)
      self.setWindowTitle("Override Alarms")
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
      button.clicked.connect(self.CheckOverrideConfig)
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
      
   #life 
   
   #Disable the OverrideDuration widget when "Remove from Service" is selected.     
   def DisableOverrideDuration(self,disable) :
      self.overrideduration.DisableOverrideDuration(disable)
      
   #Set the override duration dial
   def SetDial(self,value=None) :
      self.overrideduration.SetDial(value)
      
   #Calculate the override duration
   def CalculateOverrideDuration(self) :
      return(self.overrideduration.CalculateOverrideDuration())
   
   #Comments      
   def GetComments(self) :
      return(self.commentswidget.GetComments())  
   
   def ClearComments(self) :
      self.commentswidget.ClearComments()   
   
   #If dialog re-opened, clear out old info.
   def reset(self) :
      self.SetReason(0)
      self.SetRemoveState(False)
      self.SetDial()
      self.ClearComments()
    
   #Close the dialog           
   def Close(self) :
      self.close()
    
   #Override the selected alarms  
   #******NEED TO DEAL WITH REMOVED FROM SERVICE      
   
   #Has the user filled out the the required information?
   def CheckOverrideConfig(self) :
      ok = True
      message = None
      
      #Have any alarms been selected?
      numselected = getSelectedAlarms()
      if (len(numselected) == 0) :
         ok = False
         message = "Select an alarm to override"
           
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
      
      self.OverrideAlarms()
      self.Close()
   
   #Shelve the selected alarms
   def OverrideAlarms(self) :
      
      alarmlist = getSelectedAlarms()
      confirmed = ConfirmAlarms(alarmlist)
      if (not confirmed) :
         return         
            
      reason = self.GetReason()
      duration = self.CalculateOverrideDuration()   
          
      for alarm in alarmlist :
         print("OVERRIDE",alarm.get_name(),reason,duration)
       #  alarm.Override.request(reason,duration)
   
   def reset(self) :
      pass
         
#Reason for override
class OverrideReasonCombo(QtWidgets.QComboBox) :
   def __init__(self,parent=None, *args,**kwargs) :
      super(OverrideReasonCombo,self).__init__(parent,*args,**kwargs)
      
      reasonlist = ["Reason for Override"]
      reasonlist.extend(get_override_reasons())
      
      #Waiting for official list from Ops
      #reasonlist = ["Reason for Override", 'Nuisance', 'Broken', 'Maintenance']        
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
      self.parent.DisableOverrideDuration(remove)

#User selects the amount of time to shelve the alarm.
class OverrideDuration(QtWidgets.QWidget) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(OverrideDuration,self).__init__(parent,*args,**kwargs)
      
      #5 days in minutes
      self.maxlife = 7200
      self.minlife = 1
      self.defaultlife = 60
      
      #testing
      self.defaultlife = 0.1

      layout = QtWidgets.QGridLayout()
      self.setLayout(layout)
      
      label = QtWidgets.QLabel("Override Duration")
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
      dial.valueChanged.connect(self.SetOverrideDuration)
      dial.setSingleStep(10)
      dial.setRange(self.minlife,self.maxlife) 
      layout.addWidget(dial,1,0,1,3)  
      
      self.dial = dial
   
   #Called when the dial is used.
   def SetOverrideDuration(self) :
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
   def DisableOverrideDuration(self,disable) :
      if (disable) :
         self.SetDurationVal("")
         self.SetDurationUnits("")
         self.SetDialState(False)
      else :
         #If enabling the widget, 
         #call "SetShelfLife" directly.  
         self.SetOverrideDuration()
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
   def CalculateOverrideDuration(self) :      
      value = self.dial.value() * 60
      return(value)
    
#Optional user comments. Consists of a label and
#QPlainTextEdit widget
class OverrideCommentsWidget(QtWidgets.QWidget) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(OverrideCommentsWidget,self).__init__(parent)
         
      commentslayout = QtWidgets.QHBoxLayout()
      self.setLayout(commentslayout)
      
      label = QtWidgets.QLabel("Comments")
      commentslayout.addWidget(label)
      
      #Inherit from QPlainTextEdit to adjust sizeHint
      comments = OverrideCommentsEdit(self)
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
class OverrideCommentsEdit(QtWidgets.QPlainTextEdit) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(OverrideCommentsEdit,self).__init__(parent)
      
      
   #Override the widget's initial size hint
   def sizeHint(self) :
      size = QtCore.QSize()
      height = 1 
      width = 250
      size.setHeight(height)
      size.setWidth(width)      
      return(size)
