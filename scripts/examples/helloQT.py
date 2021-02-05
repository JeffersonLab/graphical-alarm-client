#####!/usr/local/bin/python3


####! /Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class AlarmModel(QtCore.QAbstractTableModel) :
   def __init__(self,data,parent = None, *args) :
      super(AlarmModel,self).__init__(parent,*args) 
      
      self.data = data
   
   def data(self,index,role) :
      row = index.row()
      col = index.column()
      
      if role == Qt.DisplayRole :
         alarm = self.data[row]
         if (col == 0) :
            return(alarm.name)
         if (col == 1) :  
            return(alarm.time)
            
   def rowCount(self,index) :
      return(len(self.data))
   
   def columnCount(self,index) :      
      return(2)
   
   def headerData(self,section,orientation,role) :
      if (role != Qt.DisplayRole) :
         return
      if (orientation != Qt.Horizontal) :
         return
         
      if (section == 0) :
         return("Name")
      if (section == 1) :
         return("TimeStamp")

class Alarm(object) :
   def __init__(self,num) :
      self.name = "channel" + str(num)
      self.time = "time of alarm " + str(num*2)
            

#Only one widget for a main window
class MainWindow(QtWidgets.QMainWindow) :
   def __init__(self,*args,**kwargs) :
      super(MainWindow,self).__init__(*args,**kwargs)
      self.setWindowTitle("JAWS")
      
      alarmpane = QtWidgets.QTableView()
      data = []
      for i in range(5) :
         data.append(Alarm(i))
         
      alarmmodel = AlarmModel(data)
      alarmpane.setModel(alarmmodel)
      
      self.setCentralWidget(alarmpane)
      
app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
