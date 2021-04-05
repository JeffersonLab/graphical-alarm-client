
from JAWSManager import *
from AlarmProcessor import *
from utils import *

#Alarm Manager inherits from JAWSManager. 
#It is the entry point to view the active alarms.
class AlarmManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      super(AlarmManager,self).__init__("JAWS - Active Alarm Manager","alarm",
         *args,**kwargs)
           
      GetModel().ConfigureColumns()
      
      
   #The AlarmManager toolbar
   def ToolBar(self) :
      toolbar = AlarmToolBar(self)
      return(toolbar)
   
   #The AlarmManager menubar
   def MenuBar(self) :
      menubar = AlarmMenuBar(self)
      return(menubar)
 
   #Create the alarm table. Sort by the alarm timestamp
   def TableView(self) :
      tableview = AlarmTable()
      tableview.sortByColumn(3,1)
      return(tableview)
   
   #Create the alarm model
   def ModelView(self) :
      modelview = AlarmModel(self.data)      
      return(modelview)

   #AlarmProcessor inherits from Processor
   def StartProcessor(self) :
      self.processor = AlarmProcessor()
   
   #Create the AlarmFilterDialog. Accessed from the toolbar  
   def FilterDialog(self) :
      filterdialog = AlarmFilterDialog()
      return(filterdialog)
   
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
   
   def AddActions(self) :
      super().AddActions()
      ackaction = AckAction(self)
      self.addAction(ackaction)
      self.actionlist.append(ackaction)
      
      #Both Managers include a FilterDialog on their toolbar.
      #Add access to shelving to the AlarmManager toolbar
      shelfaction = ShelfAction(self)
      self.addAction(shelfaction)
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
