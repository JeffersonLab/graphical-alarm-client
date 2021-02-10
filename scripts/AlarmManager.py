from JAWSManager import *
from AlarmModelView import *

from utils import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

from JAWSManager import *

class AlarmManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      super(AlarmManager,self).__init__("JAWS - Active Alarm Manager","alarm",
         *args,**kwargs)
     
      self.tableview.setColumnWidth(2,200)
      self.tableview.setColumnWidth(3,150)
      
      
   def ProxyModel(self) :
      proxymodel = AlarmProxyModel()
      
      return(proxymodel)
   
   def TableView(self) :
      tableview = AlarmTable()
      tableview.sortByColumn(3,1)
      return(tableview)
   
   def ModelView(self) :
      modelview = AlarmModel(self.data) 
      #print("INIT",modelview)
      return(modelview)
      
      
app = QtWidgets.QApplication(sys.argv)
window = AlarmManager()

app.exec()
