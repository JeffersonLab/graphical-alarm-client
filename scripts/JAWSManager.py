import os
import sys
import argparse

from PyQt5 import QtCore, QtGui, QtWidgets

from AlarmThread import *
from JAWSModel import *
from Filters import *
from PrefDialog import *
from OverrideDialog import *
from utils import *

#Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-test',help="Run in debug mode",action='store_true')
args = parser.parse_args()
print("*****",args.test)

setDebug(args.test)

      
#Parent toolbar. There are common actions for children.
#Specific actions are added by them
class ToolBar(QtWidgets.QToolBar) :
   def __init__(self,parent,*args,**kwargs) :
      super(ToolBar,self).__init__(*args,**kwargs)
      self.parent = parent      
      self.actionlist = []
      self.addActions()
   
   #Add the common actions   
   def addActions(self) :
      #Display user preferences
      prefaction = PrefAction(self).addAction()
      
      #Actions added to the actionlist are subject to configuration
      propaction = PropertyAction(self).addAction()
      self.actionlist.append(propaction)
      
      removefilter = RemoveFilterAction(self).addAction()
      self.removefilter = removefilter
      
   
   #Access to the Remove Filter action button
   def getRemoveFilterAction(self) :
      return(self.removefilter)
         
   #Configure the tool bar when necessary
   def configureToolBar(self) :
      for action in self.actionlist :               
         action.configToolBarAction()
      

#NOT IMPLEMENTED YET
class JAWSMessenger(QtWidgets.QWidget) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(JAWSMessenger,self).__init__(parent,*args,**kwargs)
      
      layout = QtWidgets.QHBoxLayout()
      self.timestamp = QtWidgets.QLabel()
      self.timestamp.setFixedWidth(10)
      layout.addWidget(self.timestamp) 
      
      self.message = QtWidgets.QLabel()
      layout.addWidget(self.message)
      
      self.setLayout(layout)
   
   def setMessage(self,timestamp,message) :
      self.timestamp.setText(timestamp)
      self.message.setText(message)   
      
      
