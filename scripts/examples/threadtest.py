import signal

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRunnable,QThreadPool, \
   QTimer

from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QMainWindow,\
   QVBoxLayout, QLabel
   
import traceback
import time 

from AlarmMonitor import *
  

class WorkerSignals(QObject) :
   finished = pyqtSignal()
   error = pyqtSignal(tuple)
   result = pyqtSignal(object)
   model = pyqtSignal(int)
   

   
#Worker thread
class Worker(QRunnable) :
   
   def __init__(self,monitor) :
      super(Worker,self).__init__()
      #self.fn = fn 
      #self.args = args
      #self.kwargs = kwargs
      self.monitor = monitor
      self.running = True
      #self.signals = WorkerSignals()
      #self.kwargs['model_callback'] = self.signals.model
      self.count = 0
      
   #This is where the monitor code goes
   def run(self) :
      
      while (self.running) :
         self.monitor.Monitor()
         time.sleep(1)
         self.count = self.count + 1
      
      try:
         
         result = self.fn(*self.args,**self.kwargs)
      except:
         traceback.print_exc()
         exctype,value = sys.exc_info()[:2]
         self.signals.error.emit((exctype,value,traceback.format_exc()))
      else :
         self.signals.result.emit(result)
      finally:
         self.signals.finished.emit()

         
class AlarmModel(QtCore.QAbstractTableModel) :
   def __init__(self,data=None,parent = None, *args) :
      super(AlarmModel,self).__init__(parent,*args) 
      
      self.data = data or []
      self.dataChanged.connect(self.loadModel)
   
   def update(self) :
      print("UPDATE")
      
   def data(self,index,role) :
      
      row = index.row()
      col = index.column()
      
      if role == Qt.DisplayRole :
         alarm = self.data[row]
         if (col == 0) :
            return(alarm)
         
   
   def loadModel(self,alarm) :
      print("LoADING:",alarm.GetName())         
      self.data.append(alarm)
   
   
   def rowCount(self,index) :
      return(len(self.data))
   
   def columnCount(self,index) :      
      return(5)
   
   def headerData(self,section,orientation,role) :
      if (role != Qt.DisplayRole) :
         return
      if (orientation != Qt.Horizontal) :
         return
      
      
      if (section == 0) :
         return("Status")
      if (section == 1) :
         return("Name")
      if (section == 2) :
         return("TimeStamp")
      if (section == 3) :
         return("Category")
      if (section == 4) :
         return("Area")



#Only one widget for a main window
class MainWindow(QtWidgets.QMainWindow) :
   def __init__(self,*args,**kwargs) :
      super(MainWindow,self).__init__(*args,**kwargs)
      self.setWindowTitle("JAWS")
            
      #Table holding the model
      alarmpane = QtWidgets.QTableView()
      
      #Adjusts columns to contents
      alarmpane.setSizeAdjustPolicy(
        QtWidgets.QAbstractScrollArea.AdjustToContents)
      
      #Expands table if more rows added.
      alarmpane.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding |
         QtWidgets.QSizePolicy.ShrinkFlag, 
         QtWidgets.QSizePolicy.MinimumExpanding)
      
      self.alarmpane = alarmpane
      
      self.counter = 0
      self.data = []
            
      self.alarmmodel = AlarmModel(self.data)
      #SetMain(self)
      alarmpane.setModel(self.alarmmodel)
      
      self.setCentralWidget(alarmpane)
      self.show()
      
      self.threadpool = QThreadPool()
      QtWidgets.QShortcut("Ctrl+C", self, 
         activated=self.closeEvent)
      
      self.timer = QTimer()
      self.timer.setInterval(1000)
      self.timer.timeout.connect(self.recurring_timer)
      self.timer.start()
      
      self.monitor = AlarmMonitor()
      self.start_worker()
   
   def closeEvent(self,event) :
      print("CLOSING")
      self.stop_worker()
      sys.exit(0)
   
   def stop_worker(self) :
      print("STOPPING!")
      self.worker.running = False
   
   def start_worker(self) :
      
      self.worker = Worker(self.monitor)
      self.threadpool.start(self.worker)
      
      
   def add(self,alarm) :
      
      self.alarmmodel.data.append(alarm)
      
     
      #Updates the data in the table
      self.alarmmodel.layoutChanged.emit()
   
   #Updating the GUI
   def recurring_timer(self) :
      
      self.counter +=1
      
      if (self.counter == 5) :
         self.alarmmodel.data.remove(2)
      elif (self.counter == 10) :
         self.alarmmodel.data = []
         self.counter = 0
      else :   
         self.add(self.counter)
      

app = QtWidgets.QApplication([])
window = MainWindow()
app.exec_()
     