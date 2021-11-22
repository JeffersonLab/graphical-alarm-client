"""
.. module:: OverrideManager
   :synopsis : JAWSManager that displays Overridden Alarms
.. moduleauthor:: Michele Joyce <erb@jlab.org>
"""
from signal import signal, SIGINT
from sys import exit

from JAWSManager import *
from jlab_jaws_helper.JAWSProcessor import *

from OverrideProcessor import *
from JAWSTableView import *

import time

"""
Column definitions for an OverrideManager
"""
COLUMNS = {
     'priority' : {'size' : 175, 'filter' : PriorityFilter,'settings' : None},
     'status' : {'size': 75, 'filter' : StatusFilter,'settings' : None},
     'name' : {'size' : 200},
     'override_date': {'size': 150, 'label' : "Override Date"},  
     'location' : {'filter' : LocationFilter,'settings' : None},
     'category' : {'filter' : CategoryFilter, 'settings' : None},
     'time_left' : {},
     'expiration' : {},
     'override_type' : {'filter' : OverrideTypeFilter},
     'reason' : {'filter' : OverrideReasonFilter},
     'comments' : {},
     'overridden_by': {'filter' : UserFilter},
     'trigger' : {}
     
}


class OverrideManager(JAWSManager) :
   """ A JAWSManager to display overridden alarms
   """
   def __init__(self,*args,**kwargs) :
         
      self.columns = COLUMNS
      self.name = "overridemanager"  
      
      #OverrideManager will keep a countdown thread for each relevant alarm.
      self.threadlist = []
      self.workers = {}
            
      super(OverrideManager,self).__init__("JAWS - Overridden Alarm Manager",self.name,
         *args,**kwargs)
      
      self.stylecolor = 'darkBlue'
      #Apply filters if presetn
      if (len(self.filters) == 0) :
         self.makeFilters()
     
   def createToolBar(self) :
      """ OverrideManager toolbar
      """
      toolbar = OverrideToolBar(self)
      return(toolbar)
   
   def createMenuBar(self) :
      """ OverrideManager menubar
      """
      menubar = OverrideMenuBar(self)
      return(menubar)
  
   def createTableView(self) :
      """ Display table
      """
      tableview = OverrideTable()      
      return(tableview)
   
   def createModelView(self) :
      """ Alarm model
      """
      modelview = OverrideModel(self.data)      
      return(modelview)
   
   def createProxyModel(self) :
      """ Proxy Model 
      """
      proxymodel = OverrideProxy()     
      return(proxymodel)

   #AlarmProcessor inherits from Processor
   def createProcessor(self) :
      """ Monitors applicable topics and processes them
      """
      processor = OverrideProcessor()
      return(processor)
   
   def createPropertyDialog(self,alarm) :
      """ Create a property dialog for an active alarm  
          :param alarm: alarm to display
          :type alarm : JAWSALARM
      """
      
      name = alarm.get_name()
      if (name in self.propdialogs) :
         propertydialog = self.propdialogs[name]
      else :
         
         propertydialog = AlarmPropertyDialog(alarm,self)
         self.propdialogs[name] = propertydialog
         
      return(propertydialog)
   
   #The Alarm/Shelf Preference Dialogs have different spacing and sizeHint 
   #variables.
   #PROBABLY SHOULD BE KEPT WITH PREF DIALOG...
   def prefSpacing(self) :
      return(2)
   def prefMultiplier(self) :
      return(30)
        
   
   def updateAlarms(self,msg) :      
      """ Called by the topic thread when a message comes in
            Args:
               msg: 'cimpl.Message'
      """
      
      #Have to have thread action and GUI updates completely separate.
      #Create/Process the alarm 
      alarm = self.processor.process_alarm(msg)
      
      #Now, update the Manager
      if (alarm != None) :
         state = alarm.get_state(name=True)
         
         #Determine what to do based on the state of the alarm.
         if (state != None and not isinstance(state,dict)) :
            state = state.lower()
            
            #If Active or Normal, alarm has not been overriden...don't show
            if (state == "active" or state == "normal") :                          
               getModel().removeAlarm(alarm)
            
            #Add the alarm with the following states. 
            #This includes override states that are "Normal"
            elif ("disabled" in state) :             
               getModel().addAlarm(alarm)
            elif ("filtered" in state) :
               getModel().addAlarm(alarm)
            elif("masked" in state) :
               getModel().addAlarm(alarm)
            
            elif("shelved" in state) :
               #Shelved can be "oneshot" or "continuous"
               getModel().addAlarm(alarm)
               
               #A continuous shelved alarm has a countdown thread associated 
               #with it. A one shot does not.
               #Just in case there is an existing worker
               self.killWorker(alarm)
               if (alarm.get_property('oneshot') != None and not
                  alarm.get_property('oneshot')) :
                     self.startCountDown(alarm)               
            else :
               getModel().removeAlarm(alarm)
         else :
            getModel().removeAlarm(alarm)
   
   
   def startCountDown(self,alarm) :
      """ Start a countdown timer for the alarm
          Args:
            alarm: The alarm of interest
      """
      #Create a thread for the alarm
      #The thread, will call the alarm's "calc_time_left procedure
      thread = QThreadPool()
      worker = Worker(alarm.calc_time_left,0.5)
      
      #Save the thread to stop it if necessary
      if (not alarm in self.workers) :
         self.workers[alarm] = worker
         
      worker.signals.output.connect(self.countDown)
      thread.start(worker)
   
      #Add the thread and worker to the list if not
      #there already
      if (not thread in self.threadlist) :
         self.threadlist.append(thread)
         
  
   def countDown(self,alarm) :
      """ Called by the thread when the alarm's "timeleft" property is updated
          Args:
            alarm : the alarm of interest
      """
               
      timeleft = alarm.get_property('timeleft')
      #emit a signal to the model, to let it know that the timeleft field
      #has changed, and needs to redraw
      if (timeleft != None) :
         row = getModel().data.index(alarm)
         col = getModel().getColumnIndex("time_left")
         modelindex = getModel().createIndex(row,col)     
         getModel().dataChanged.emit(modelindex,modelindex,[Qt.DisplayRole])
      else :
         self.killWorker(alarm)
      
   def killWorker(self,alarm) :
      """ Worker thread is complete. Clean up
          Args:
            alarm : The alarm of interest
      """
      if (alarm in self.workers) :     
         self.workers[alarm].Stop() #Stop the worker, and remove from list.
         self.workers.pop(alarm)
   
   #Close the GUI gracefully (MainWindow function) 
   #closeEvent != CloseEvent
   def closeEvent(self, event=QtGui.QCloseEvent()) :
      
      try :
         workers = list(self.workers)[:]
         for alarm in workers :
            self.killWorker(alarm)  
      except Exception as e:
       
         pass
      super().closeEvent(event)
 