#only one widget for a main window
class JAWSManager(QtWidgets.QMainWindow) :
   def __init__(self,title,managername,debug=False,*args,**kwargs) :
      super(JAWSManager,self).__init__(*args,**kwargs)
      
      
      setManager(self)
      self.searchwidget = None
      #Instantiate Manager members
      self.managername = managername  #Manager name
      self.debug = debug
      self.data = []    #alarm data
      self.filters = [] #available alarm filters
      self.searchindex = []
      
      self.stylecolor = None
      
      self.jaws_topics = {}
      self.consumer_dict = {}
      self.consumers = []
      self.overridedialog = None   #dialog displaying suppression options
      self.prefdialog = None    #dialog displaying preferences
      self.removefilter = None  #Removes all filters.Associated with the tool bar
      
      self.propdialogs = {}
      self.managerprefs = self.readPrefs() #Read user preferences.
      
      #Begin to configure the main window     
      self.setWindowTitle(title)
          
      #Create the pieces and parts of the modelview and tableview
      self.createModelAndTable()
            
      self.toolbar = self.createToolBar()  
      self.addToolBar(self.toolbar)
       
      #Put the table in the main widget's layout.
      #Need to have a layout for its size hint.
      layout = QtWidgets.QGridLayout()
      
      menubar = self.createMenuBar()
      layout.addWidget(menubar)      
      layout.addWidget(self.tableview)
      
    #  self.messenger = JAWSMessenger()      
     # layout.addWidget(self.messenger)
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
      
      #Show the results
      self.setCentralWidget(widget)
      self.show()
       
      #Initial configuration based on prefs and alarm
      #status
      self.initConfig()
      
      self.createClassTopic()
      
      self.createTopics()
      
      #Initialize
      
      self.processor = JAWSProcessor(self.jaws_topics)
      
      #Start the worker threads to monitor for messages
      self.startWorkers()
      
      #Initialize the size of the main gui
      self.setSize()
   
   def setMessage(self,timestamp,message) :
      self.messenger.setMessage(timestamp,message)
      
   def createTopics(self) :
      topicnames = self.topicnames
      
      for topicname in topicnames :
         jaws_topic = create_JAWS_topic(self.managername,topicname, 
            self.initMessages,self.updateMessages,True)
         
         self.jaws_topics[topicname] = jaws_topic
         
   def createClassTopic(self) :
      topicname = 'alarm-classes'
      jaws_topic = create_JAWS_topic(self.managername,topicname,
         self.initMessages,self.updateMessages,False)
      self.jaws_topics[topicname] = jaws_topic
      
      


   ### THE FOLLOWING METHODS DEAL WITH THREADING
   
   #Create and start the worker.
   def startWorkers(self) :
      
      #Create a thread for each topic
      jaws_topics = self.jaws_topics
      
      numtopics = len(jaws_topics)
      
      #return
      self.threadpool = QThreadPool()  
      self.threadpool.setMaxThreadCount(numtopics + 1)
      self.workerthreads = {}
      for topic in self.jaws_topics :
         jaws_topic = jaws_topics[topic]
         consumer = jaws_topic.get_consumer()
         worker = JAWSWorker(self.createConsumer,topic)
         
         self.workerthreads[topic] = worker
         worker.signals.progress.connect(self.updateAlarms)
        
         self.threadpool.start(worker)
         self.workerthreads[topic] = worker
         

   #Create a consumer for the topic  
   def createConsumer(self,topic) :
      """
         Create a consumer for the topic
         ARGS:
            topic : topic 
            monitor : True/False
         NOTE:
            When a consumer is created, pass it the initializ
      """
      jaws_topic = self.jaws_topics[topic]
      consumer = jaws_topic.get_consumer()
      self.consumer_dict[topic] = jaws_topic.get_consumer()
      
      self.consumers.append(consumer)
      consumer.start()
      
      
   #Initial messages (this is in the jawsconsumer thread)
   def initMessages(self,msglist) :      
      
      #Process each alarm 
      for msg in msglist.values() :        
         topic = get_msg_topic(msg)    
         worker = self.workerthreads[topic]
         worker.signals.progress.emit(msg)
         
   
   #Called when there is a new message (jaws consumer thread)
   def updateMessages(self,msg) :    
      topic = get_msg_topic(msg)      
      worker = self.workerthreads[topic]
      worker.signals.progress.emit(msg)
   
           
   
   #Close the GUI gracefully (MainWindow function) 
   #closeEvent != CloseEvent
   def closeEvent(self, event=QtGui.QCloseEvent()) :
      
      #Close down the consumers nicely
      if (self.consumers != None) :        
         for consumer in self.consumers :        
            consumer.stop()
      sys.exit(0)
   
   
   #Create the table, model, and proxymodel that will
   #display and organize the alarm data
   def createModelAndTable(self) :
   
      ##### Using a proxymodel allows us to easily sort and filter
      proxymodel = self.createProxyModel()      
      self.proxymodel = proxymodel
      
      #Create the TableView widget that will display model
      self.tableview = self.createTableView()
      
      #Create the alarmmodel that will be displayed in the table
      self.modelview = self.createModelView()
      
      #Assign the model to the table
      self.tableview.setModel(proxymodel)
      self.tableview.setSortingEnabled(True)  
       
      #Have to connect AFTER model has been set in the tableview
      #If a row is selected, the tool bar configuration may change
      self.tableview.selectionModel().selectionChanged.connect(
         self.tableview.rowSelected)
      
      self.proxymodel.setSourceModel(self.modelview)
      
      #Make the model and the table available      
      setModel(self.modelview)
      setTable(self.tableview)
      setProxy(self.proxymodel)
      
         
   def getProcessor(self) :
      return(self.processor)
      
   #Configure based on the initial set of messages
   def initConfig(self) :
      self.applyPrefs()
      self.configureColumns()
      self.configureToolBar()
   
   #Configure the column width.
   #Some columns have a width assigned  
   def configureColumns(self) :
      getModel().configureColumns()
    
   #Configure the tool bar.   
   def configureToolBar(self) :
      self.getToolBar().configureToolBar()
   
   def configureProperties(self,alarm) :
      if (alarm.get_name() in self.propdialogs) :
         dialog = self.propdialogs[alarm.get_name()]
         dialog.configureProperties()
   
   def configureOverrideDialog(self) :
      if (self.overridedialog != None) :
         self.overridedialog.reset()
    
   def getName(self) :
      return(self.name)     
   #Access to the Manager's toolbar  
   def getToolBar(self) :
      return(self.toolbar)
      
   #Access the RemoveFilter for configuration  
   def getRemoveFilterAction(self) :
      return(self.getToolBar().getRemoveFilterAction())
   
   #Access the manager's set of filters.      
   def getFilters(self) :      
      return(self.filters)
   
   def configureManager(self,alarm) :
      self.getToolBar().configureToolBar()
      self.configureProperties(alarm)
      self.setSize()
      
      if (self.overridedialog != None) :
         self.overridedialog.reset()

   def setGroupBoxStyle(self,groupbox) :
      
      if (self.stylecolor != None) :
         
         color = self.stylecolor
         style = "font-weight: bold; color: " + color +";"
         groupbox.setStyleSheet('QGroupBox{' + style + '}')
         

   def setDialogStyle(self,dialog) :
      dialog.setStyleSheet('QDialog{border: 5px solid black;}')   

   def setButtonStyle(self,button) :
      if (self.stylecolor != None) :
         color = self.stylecolor
         style = 'background-color: ' + color + "; color: white;"
         button.setStyleSheet('QPushButton{' + style +'}')

   ### The following deals with accessing and applying
   #   user preferences.
   
   #Access this manager's preference configuration   
   def getPrefs(self) :
      return(self.managerprefs)

   #Create the preference file name   
   def getPrefFile(self) :
      user = getUser()
      manager = self.name
      filename = "." + user + "-jaws-" + manager
      return(filename)
   
   #Read preference file.
   #Preferences contain initial configuration information 
   #such as hidden/shown table columns
   def readPrefs(self) :
      prefs = {}
      filename = self.getPrefFile()
      
      if (os.path.exists(filename)) :        
         #Preference file is written as a dictionary.
         #The "eval" turns the string back into a dictionary
         line = open(filename,'r').read()
         if (len(line) > 0) :
            prefs = eval(line)
      return(prefs)
   
   #Save the user preferences.
   def savePrefs(self) :
      filename = self.getPrefFile()
      if (os.path.exists(filename)) :
         os.remove(filename)
      #Write the preference dictionary to the file.
      prefs = self.managerprefs
      with open(filename,"a+") as file :
        file.write(str(prefs))
      file.close()
   
   def applySearchFilters(self,alarm) : 
      if (self.searchwidget == None) :
         return(True)
      return(self.searchwidget.applySearchFilters(alarm))
 
   #Apply preferences if applicable
   def applyPrefs(self) :
      prefs = self.getPrefs()
      
      if (prefs == None or len(prefs) == 0) :
         return
      
      if ("display" in prefs) :
         getModel().applyDisplayPrefs(prefs['display']['show'])
         
      if ("sort" in prefs) :
         sortcolumn = prefs['sort']['column']
         sortorder = prefs['sort']['order']

      else :
         if (getTable() == None) :
            print("NO TABLE")
            return
         else :
            (sortcolumn,sortorder) = getTable().getDefaultSort()
      
      getTable().sortByColumn(sortcolumn,sortorder)
   
   
   
   ### The following deal with the manager's filters.
   
   #Create the filters for the manager.
   def makeFilters(self) :
      
      #Not all columns have filters. 
      columns = self.columns
      for col in columns :          
         if ("searchable" in columns[col]) :
            continue
         if ("filter" in columns[col]) :
            
            filtertype = columns[col]['filter']  
            
            jawsfilter = filtertype(col,columns[col])  
            #if (col == "name") :
            self.filters.append(jawsfilter)
  
      self.initFilters()
      
 #     searchfilter = SearchFilter("search")
  #  self.filters.append(searchfilter)
  #    self.searchfilter = searchfilter
      
  
   #Handler initial filter values (from prefs file) a little 
   #differently
   def initFilters(self) :
      prefs = self.getPrefs()      
      if (not 'filters' in prefs) :
         prefs['filters'] = {}
      
      #if (prefs != None and "filters" in prefs) :
      for filter in self.filters :       
         name = filter.getName()
         filterstate = filter.getCurrentState()
         if (name in prefs['filters']) :
            filterstate = prefs['filters'][name]         
         filter.setState(filterstate)        
         filter.setHeader()
         
   #Create the preference dialog
   def createPrefDialog(self) :
      if (self.prefdialog == None) :
         self.prefdialog = PrefDialog()
      return(self.prefdialog)
   
   #Access the preference dialog
   def getPrefDialog(self) :
      return(self.prefdialog)
        
   #Create a dialog for overriding an alarm. Common to children
   def createOverrideDialog(self,selectedalarms=None) :
      
      if (self.overridedialog == None) :
         self.overridedialog = OverrideDialog(selectedalarms)
      self.overridedialog.setSelection(selectedalarms)
      return(self.overridedialog)   

   #Adjust the size of the main gui when alarms are added/removed
   def setSize(self) :
      self.widget.adjustSize()
      self.adjustSize() 
