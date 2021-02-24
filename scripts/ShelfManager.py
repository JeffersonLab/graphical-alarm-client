from JAWSManager import *
from AlarmModelView import *

from utils import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

from ShelfProcessor import *

class ShelfMenuBar(QtWidgets.QMenuBar) :
   def __init__(self,parent,*args,**kwargs) :
      
      super(ShelfMenuBar,self).__init__(parent,*args,**kwargs)          
      filemenu = self.addMenu("File")
      
      shelfaction = QAction("Launch Active Alarm Manager",self)
      shelfaction.triggered.connect(self.launchAlarmManager)
      filemenu.addAction(shelfaction)
      
      exitaction = QAction("Quit",self)
      exitaction.triggered.connect(parent.closeEvent)
      filemenu.addAction(exitaction)

   def launchAlarmManager(self,event) :
      command = "python3 " + SOURCEDIR + "AlarmManager.py &"
      os.system(command)
      

class ShelfToolBar(ToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(ShelfToolBar,self).__init__(parent,*args,**kwargs)
     
      unshelfaction = UnShelveAction(self)
      self.addAction(unshelfaction)

class ShelfManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      self.threadlist = []
      self.workerlist = []
      self.shelfqueue = []
     
      super(ShelfManager,self).__init__("JAWS - Alarm Shelf","shelf",
         *args,**kwargs)
     
      self.tableview.setColumnWidth(2,150)
      self.tableview.setColumnWidth(3,150)
      self.tableview.setColumnWidth(6,250)
            
   def ProxyModel(self) :
      proxymodel = ProxyModel()
      
      return(proxymodel)
   
   def TableView(self) :
      tableview = ShelfTable()
      tableview.sortByColumn(2,1)
      return(tableview)
   
   def ModelView(self) :
      modelview = ShelfModel(self.data)       
      return(modelview)
   
   def FilterDialog(self) :
      filterdialog = ShelfFilterDialog()
      return(filterdialog)
   
   def MenuBar(self) :
      menubar = ShelfMenuBar(self)
      return(menubar)

      
   def ToolBar(self) :
      toolbar = ShelfToolBar(self)
      return(toolbar)

   def StartProcessor(self) :
      self.processor = ShelfProcessor()
      self.EmptyQueue()
    
   #Creates the expiration countdown thread   
   def StartCountDown(self,alarm) :
      print(alarm.GetName(),"counting",alarm.counting)
      thread = QThreadPool()      
      
      worker = Worker(alarm.CalcTimeLeft,alarm.delay)
     
      worker.signals.output.connect(self.CountDown)
 
      #alarm.thread = thread
      alarm.worker = worker
      thread.start(worker)
      if (not thread in self.threadlist) :
         self.threadlist.append(thread)
      if (not worker in self.workerlist) :
         self.workerlist.append(worker)
  
 
         
   def CountDown(self,alarm) :      
      
     
      if (not alarm in GetModel().data) :
        
         timeleft = None
      else :         
         timeleft = alarm.timeleft
        
      if (timeleft != None) :
            
         row = GetModel().data.index(alarm)
         index = GetModel().createIndex(row,0)
         GetModel().dataChanged.emit(index,index,[Qt.DisplayRole])
         
      else :
         worker = alarm.worker
         worker.stop()
         alarm.worker = None
   
   def stopWorker(self) :
      super().stopWorker()
      try :
         for worker in self.workerlist :           
            worker.stop()
         for thread in self.threadlist :
            thread.join()
      except :
         pass
   
   
   def EmptyQueue(self) :
          
      for alarm in self.shelfqueue :
         if (alarm.counting or alarm.GetShelfExpiration() == None) :
            return
         worker = None
         alarm.counting = True
         self.StartCountDown(alarm)
               
   def AddToQueue(self,alarm) :
      if (alarm.GetShelfExpiration() == None) :
         return
      if (not alarm in self.shelfqueue) :
         self.shelfqueue.append(alarm)  


app = QtWidgets.QApplication(sys.argv)
window = ShelfManager()

app.exec()
