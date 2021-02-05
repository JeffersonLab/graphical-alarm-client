
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool

from AlarmProcessor import *
from AlarmThread import *
from AlarmModelView import *
from utils import *


class MyProxyModel(QtCore.QSortFilterProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(MyProxyModel,self).__init__(*args,**kwargs)
      
#Only one widget for a main window
class MainWindow(QtWidgets.QMainWindow) :
   def __init__(self,*args,**kwargs) :
      super(MainWindow,self).__init__(*args,**kwargs)
      
      self.data = [] 
      
      self.setWindowTitle("JAWS")
      
      ###
      #self.proxymodel = QtCore.QSortFilterProxyModel()
      #Create the alarmmodel that will be displayed in the table
      self.alarmmodel = AlarmModel(self.data)

      self.proxymodel = MyProxyModel()
      self.proxymodel.setDynamicSortFilter(True)
      self.proxymodel.setSourceModel(self.alarmmodel)
      self.proxymodel.setFilterKeyColumn(2)
      
      #Create the TableView widget that will display the alarm model
      self.alarmtable = AlarmTable()
      self.alarmtable.sortByColumn(2,1)   
      
      #Assign the model to the table
      self.alarmtable.setModel(self.proxymodel)
      self.alarmtable.setSortingEnabled(True)
            
      
      #Put the table in the main widget's layout.
      #Need to have a layout for its size hint.
      layout = QtWidgets.QHBoxLayout()
      layout.addWidget(self.alarmtable,0,Qt.AlignHCenter)
      self.layout = layout
      
      #The actual widget. 
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
            
      #Capture ctrl-c for quitting.
      QtWidgets.QShortcut("Ctrl+C", self, activated=self.closeEvent)

      #Make the main window and the model available      
      SetMain(self)
      SetModel(self.alarmmodel)
      
      #Record the orignal width of the GUI. We'll expand it if
      #a column needs to expand
      self.minwidth = self.layout.sizeHint().width()
      
      
      #Show the results
      self.setCentralWidget(widget)
      self.show()
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
   
   #We have to set the height explicitly, if we want the GUI
   #to shrink back if alarms are removed.  
   def resize(self,bigger=True) :
      if (bigger) :
         #This will resize the columns if necessry
         self.getTable().resizeColumnToContents(2)
      
      
      #What height does the layout (of the MainWindow) need?
      heighthint = self.layout.sizeHint().height()
      
      #If we're adding an alarm, make it bigger.
      #need to add the offset to account for margins
      if (bigger) :        
         self.setFixedHeight(heighthint + 35)
      else :
         #An alarm is removed, reduce the MainGui
         self.setFixedHeight(heighthint - 30)
         
   #Access the AlarmTable
   def getTable(self) :
      return(self.alarmtable) 
    
      
app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
#window.show()
app.exec()
