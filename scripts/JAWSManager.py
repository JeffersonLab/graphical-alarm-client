
import sys
import argparse

from PyQt5 import QtCore, QtGui, QtWidgets

from AlarmThread import *
from ModelView import *
from Filters import *
from ShelvingDialog import *
from PrefDialog import *

from utils import *

#Parent toolbar. There are common actions for children.
#Specific actions are added by them
class ToolBar(QtWidgets.QToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(ToolBar,self).__init__(*args,**kwargs)
      
      self.parent = parent      
      self.actionlist = []
      self.AddActions()
   
   #Add the common actions   
   def AddActions(self) :
      prefaction = PrefAction(self)
      self.addAction(prefaction)

      propaction = PropertyAction(self)
      self.addAction(propaction)
      self.actionlist.append(propaction)
      
      filteraction = FilterAction(self)
      self.addAction(filteraction)
      
      
   #Configure the tool bar when necessary
   def ConfigToolBar(self) :
      for action in self.actionlist :               
         action.ConfigToolBarAction()
      

#Only one widget for a main window
class JAWSManager(QtWidgets.QMainWindow) :
   def __init__(self,title,type,*args,**kwargs) :
      super(JAWSManager,self).__init__(*args,**kwargs)
      
      self.data = [] 
      self.type = type
      self.filterDialog = None   
      self.shelfDialog = None  
      self.prefDialog = None
      
      self.setWindowTitle(title)
      
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
      #Have to connect AFTER model has been set in the tableview
      self.tableview.selectionModel().selectionChanged.connect(
         RowSelected)
    
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
      self.widget = widget
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
      self.toolbar.ConfigToolBar()         
      self.threadpool = QThreadPool()         
      self.StartWorker()
      
      
   #Close the GUI gracefully (MainWindow function) 
   #closeEvent != CloseEvent
   def closeEvent(self, event=QtGui.QCloseEvent()) :
      self.StopWorker()
      sys.exit(0)

   #use the same proxymodel class
   def ProxyModel(self) :
      proxymodel = ProxyModel()     
      return(proxymodel)
   
   #Access to tableview
   def GetTable(self) :
      return(self.tableview)
        
   #Create and start the worker.
   def StartWorker(self) :
      
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
   def StopWorker(self) :
      self.worker.stop()
   
   def PrefDialog(self) :
      prefdialog = PrefDialog()
      return(prefdialog)
      
   #Create a dialog for shelving an alarm. Common to children
   def ShelfDialog(self) :
      shelfdialog = ShelfDialog()
      return(shelfdialog)   

   #Adjust the size of the main gui when alarms are added/removed
   def SetSize(self) :
      self.widget.adjustSize()
      self.adjustSize() 
