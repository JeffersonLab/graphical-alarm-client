import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRunnable,QThreadPool, \
   QTimer
from PyQt5.QtGui import QIcon, QPixmap

import time 
import traceback

from AlarmProcessor import *
from utils import *

ValueRole = QtCore.Qt.UserRole + 1
#Signals available from running worker
class WorkerSignals(QObject) :
   output = pyqtSignal(object)
      
#worker thread (generic)    
class Worker(QRunnable) :
   def __init__(self,fn,*args,**kwargs) :
      super(Worker,self).__init__()
      
      #fn is the function in the GUI to call from the thread
      #In this case it is AlarmProcessor.GetAlarms()
      self.fn = fn
      
      #Possible arguments
      self.args = args
      self.kwargs = kwargs
      self.running = True
      
      #Worker will emit a signal upon return from GUI call
      self.signals = WorkerSignals()
   
   #The thread continues to run as long as the application is 
   #up. When user wants to quit, self.running is set to False 
   def run(self) :      
      while (self.running) :
         try :
            #Call the proscribed function
            result = self.fn(*self.args,**self.kwargs)
         except :
            traceback.print_exc()
         else :
            #emit the result. The GUI will pick up the result to process
            self.signals.output.emit(result)
         
         #Wait, and do it again
         time.sleep(0.5)
   
   #Stop the thread   
   def stop(self) :
      self.running = False

class AlarmTable(QtWidgets.QTableWidget) :
   def __init__(self,data,*args) :
      super(AlarmTable,self).__init__(*args)
      
      self.data = data
      self.setData()
   
   def setData(self) :
      headers = ['Ack','Status','Name','Timestamp','Category','Area']
      self.setHorizontalHeaderLabels(headers)
      
        
#Only one widget for a main window
class MainWindow(QtWidgets.QMainWindow) :
   def __init__(self,*args,**kwargs) :
      super(MainWindow,self).__init__(*args,**kwargs)
      
      self.data = [] 
      
      self.setWindowTitle("JAWS")
     
      #Create the TableView widget that will display the alarm model
      self.alarmtable = AlarmTable(self.data)
      
      #Create the alarmmodel that will be displayed in the table
      #self.alarmmodel = AlarmModel(self.data)
      #Assign the model to the table
     # self.alarmtable.setModel(self.alarmmodel)
      
      #Put the table in the main widget's layout
      layout = QtWidgets.QHBoxLayout()
      layout.addWidget(self.alarmtable,0,Qt.AlignHCenter)
      
      #The actual widget. 
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
   
      #Capture ctrl-c for quitting.
      QtWidgets.QShortcut("Ctrl+C", self, activated=self.closeEvent)

      #Make the main window and the model available      
      SetMain(self)
      #SetModel(self.alarmmodel)
      

      self.rowheight = 30
      
      #Show the results
      self.setCentralWidget(widget)
      self.show()
      return
      #Set up the threading
      self.processor = AlarmProcessor()
      self.threadpool = QThreadPool()
      
      self.startWorker()
   
   #Create and start the worker.
   def startWorker(self) :
      #The function that the worker will call
      self.worker = Worker(self.processor.GetAlarms) 
      
      #Connect to the worker's emit signal, and call the GUI to 
      #process the alarms
      self.worker.signals.output.connect(self.ProcessAlarms)
      self.threadpool.start(self.worker)
   
   #Process the alarms.
   #This must be done from the MainWindow thread because the GUI
   #will be updated.
   def ProcessAlarms(self,msg) :
     if (msg != None and not msg.error()) :        
         self.processor.ProcessAlarms(msg)
   
   #Stop the worker from running. 
   def stopWorker(self) :
      self.worker.stop()
   
   #Close the GUI gracefully
   def closeEvent(self,event) :
      self.stopWorker()
      sys.exit(0)
   
   def resizeWidth(self) :
      nowwidth = self.getWidth()
      #Make the main gui bigger or smaller as necessary. 
      if (nowwidth > self.origwidth) :
         self.setFixedWidth(nowwidth)
      elif (nowwidth < self.origwidth) :
         self.setFixedWidth(self.origwidth)
   
   def resizeHeight(self) :
      
      min = 30*2

      #self.setFixedHeight(30 + self.origheight)
      
      nowheight = self.height()
      
      print("WINDOW:",self.height())
      
      
      tableheight = self.getHeight()
      numrows = GetModel().rowCount(0)
      if (numrows == 1) :
         newheight = 100
      self.setFixedHeight(newheight)
      
      
      print("TABLE",nowheight,"WITH",str(numrows))
      
      newheight = (numrows * 30) 
      if (newheight < self.height()) :
         newheight = min
      

      #self.setFixedHeight(newheight)
      print("NEWHEIGHT:",newheight)
      #if (newheight > min and newheight < self.getHeight()) :
       #  self.setFixedHeight(newheight)
      
      return
         
   #The table has resized for new data. Does the MainWindow
   #need to be expanded, or shrunk?  
   def resizeWindow(self) :
      
      #Resize the table itself 
      self.getTable().resizeColumnsToContents()
      #self.getTable().resizeRowsToContents()
      
      #self.getTable().resizeRowsToContents()
      self.resizeWidth()
      #self.resizeHeight()
     
      
      
   #Add up the columns of the table to determine what width to set
   #the Main Window
   def getWidth(self) :
      width = 0
      for i in range(GetModel().columnCount(0)) :
         colwidth = self.getTable().columnWidth(i)
         width = width + colwidth
      return(width + 20)
   
   def getHeight(self) :
      height = 0
      for i in range(GetModel().rowCount(0)) :
         rowheight = self.getTable().rowHeight(i)
         height = height + rowheight
      return(height)
      
   #Access the AlarmTable
   def getTable(self) :
      return(self.alarmtable) 
    

         
      
app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
#window.show()
app.exec()

         
         
      
