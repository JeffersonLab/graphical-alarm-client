from JAWSManager import *
from AlarmModelView import *

from utils import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

from JAWSManager import *

class ShelfManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      super(ShelfManager,self).__init__("JAWS - Alarm Shelf","shelf",
         *args,**kwargs)
     
  #    self.tableview.setColumnWidth(2,200)
   #   self.tableview.setColumnWidth(3,150)
      
      
   def ProxyModel(self) :
      proxymodel = ProxyModel()
      
      return(proxymodel)
   
   def TableView(self) :
      tableview = ShelfTable()
     # tableview.sortByColumn(3,1)
      return(tableview)
   
   def ModelView(self) :
      modelview = ShelfModel(self.data)       
      return(modelview)
      
   def StartProcessor(self) :
      self.processor = ShelfProcessor()
      
app = QtWidgets.QApplication(sys.argv)
window = ShelfManager()

app.exec()
