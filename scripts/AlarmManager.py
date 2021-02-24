from JAWSManager import *
from AlarmModelView import *

from utils import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

from JAWSManager import *
from AlarmShelving import *

class AlarmToolBar(ToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(AlarmToolBar,self).__init__(parent,*args,**kwargs)
     
      shelfaction = ShelfAction(self)
      self.addAction(shelfaction)
   
class AlarmMenuBar(QtWidgets.QMenuBar) :
   def __init__(self,parent,*args,**kwargs) :
      
      super(AlarmMenuBar,self).__init__(parent,*args,**kwargs)          
      filemenu = self.addMenu("File")
      
      shelfaction = QAction("Launch Shelf Manager",self)
      shelfaction.triggered.connect(self.launchShelfManager)
      filemenu.addAction(shelfaction)
      
      exitaction = QAction("Quit",self)
      exitaction.triggered.connect(parent.closeEvent)
      filemenu.addAction(exitaction)
   
   
   def launchShelfManager(self,event) :
      command = "python3 " + SOURCEDIR + "ShelfManager.py &"
      os.system(command)
      
class AlarmManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      super(AlarmManager,self).__init__("JAWS - Active Alarm Manager","alarm",
         *args,**kwargs)
     
      self.tableview.setColumnWidth(2,200)
      self.tableview.setColumnWidth(3,150)
      
   
   def ToolBar(self) :
      toolbar = AlarmToolBar(self)
      return(toolbar)
         
   def ProxyModel(self) :
      proxymodel = ProxyModel()
      
      return(proxymodel)
   
   def TableView(self) :
      tableview = AlarmTable()
      tableview.sortByColumn(3,1)
      return(tableview)
   
   def ModelView(self) :
      modelview = AlarmModel(self.data) 
      
      return(modelview)


   def MenuBar(self) :
      menubar = AlarmMenuBar(self)
      return(menubar)

   def StartProcessor(self) :
      self.processor = AlarmProcessor()
      
   def FilterDialog(self) :
      filterdialog = AlarmFilterDialog()
      return(filterdialog)
  
   def ShelfDialog(self) :
      shelfdialog = ShelfDialog()
      return(shelfdialog)
   
app = QtWidgets.QApplication(sys.argv)
window = AlarmManager()

app.exec()
