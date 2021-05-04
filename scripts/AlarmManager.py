from JAWSManager import *
from AlarmProcessor import *
from utils import *

#NOTE ABOUT METHOD AND VARIABLE NAMES
# --- self.myvariable     -- variable for this application
# --- def MyMethod()      -- method implemented for this application
# --- def libraryMethod() -- method accessed from a python library


#Entry point for the ActiveAlarm Manager
COLUMNS = {
     'type' :  {'size' : 75, 'filter' : TypeFilter,'settings' : None},
     'priority' : {'size' : 55, 'filter' : PriorityFilter,'settings' : None},
     'status' : {'size': 75, 'filter' : StatusFilter,'settings' : None},
     'name' : {'size' : 200},
     'timestamp': {'size': 150, 'settings' : None, 'sortorder': 1},  
     'location' : {'filter' : LocationFilter,'settings' : None},
     'category' : {'filter' : CategoryFilter, 'settings' : None}
}

#Alarm Manager inherits from JAWSManager. 
#It is the entry point to view the active alarms.
class AlarmManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      
      self.columns = COLUMNS
      self.name = "alarmmanager"  
      
      super(AlarmManager,self).__init__("JAWS - Active Alarm Manager","alarm",
         *args,**kwargs)
      
      if (len(self.filters) == 0) :
         self.MakeFilters()
   
  
   #The AlarmManager toolbar
   def ToolBar(self) :
      toolbar = AlarmToolBar(self)
      return(toolbar)
   
   #The AlarmManager menubar
   def MenuBar(self) :
      menubar = AlarmMenuBar(self)
      return(menubar)
 
   #The Alarm Table
   def TableView(self) :
      tableview = AlarmTable()      
      return(tableview)
   
   #The Alarm Model
   def ModelView(self) :
      modelview = AlarmModel(self.data)      
      return(modelview)

   #AlarmProcessor inherits from Processor
   def StartProcessor(self) :
      self.processor = AlarmProcessor()
   
   #Create a property dialog for an active alarm  
   def PropertyDialog(self,alarm) :
      propertydialog = AlarmPropertyDialog(alarm,self)
      return(propertydialog)
   
   #The Alarm/Shelf Preference Dialogs have different spacing and sizeHint 
   #variables.
   def PrefSpacing(self) :
      return(2)
   
   def PrefMultiplier(self) :
      return(30)
      

#The AlarmManager specific toolbar. 
#Slightly different from the ShelfManager
class AlarmToolBar(ToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(AlarmToolBar,self).__init__(parent,*args,**kwargs)
   
   #Create the toolbar actions
   def AddActions(self) :
      super().AddActions()
      
      ackaction = AckAction(self).AddAction()
      self.actionlist.append(ackaction)
      
     
      #Add access to shelving to the AlarmManager toolbar
      shelfaction = ShelfAction(self).AddAction()
      self.actionlist.append(shelfaction)
      
   
#AlarmManager specific menubar
#Slightly different from ShelfManager  
class AlarmMenuBar(QtWidgets.QMenuBar) :
   def __init__(self,parent,*args,**kwargs) :
      
      super(AlarmMenuBar,self).__init__(parent,*args,**kwargs)          
      
      filemenu = self.addMenu("File")
      
      prefsaction = PrefAction(self)
      filemenu.addAction(prefsaction)
      
      shelfaction = QAction("Launch Shelf Manager",self)
      shelfaction.triggered.connect(self.LaunchShelfManager)
      filemenu.addAction(shelfaction)
      
      exitaction = QAction("Quit",self)
      exitaction.triggered.connect(parent.closeEvent)
      filemenu.addAction(exitaction)
   
   #User can launch an instance of the ShelfManager
   def LaunchShelfManager(self,event) :
      command = "python3 " + SOURCEDIR + "ShelfManager.py &"
      os.system(command)
      

app = QtWidgets.QApplication(sys.argv)
window = AlarmManager()

app.exec()
