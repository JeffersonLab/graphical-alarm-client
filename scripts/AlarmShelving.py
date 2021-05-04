from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog

from utils import *

from AlarmModelView import *

class ShelfDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(ShelfDialog,self).__init__(parent,*args,**kwargs)
      
      self.setModal(0)
      self.setSizeGripEnabled(True)
      
      mainlayout = QtWidgets.QVBoxLayout()
      
      configuration = QtWidgets.QWidget()
      mainlayout.addWidget(configuration)
           
      layout = QtWidgets.QGridLayout()
      configuration.setLayout(layout)
      label = QtWidgets.QLabel("Reason for Shelving")
      layout.addWidget(label,0,1)
      
      self.grid = layout
      
      reasonlist = ['Select', 'Nuisance', 'Broken', 'Maintenance']
      combo = QtWidgets.QComboBox(self)
      for reason in reasonlist :
         combo.addItem(reason)
      
      layout.addWidget(combo,0,2)
      self.reasoncombo = combo
      
      timeoptions = ['Select', '5 sec', '5 min', '1 hour', '24 hours']
      radiobutton = QtWidgets.QRadioButton()
      radiobutton.toggled.connect(self.selectShelfOption)
      
      layout.addWidget(radiobutton,1,0)
      self.shelve = radiobutton
      
      label = QtWidgets.QLabel("Shelving Duration")
      layout.addWidget(label,1,1)
      
      combo = QtWidgets.QComboBox(self) 
      for time in timeoptions :
         combo.addItem(time)
      
      
      combo.currentIndexChanged.connect(self.selectDuration)
      
      layout.addWidget(combo,1,2)
      self.timecombo = combo
      
      radiobutton = QtWidgets.QRadioButton()
      radiobutton.toggled.connect(self.selectShelfOption)
      layout.addWidget(radiobutton,2,0)
      self.disable = radiobutton
      
      label = QtWidgets.QLabel("Disable Alarm") 
      layout.addWidget(label,2,1)
      
      label = QtWidgets.QLabel("Comments")
      layout.addWidget(label,3,1)
      
      comments = QtWidgets.QPlainTextEdit(self) 
      comments.resize(100,100)
      layout.addWidget(comments,3,2)
      self.comments = comments
      
      buttonwidget = QtWidgets.QWidget()
      buttonlayout = QtWidgets.QHBoxLayout()
      buttonwidget.setLayout(buttonlayout)
      mainlayout.addWidget(buttonwidget)
      
      button = QtWidgets.QPushButton("Cancel")
      buttonlayout.addWidget(button)
      button.clicked.connect(self.Cancel)
      
      button = QtWidgets.QPushButton("OK")
      buttonlayout.addWidget(button)
      button.clicked.connect(self.CheckShelfConfig)
      
      self.setLayout(mainlayout)
      self.setWindowTitle("Shelving")
      self.show()
   
   #User has selected a shelving duration.
   #Save them a click by selecting the radiobutton for them.
   def selectDuration(self,index) :
      if (index > 0) :
         self.shelve.setChecked(True)
         
   #Called when user selects to shelve for a specified amount
   #of time, or to disable the alarm until operator intervention
   #This is purely for usability purposes.
   def selectShelfOption(self) :
      
      #which radio button?
      radiobutton = self.sender()
      if (not radiobutton.isChecked()) :
         return
         
      ### We didn't define the radiobutton with text, due to 
      ### alignment, so we need to find out what label 
      ### the radiobutton is associated with. 
      ### Don't want to hard-code grid numbers, 
      ### so we'll figure out based on position
         
      #Where in the gridlayout does this radiobutton live?
      index = self.grid.indexOf(radiobutton)
      #row and column are first two elements of the position
      (row,col,r,c) = self.grid.getItemPosition(index)
         
      #the label is the next column over.         
      labelcol = col + 1
      
      #Get the text of the label to determine the option selected.
      option = self.grid.itemAtPosition(row,labelcol).widget().text()
      
      #If the radiobox is associated with the "Disable alarm" option,
      #nicely set the timecombo selection to "Select" 
      if ("disable" in option.lower()) :
         duration = self.timecombo.findText("Select")
         self.timecombo.setCurrentIndex(duration)
   
   def Reset(self) :
      self.timecombo.setCurrentIndex(0)
      self.reasoncombo.setCurrentIndex(0)
               
   def Cancel(self) :
      self.close()
   
  
            
   def ShelveAlarms(self) :
      
      alarmlist = GetSelectedAlarms()
      
      confirmed = ConfirmAlarms(alarmlist)
      if (not confirmed) :
         return
         
      reason = self.reasoncombo.currentText()
      duration = None
      if (self.shelve.isChecked()) :
         duration = self.timecombo.currentText()
      
      for alarm in alarmlist :
         alarm.ShelveRequest(reason,duration)
   
   def CheckShelfConfig(self) :
      ok = True
      message = None
      
      #Have any alarms been selected?
      numselected = CountSelectedAlarms()
      if (numselected == 0) :
         ok = False
         message = "Select an alarm to shelve"
      
      
      else :
         reason = self.reasoncombo.currentText()
         if ("Select" in reason) :
            ok = False
            #message = "Need a reason"
         else :
            selectshelf =  self.shelve.isChecked()
            selectdisable = self.disable.isChecked()
            if (not selectshelf and not selectdisable) : 
               ok = False
              # message = "Shelve or Disable"
      
            if (selectshelf) :
               shelftime = self.timecombo.currentText()
               if ("Select" in shelftime) :
                  ok = False
               #   message = "Need shelf duration"
      
      
      if (message != None) :

         msgBox = QtWidgets.QMessageBox()
         msgBox.setIcon(QtWidgets.QMessageBox.Warning)
         msgBox.setText(message)
         msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
         reply = msgBox.exec()
         return
      
      self.ShelveAlarms()
                


def ConfirmAlarms(alarmlist,which="Shelve") :
   alarmnames = []
   for alarm in alarmlist :
      alarmname = alarm.GetName()
      alarmnames.append(alarmname)
   
   
   message = which + " the following alarms?\n\n" + "\n".join(alarmnames)
   msgBox = QtWidgets.QMessageBox()
   msgBox.setIcon(QtWidgets.QMessageBox.Question)
   msgBox.setText(message)
   msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes|
      QtWidgets.QMessageBox.Cancel)
   reply = msgBox.exec()
      
   confirm = False
   if (reply == QtWidgets.QMessageBox.Yes) :
      confirm = True
         
   return(confirm)
      
class UnShelveAction(QtWidgets.QAction) :
   def __init__(self,parent,*args,**kwargs) :
      super(UnShelveAction,self).__init__(parent,*args,**kwargs)
      
      self.parent = parent
      icon = QtGui.QIcon("address-book--minus.png")
      text = "Shelf Manager"
      tip = "Shelf Manager"
      self.setIcon(icon)
      self.setIconText(text)
      self.setToolTip(tip)
      
      self.triggered.connect(self.UnShelveAlarms)
   
   def UnShelveAlarms(self) :
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
