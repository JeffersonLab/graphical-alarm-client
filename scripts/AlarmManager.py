"""
.. module:: AlarmManager
   :synopsis : JAWSManager that displays active alarms
.. moduleauthor:: Michele Joyce <erb@jlab.org>
"""
from signal import signal, SIGINT
from sys import exit

import pytz
import time


from JAWSManager import *
from jlab_jaws_helper.JAWSProcessor import *

from AlarmSearch import *
from AlarmProcessor import *
from AlarmModel import *
from JAWSTableView import *

from utils import *
"""
Column definitions for an AlarmManager
"""
COLUMNS = {
     'type' :  {'size' : 75, 'filter' : TypeFilter,'settings' : None,'empty':True},
     'priority' : {'size' : 175, 'filter' : PriorityFilter,'settings' : None,'empty':True},
     'status' : {'size': 75, 'filter' : StatusFilter,'settings' : None},
     'name' : {'size' : 200 ,'settings' : None,'headeronly': True,'searchable' : True,
               'filter' : NameFilter},
      'timestamp': {'size': 150, 'filter': RelativeTimeFilter,'settings' : None,
         'sortorder': 1},  
     'location' : {'filter' : LocationFilter,'settings' : None,'empty':True},
     'category' : {'filter' : CategoryFilter, 'settings' : None,'empty':True},
     'trigger' : {'headeronly': True,'searchable': True,'filter':TriggerFilter}
}

class AlarmManager(JAWSManager) :
   """ A JAWSManager to display active alarms
   """
   def __init__(self,*args,**kwargs) :
               
      self.columns = COLUMNS
      self.name = "alarmmanager"  
      super(AlarmManager,self).__init__("JAWS - Active Alarm Manager",self.name,
         *args,**kwargs)
      
      self.stylecolor = 'darkRed'     
      self.makeFilters()
   
   def createToolBar(self) :
      """ AlarmManager toolbar
      """
      
      toolbar = AlarmToolBar(self)
      return(toolbar)
   
   def createMenuBar(self) :
      """ AlarmManager menubar
      """
      menubar = AlarmMenuBar(self)
      return(menubar)
 
   #The Alarm Table
   def createTableView(self) :
      """ Display table
      """
      tableview = AlarmTable()      
      return(tableview)
   
   #The Alarm Model
   def createModelView(self) :
      """ Alarm model
      """
      modelview = AlarmModel(self.data)      
      return(modelview)
   
   
   def createProxyModel(self) :
      """ Proxy Model 
      """
      proxymodel = AlarmProxy()     
      return(proxymodel)

   #AlarmProcessor inherits from Processor
   def createProcessor(self) :
      """ Monitors applicable topics and processes them
      """
      processor = AlarmProcessor()
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
   
   def updateAlarms(self,msg) :      
      """ Update the alarms when a new message comes in
          Args:
            msg: 'cimpl.Message'
      """
      #The processor configures the alarm, and the manager displays the
      #results. The GUI actions must be separate from the thread actions
      alarm = self.processor.process_alarm(msg)
       
      #Determine whether or not to display/remove the alarm.
      if (alarm != None) :
         state = alarm.get_state(name=True)       
         if (state != None and not isinstance(state,dict)) :
            state = state.lower()
            if (state == "active" or "latched" in state) :
               getModel().addAlarm(alarm)
            elif (re.search("normal",state) != None) :
               getModel().removeAlarm(alarm)
            elif (re.search("shelved",state) != None) :
               getModel().removeAlarm(alarm)
            else :               
               getModel().removeAlarm(alarm)
         else :
            getModel().removeAlarm(alarm)

   #The Alarm/Shelf Preference Dialogs have different spacing and sizeHint 
   #variables.
   #PROBABLY SHOULD BE KEPT WITH PREF DIALOG...
   def prefSpacing(self) :
      return(2)
   def prefMultiplier(self) :
      return(30)
        
   
#The AlarmManager specific toolbar. 
#Slightly different from the OverrideManager
class AlarmToolBar(ToolBar) :
   """ Create the tool bar associated with the AlarmManager
   """ 
   def __init__(self,parent,*args,**kwargs) :
      super(AlarmToolBar,self).__init__(parent,*args,**kwargs)
      self.setStyleSheet('QToolBar{border: 2px solid darkRed;}')
   
   #Create the toolbar actions
   def addActions(self) :
      
      super().addActions()
      
      ackaction = AckAction(self).addAction()
      self.actionlist.append(ackaction)
           
      #Add access to overrides to the AlarmManager toolbar
      overrideaction = OverrideAction(self).addAction()
      self.actionlist.append(overrideaction)
      
      #This spacer puts the seachwidget on the far right.
      spacer = QtWidgets.QWidget()
      spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
         QtWidgets.QSizePolicy.Expanding)      
      self.addWidget(spacer)
      
      searchwidget = AlarmSearchWidget()
      getManager().searchwidget = searchwidget  
      self.addWidget(searchwidget)

class AlarmSearchWidget(QtWidgets.QWidget) :
   def __init__(self,parent=None) :
      super(AlarmSearchWidget,self).__init__(parent)
      
      layout = QtWidgets.QHBoxLayout()
      layout.setContentsMargins(0,0,5,0)
      self.setLayout(layout) 
      
      label = QtWidgets.QLabel()
      pixmap = QtGui.QPixmap("magnifier-left.png")
      label.setPixmap(pixmap)
      layout.addWidget(label)
      
      self.searchbar = AlarmSearchBar()
      layout.addWidget(self.searchbar)

   
   def applySearchFilters(self,alarm) :
      return(self.searchbar.applySearchFilters(alarm))

      
class AlarmMenuBar(QtWidgets.QMenuBar) :
   """ Menubar specific to the AlarmManager
   """
   def __init__(self,parent,*args,**kwargs) :
      """ Create the menu bar
      """
      super(AlarmMenuBar,self).__init__(parent,*args,**kwargs)                
      
      filemenu = self.addMenu("File")
      prefsaction = PrefAction(self)
      filemenu.addAction(prefsaction)
      
      exitaction = QAction("Quit",self)
      exitaction.triggered.connect(parent.closeEvent)
      filemenu.addAction(exitaction)
      
      self.setStyleSheet('QMenuBar{background-color: black; color: white}')
 

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet('QMainWindow{border: 5px solid darkRed;}')
window = AlarmManager()
app.exec()
