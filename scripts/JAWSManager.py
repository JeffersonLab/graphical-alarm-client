
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

#from AlarmManager import *

from AlarmProcessor import *
from AlarmThread import *
from AlarmModelView import *
from AlarmFilters import *
from AlarmShelving import *
from utils import *

class MyProxyModel(QtCore.QSortFilterProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(MyProxyModel,self).__init__(*args,**kwargs)
      self.setDynamicSortFilter(True)


class ToolBar(QtWidgets.QToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(ToolBar,self).__init__(*args,**kwargs)
      
      self.parent = parent
      self.parent.filterDialog = None
            
      filteraction = FilterAction(self)
      self.addAction(filteraction)
   
   def showShelfConfig(self,state=None) :
     
      dialog = self.parent.shelfDialog
      if (dialog == None) :
         dialog = self.parent.ShelfDialog()
      
      dialog.show()
      dialog.activateWindow()
      dialog.raise_()
      
      dialog.Reset()
      
      self.parent.shelfDialog = dialog
      
   def showFilter(self,state) :
      dialog = self.parent.filterDialog
      
      if (dialog == None) :
        
         dialog = self.parent.FilterDialog()
      
      dialog.show()
      dialog.activateWindow()
      dialog.raise_();
      
      self.parent.filterDialog = dialog

#Only one widget for a main window
class JAWSManager(QtWidgets.QMainWindow) :
   def __init__(self,title,type,*args,**kwargs) :
      super(JAWSManager,self).__init__(*args,**kwargs)
      
      self.data = [] 
      self.type = type
      self.setWindowTitle(title)
      self.filterDialog = None   
      self.shelfDialog = None  
      self.toolbar = self.ToolBar()  
      self.addToolBar(self.toolbar)
      
      
      
      ###
      proxymodel = self.ProxyModel()      
      self.proxymodel = proxymodel
      
      #Create the TableView widget that will display the alarm model
      self.tableview = self.TableView()
      
      #Create the alarmmodel that will be displayed in the table
      self.modelview = self.ModelView()
      
      #Assign the model to the table
      self.tableview.setModel(proxymodel)
      self.tableview.setSortingEnabled(True)
      
      self.proxymodel.setSourceModel(self.modelview)
      self.proxymodel.setFilterKeyColumn(3)
      
      #Put the table in the main widget's layout.
      #Need to have a layout for its size hint.
      layout = QtWidgets.QGridLayout()
      
      menubar = self.MenuBar()
      layout.addWidget(menubar)
      
      layout.addWidget(self.tableview)
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
      SetModel(self.modelview)
      SetTable(self.tableview)
 
      #Show the results
      self.setCentralWidget(widget)
      self.show()
      
      
      #Set up the threading
      self.StartProcessor()      
      self.threadpool = QThreadPool()      
      self.startWorker()
   

   def GetTable(self) :
      return(self.tableview)
        
   #Create and start the worker.
   def startWorker(self) :
    
      #The function that the worker will call
      self.worker = Worker(self.processor.GetAlarms,0.5) 
      
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
   def closeEvent(self, event=QtGui.QCloseEvent()) :
      
      self.stopWorker()
      sys.exit(0)
   
   #Access the AlarmTable
   def getTable(self) :
      return(self.tableview) 
    

      
#app = QtWidgets.QApplication(sys.argv)
#window = AlarmManager()
#window = JAWSManager("HELLO","MAN")
#window.show()
#app.exec()
