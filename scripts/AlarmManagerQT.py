
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

#from ShelfManager import *

from AlarmProcessor import *
from AlarmThread import *
from AlarmModelView import *
from AlarmFilters import *
from utils import *

class MyProxyModel(QtCore.QSortFilterProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(MyProxyModel,self).__init__(*args,**kwargs)
      self.setDynamicSortFilter(True)


class AlarmToolBar(QtWidgets.QToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(AlarmToolBar,self).__init__(*args,**kwargs)
      
      self.parent = parent
      self.parent.filterDialog = None
            
      filteraction = FilterAction(self)
      self.addAction(filteraction)
      
  #    shelveaction = ShelveAction(self)
   #   self.addAction(shelveaction)
   
   def showFilter(self,state) :
      dialog = self.parent.filterDialog
      if (dialog == None) :
         self.parent.filterDialog = FilterDialog(self)
      elif (dialog != None) :
         dialog.show()

#Only one widget for a main window
class MainWindow(QtWidgets.QMainWindow) :
   def __init__(self,*args,**kwargs) :
      super(MainWindow,self).__init__(*args,**kwargs)
      
      self.data = [] 
      
      self.setWindowTitle("JAWS")
      self.filterDialog = None
      self.toolbar = AlarmToolBar(self)
      self.addToolBar(self.toolbar)
      ###
      proxymodel = AlarmProxyModel()      
      self.proxymodel = proxymodel
      
      #Create the TableView widget that will display the alarm model
      self.alarmtable = AlarmTable()
      self.alarmtable.sortByColumn(3,1)   
      
      #Create the alarmmodel that will be displayed in the table
      self.alarmmodel = AlarmModel(self.data)
      
      #Assign the model to the table
      self.alarmtable.setModel(proxymodel)
      self.alarmtable.setSortingEnabled(True)
      
      self.proxymodel.setSourceModel(self.alarmmodel)
      self.proxymodel.setFilterKeyColumn(3)
      
      #Put the table in the main widget's layout.
      #Need to have a layout for its size hint.
      layout = QtWidgets.QGridLayout()
      layout.addWidget(self.alarmtable)
      self.layout = layout
      
      #Total misnomer. This command grows and shrinks the main window
      #when the table rows are added or removed. Also allows for the
      #size grip to still be used by the user.
      layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize);
         
      #The actual widget. 
      widget = QtWidgets.QWidget()
      widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
         QtWidgets.QSizePolicy.MinimumExpanding)
   
      widget.setLayout(layout)
            
      #Capture ctrl-c for quitting.
      QtWidgets.QShortcut("Ctrl+C", self, activated=self.closeEvent)

      #Make the main window and the model available      
      SetManager(self)
      SetModel(self.alarmmodel)
      
      self.alarmtable.setColumnWidth(2,200)
      self.alarmtable.setColumnWidth(3,150)

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
   
   #Access the AlarmTable
   def getTable(self) :
      return(self.alarmtable) 
    

      
app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
#window.show()
app.exec()
