from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtCore import Qt, QObject,QThreadPool
#from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog,QMenu

from JAWSManager import *
from OverrideProcessor import *
from utils import *

#The ShelfManager. Inherits from the JAWSManager.
     
#The ShelfManager main gui.
class ShelfManager(JAWSManager) :
   def __init__(self,*args,**kwargs) :
      
      #Keep track of the countdown threads and workers.
      self.threadlist = []
      self.workerlist = []
      
      #During initialization, we will queue the 
      #alarms that are already shelved. 
      #After initialization, they'll be displayed
      self.shelfqueue = []
      
      self.manager = "shelfmanager"
      super(ShelfManager,self).__init__("JAWS - Alarm Shelf","shelf",
         *args,**kwargs)
            
   #The following create the Shelf specific pieces
   
   #Table
   def TableView(self) :
      tableview = ShelfTable()
      tableview.sortByColumn(2,1)
      return(tableview)
   
   #Model
   def ModelView(self) :
      modelview = ShelfModel(self.data)       
      return(modelview)
   
   #Menubar
   def MenuBar(self) :
      menubar = ShelfMenuBar(self)
      return(menubar)
   
   #Toolbar
   def ToolBar(self) :
      toolbar = ShelfToolBar(self)
      return(toolbar)

   #FilterDialog
   def FilterDialog(self) :
      filterdialog = ShelfFilterDialog()
      return(filterdialog)
   

   #PropertyDialog
   def PropertyDialog(self,alarm) :
      propertydialog = ShelfPropertyDialog(alarm,self)
      return(propertydialog)
   
   def PrefSpacing(self) :
      return(5)
   
   def PrefMultiplier(self) :
      return(40)
      
      
   #Start the shelf processor
   def StartProcessor(self) :
      self.processor = ShelfProcessor()
      self.EmptyQueue()
    
   #Creates the expiration countdown thread 
   #NOTE: The ShelfManager has the normal Kafka client thread, 
   #but also creates a thread for each shelved alarm, to keep 
   #track of the countdown to expiration.  
   def StartCountDown(self,alarm) :      
      
      #Create a thread
      thread = QThreadPool()      
      
      #After the amount of time specified by the delay,
      #calculate the time left for the alarm.
      worker = Worker(alarm.CalcTimeLeft,alarm.delay)
      
      #When the time left changes, a signal is emitted.
      #The signal prompts a call to the CountDown subroutine
      #This needs to be in the main gui in order to update.
      worker.signals.output.connect(self.CountDown)
 
      #Assign the worker to the alarm.
      alarm.worker = worker
      thread.start(worker)
      
      #Add the thread and worker to the list if not
      #there already
      if (not thread in self.threadlist) :
         self.threadlist.append(thread)
      if (not worker in self.workerlist) :
         self.workerlist.append(worker)
  
   #Called whenever the alarm's "timeleft" property is updated.        
   def CountDown(self,alarm) :      
      
      #If the alarm is not in the model, no "timeleft"   
      if (not alarm in GetModel().data) :        
         timeleft = None
      else :         
         #Otherwise, get the alarm's timeleft value.
         timeleft = alarm.timeleft
      
      #emit a signal to the model, to let it know that the 
      #timeleft field has changed, and to redraw 
      if (timeleft != None) :
         #Get the row in which the alarm is displayed
         row = GetModel().data.index(alarm)
         col = GetModel().GetColumnIndex("time left")
         #"timeleft" is displayed in the first column
         index = GetModel().createIndex(row,col)
         #emit the signal
         GetModel().dataChanged.emit(index,index,[Qt.DisplayRole])
         
         
      else :
         print("TIMES UP")
         #If the timeleft is "none" .. stop the worker.
         worker = alarm.worker
         worker.stop()
         alarm.worker = None
   
   #Stop all workers (GUI exited) 
   def StopWorker(self) :     
      
      #Stop the individual timeleft workers and threads
      try :
         for worker in self.workerlist :           
            worker.stop()
         for thread in self.threadlist :
            thread.join()
      except :
         pass
      
      #Stop the parent's thread (ShelfProcessor)
      super().StopWorker()
   
   #The ShelfProcessor will add shelved alarms to the queue to
   #during initialization. When initialization is complete,
   #Shelved alarms will be displayed, and timeleft threads will
   #be created.
   def AddToQueue(self,alarm) :
      if (alarm.GetShelfExpiration() == None) :
         return
      if (not alarm in self.shelfqueue) :
         self.shelfqueue.append(alarm)  

   #Empty out the initialization queue
   def EmptyQueue(self) :
      
      for alarm in self.shelfqueue :
         if (alarm.counting or alarm.GetShelfExpiration() == None) :
            return
         worker = None
         alarm.counting = True
         self.StartCountDown(alarm)
               
#Create the menubar for the ShelfManager
class ShelfMenuBar(QtWidgets.QMenuBar) :
   def __init__(self,parent,*args,**kwargs) :
      
      super(ShelfMenuBar,self).__init__(parent,*args,**kwargs)          
      filemenu = self.addMenu("File")
      
      #Launch the AlarmManager
      shelfaction = QAction("Launch Active Alarm Manager",self)
      shelfaction.triggered.connect(self.LaunchAlarmManager)
      filemenu.addAction(shelfaction)
      
      exitaction = QAction("Quit",self)
      exitaction.triggered.connect(parent.closeEvent)
      filemenu.addAction(exitaction)
   
   #Launch the AlarmManager. 
   def LaunchAlarmManager(self,event) :
      command = "python3 " + SOURCEDIR + "AlarmManager.py &"
      os.system(command)

#Create the toolbar for the ShelfManager
class ShelfToolBar(ToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(ShelfToolBar,self).__init__(parent,*args,**kwargs)
   
   #Add actions specific to the ShelfManager.
   def AddActions(self) :
      #Add the actions common to all managers
      super().AddActions()

     
      unshelfaction = UnShelveAction(self)
      self.addAction(unshelfaction)
      self.actionlist.append(unshelfaction)
      
      shelfaction = ShelfAction(self)
      self.addAction(shelfaction)
      self.actionlist.append(shelfaction)
      

app = QtWidgets.QApplication(sys.argv)
window = ShelfManager()

app.exec()