#The OverrideManager specific toolbar. 
#Slightly different from the OverrideManager
class OverrideToolBar(ToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(OverrideToolBar,self).__init__(parent,*args,**kwargs)
      self.setStyleSheet('QToolBar{border: 2px solid darkBlue;}')
  
  #    background-color: black;
   #Create the toolbar actions
   def addActions(self) :
      super().addActions()
      
      #ackaction = AckAction(self).addAction()
      #self.actionlist.append(ackaction)
      
     
      #Add access to overrides to the OverrideManager toolbar
  #    overrideaction = OverrideAction(self).addAction()
   #   self.actionlist.append(overrideaction)
      
      
   
class OverrideMenuBar(QtWidgets.QMenuBar) :
   """ Menubar specific to the OverrideManager
   """
   def __init__(self,parent,*args,**kwargs) :
      """ Create the menu bar
      """
      super(OverrideMenuBar,self).__init__(parent,*args,**kwargs)                
      
      filemenu = self.addMenu("File")
  #    filemenu.setStyleSheet('QMenu:QMenuItem{background-color: blue;}')
      prefsaction = PrefAction(self)
      filemenu.addAction(prefsaction)
      
     # overrideaction = QAction("Launch Override Manager",self)
     # overrideaction.triggered.connect(self.LaunchShelfManager)
     # filemenu.addAction(shelfaction)
      
      exitaction = QAction("Quit",self)
      exitaction.triggered.connect(parent.closeEvent)
      filemenu.addAction(exitaction)
      
      self.setStyleSheet('QMenuBar{background-color: black; color: white}')
 
   def LaunchShelfManager(self,event) :
      """ User can launch an instance of the ShelfManager
      """
      command = "python3 " + SOURCEDIR + "ShelfManager.py &"
      os.system(command)
 
      
def handler(signal_received,frame) :
   print("FRAME:",frame)
   print('SIGINT or CTRL-C detected.Exiting gracefully')
   

   
app = QtWidgets.QApplication(sys.argv)
#app.setStyleSheet('QMainWindow{background-color: black;border: 1px solid black;}')
app.setStyleSheet('QMainWindow{border: 5px solid darkBlue;}')
window = OverrideManager()
app.exec()
