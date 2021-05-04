import os
import sys
import argparse

from PyQt5 import QtCore, QtGui, QtWidgets

from AlarmThread import *
from ModelView import *
from Filters import *
from ShelvingDialog import *
from PrefDialog import *

from utils import *

#NOTE ABOUT METHOD AND VARIABLE NAMES
# --- self.myvariable     -- variable for this application
# --- def MyMethod()      -- method implemented for this application
# --- def libraryMethod() -- method accessed from a python library

#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-test',help="Run in debug mode",action='store_true')
args = parser.parse_args()

SetTest(args.test)
      
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
      #Display user preferences
      prefaction = PrefAction(self).AddAction()
      
      #Actions added to the actionlist are subject to configuration
      propaction = PropertyAction(self).AddAction()
      self.actionlist.append(propaction)
      
      removefilter = RemoveFilterAction(self).AddAction()
      self.removefilter = removefilter
   
   #Access to the Remove Filter action button
   def GetRemoveFilterAction(self) :
      return(self.removefilter)
         
   #Configure the tool bar when necessary
   def Configure(self) :
      for action in self.actionlist :               
         action.ConfigToolBarAction()
      

#Only one widget for a main window
class JAWSManager(QtWidgets.QMainWindow) :
   def __init__(self,title,type,*args,**kwargs) :
      super(JAWSManager,self).__init__(*args,**kwargs)
      
      SetManager(self)
          
      #Instantiate Manager members
      self.type = type  #Manager type
      self.data = []    #alarm data
      self.filters = [] #available alarm filters
      
      self.shelfdialog = None   #dialog displaying suppression options
      self.prefdialog = None    #dialog displaying preferences
      self.removefilter = None  #Removes all filters.Associated with the tool bar
      
      self.managerprefs = self.ReadPrefs() #Read user preferences.
      
      #Begin to configure the main window     
      self.setWindowTitle(title)
      
      
      #Create the pieces and parts of the modelview and tableview
      self.CreateModelAndTable()
      
      self.toolbar = self.ToolBar()  
      self.addToolBar(self.toolbar)
       
      #Put the table in the main widget's layout.
      #Need to have a layout for its size hint.
      layout = QtWidgets.QGridLayout()
      
      menubar = self.MenuBar()
      layout.addWidget(menubar)      
      layout.addWidget(self.tableview)
     
      ############   NEEDS TO BE EXERCISED BEFORE REMOVAL 
      #Total misnomer. This command grows and shrinks the main window
      #when the table rows are added or removed. Also allows for the
      #size grip to still be used by the user.
      layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize);
         
      #The actual widget. 
      widget = QtWidgets.QWidget()
      widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
         QtWidgets.QSizePolicy.MinimumExpanding)
      widget.setLayout(layout)
      
      #We will use the widget later to resize the MainWindow
      self.widget = widget
      
      #Capture ctrl-c for quitting.
      QtWidgets.QShortcut("Ctrl+C", self, activated=self.closeEvent)
        
      #Show the results
      self.setCentralWidget(widget)
      self.show()
      
      #Initial configuration based on prefs and alarm
      #status
      self.InitConfig()
     
      #Initial processing of the Kafka messages
      self.StartProcessor()   
      self.SetSize()
      
      #Start the worker thread to monitor for messages
      self.StartWorker()
   
   #Create the table, model, and proxymodel that will
   #display and organize the alarm data
   def CreateModelAndTable(self) :
   
      ##### Using a proxymodel allows us to easily sort and filter
      proxymodel = self.ProxyModel()      
      self.proxymodel = proxymodel
      
      #Create the TableView widget that will display model
      self.tableview = self.TableView()
      
      #Create the alarmmodel that will be displayed in the table
      self.modelview = self.ModelView()
      
      #Assign the model to the table
      self.tableview.setModel(proxymodel)
      self.tableview.setSortingEnabled(True)  
       
      #Have to connect AFTER model has been set in the tableview
      #If a row is selected, the tool bar configuration may change
      self.tableview.selectionModel().selectionChanged.connect(
         RowSelected)
      
      self.proxymodel.setSourceModel(self.modelview)
      
      #Make the model and the table available      
      SetModel(self.modelview)
      SetTable(self.tableview)
      SetProxy(self.proxymodel)
   
   #Managers use the same proxymodel class
   def ProxyModel(self) :
      proxymodel = ProxyModel()     
      return(proxymodel)

   #Configure based on the initial set of messages
   def InitConfig(self) :
      self.ApplyPrefs()
      self.ConfigureColumns()
      self.ConfigureToolBar()
   
   #Configure the column width.
   #Some columns have a width assigned  
   def ConfigureColumns(self) :
      GetModel().ConfigureColumns()
    
   #Configure the tool bar.   
   def ConfigureToolBar(self) :
      self.GetToolBar().Configure()
   
   #Access to the Manager's toolbar  
   def GetToolBar(self) :
      return(self.toolbar)
      
   #Access the RemoveFilter for configuration  
   def GetRemoveFilterAction(self) :
      return(self.GetToolBar().GetRemoveFilterAction())
   
   #Access the manager's set of filters.      
   def GetFilters(self) :      
      return(self.filters)
   
   
   ### The following deals with accessing and applying
   #   user preferences.
   
   #Access this manager's preference configuration   
   def GetPrefs(self) :
      return(self.managerprefs)

   #Create the preference file name   
   def GetPrefFile(self) :
      user = GetUser()
      manager = self.name
      filename = "." + user + "-jaws-" + manager
      return(filename)
   
   #Read preference file.
   #Preferences contain initial configuration information 
   #such as hidden/shown table columns
   def ReadPrefs(self) :
      prefs = {}
      filename = self.GetPrefFile()
      
      if (os.path.exists(filename)) :        
         #Preference file is written as a dictionary.
         #The "eval" turns the string back into a dictionary
         line = open(filename,'r').read()
         if (len(line) > 0) :
            prefs = eval(line)
      return(prefs)
   
   #Save the user preferences.
   def SavePrefs(self) :
      filename = self.GetPrefFile()
      if (os.path.exists(filename)) :
         os.remove(filename)
      #Write the preference dictionary to the file.
      prefs = self.managerprefs
      with open(filename,"a+") as file :
        file.write(str(prefs))
      file.close()
   
   #Apply preferences if applicable
   def ApplyPrefs(self) :
      prefs = self.GetPrefs()
      if (prefs == None) :
         return
      
      if ("display" in prefs) :
         GetModel().ApplyChanges(prefs['display']['show'])
         
      if ("sort" in prefs) :
         sortcolumn = prefs['sort']['column']
         sortorder = prefs['sort']['order']
      else :
         (sortcolumn,sortorder) = GetTable().GetDefaultSort()
      GetTable().sortByColumn(sortcolumn,sortorder)
   
   ### The following deal with the manager's filters.
   
   #Create the filters for the manager.
   def MakeFilters(self) :
      #Not all columns have filters. 
      columns = self.columns
      for col in columns :          
         
         if ("filter" in columns[col]) :
            filtertype = columns[col]['filter']            
            filter = filtertype()
            
            self.filters.append(filter)
      
      self.InitFilters()
  
   #Handler initial filter values (from prefs file) a little 
   #differently
   def InitFilters(self) :
      
      prefs = self.GetPrefs()      
      if (not 'filters' in prefs) :
         prefs['filters'] = {}
         
      #if (prefs != None and "filters" in prefs) :
      for filter in self.filters :
         name = filter.GetName()
         settings = filter.GetCurrentSettings()
         if (name in prefs['filters']) :
            settings = prefs['filters'][name]
         
         filter.SetSettings(settings)               
         filter.SetHeader()
         

   #Close the GUI gracefully (MainWindow function) 
   #closeEvent != CloseEvent
   def closeEvent(self, event=QtGui.QCloseEvent()) :
      self.StopWorker()
      sys.exit(0)

        
   #Create and start the worker.
   def StartWorker(self) :
      self.threadpool = QThreadPool()         
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
      self.worker.Stop()
   
   #Create the preference dialog
   def PrefDialog(self) :
      prefdialog = PrefDialog()
      return(prefdialog)
   
   def GetPrefDialog(self) :
      return(self.prefdialog)
        
   #Create a dialog for shelving an alarm. Common to children
   def ShelfDialog(self) :
      shelfdialog = ShelfDialog()
      return(shelfdialog)   

   #Adjust the size of the main gui when alarms are added/removed
   def SetSize(self) :
      self.widget.adjustSize()
      self.adjustSize() 
