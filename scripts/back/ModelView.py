#Contains the Alarm and Shelf Models

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

from utils import *

#Parent ModelView. AlarmModel and ShelfMmodel inherit         
class ModelView(QtCore.QAbstractTableModel) :
   
   def __init__(self,data=None,parent = None, *args) :
      super(ModelView,self).__init__(parent,*args) 
      self.data = data or []
      
      #Columns that are shared by the Alarm and Shelf managers
      self.columnconfig = {
                        'type' : 75,                    
                        'priority' : 55,
                        'name' : 200}
   
   #rowCount must be overloaded. 
   #Overload it here, since the same for all children 
   def rowCount(self,index) :
      return(len(self.data))
   
   #columnCount must be overloaded
   def columnCount(self,index) :      
      return(len(self.columns))

   def GetColumnIndex(self,property) :
     
      if (not property in self.columns) :
         index = None
      else :
         index = self.columns.index(property)
      return(index)
   
   def GetColWidth(self,property) :
      width = None
      if (property in self.columnconfig) :
         width = self.columnconfig[property]
      return(width)   

   def ConfigureColumns(self) :
      modelindex = self.GetColumnIndex
      
      for prop in self.columns :
         width = self.GetColWidth(prop)
         if (width != None) :
            GetTable().setColumnWidth(modelindex(prop),width)

   #Add alarm to the data. 
   def addAlarm(self,alarm) :
      #Remove the alarm from the data first.
      if (alarm in self.data) :
         self.data.remove(alarm)
      
      #Need to emit this signal so that the TableView will be ready
      self.layoutAboutToBeChanged.emit()    
      #add the alarm to to the model data.
      self.data.append(alarm)
      #Emit signal to the TableView to redraw
      self.layoutChanged.emit()
      
      #Apply filters if applicable
      filters = GetManager().filterDialog
      if (filters != None) :
         filters.applyFilters()
      
      GetManager().toolbar.ConfigToolBar()
      GetManager().SetSize()
      
         
   #Remove the alarm. 
   def removeAlarm(self,alarm) :
      
      #Double check that the alarm is in the dataset.
      if (alarm in self.data) :        
         #Warn the TableView
         self.layoutAboutToBeChanged.emit()
         #Actually remove the alarm
         self.data.remove(alarm)   
         #Emit signal to TableView to redraw
         self.layoutChanged.emit()
         
         #Apply filters.      
         filters = GetManager().filterDialog
         if (filters != None) :
            filters.applyFilters()
           
      GetManager().toolbar.ConfigToolBar()
      GetManager().SetSize()
     
   #Configure the header if the data is filtered      
   def setFilter(self,column,filtered=False) :
      #If the user filters the data from the FilterDialog..
      #indicate that on the column header by adding a little
      #filter icon to the columns that have been filtered.
      try :
         if (not filtered) :
            self.filtercols[column] = False
         else :
            self.filtercols[column] = True
         self.headerDataChanged.emit(Qt.Horizontal,column,column)
      except :
         pass
   
   #Display headers for the columns
   def headerData(self,section,orientation,role) :
      #sourcemodel = self.sourceModel()
      
      if (role != Qt.DisplayRole and role != Qt.DecorationRole) :
         return
      if (orientation != Qt.Horizontal) :
         return      
      
      try :
         #Try to add the filter image to the header to show it's filtered 
         if (role == Qt.DecorationRole and self.filtercols[section]) :
            return (QtGui.QPixmap("funnel--plus.png"))
         elif (role == Qt.DecorationRole) :
            return("") 
      except : 
         return("")
      
      if (role == Qt.DisplayRole) :
         return(self.columns[section].title())
      
      return(QtCore.QAbstractTableModel.headerData(self,section,orientation,role))


#The model used with the ShelfManager.
class ShelfModel(ModelView) :
   def __init__(self,data=None,parent=None,*args) :
      super(ShelfModel,self).__init__(data,parent,*args)
      
      self.columns = ['type','priority','time left','name','date shelved',
         'exp date', 'location', 'category','reason']
      
      
      self.columnconfig['date shelved'] = 150
      self.columnconfig['exp date'] = 150
      self.columnconfig['reason'] = 250


   #Overloaded function that must be defined.      
   def data(self,index,role) :
      #The index (contains both x,y) and role are passed.  
      #The roles give instructions about how to display the model.
      row = index.row()
      col = index.column()
            
      #Center columns
      if (role == Qt.TextAlignmentRole) : 
         return(Qt.AlignCenter)
         
      #Insert the appropriate information into the display, based
      #on the column. 
      if role == Qt.DisplayRole :
         alarm = self.data[row] 
         
         #This is the expiration countdown
         if (col == self.GetColumnIndex("time left")) :
            timedisplay = self.DisplayTimeLeft(alarm)
            return(timedisplay)

         if (col == self.GetColumnIndex("name")) :
            
            return(alarm.GetName())
         
         if (col == self.GetColumnIndex("date shelved")) :
            timestamp = alarm.GetShelfTime()
            if (timestamp != None) :
               return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         
         if (col == self.GetColumnIndex("exp date")) :
            timestamp = alarm.GetShelfExpiration()
            if (timestamp != None) :
               return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         
         if (col == self.GetColumnIndex("category")) :
            return(alarm.GetCategory())
         if (col == self.GetColumnIndex("location")) :
            return(alarm.GetLocation())  
         if (col == self.GetColumnIndex("reason")) :
            return(alarm.GetShelfReason())
   
   #Figure out a pretty way to display the time left until
   #expiration  
   def DisplayTimeLeft(self,alarm) :
      
      #How much time left? A disabled alarm will not have alarm.timeleft 
      #defined
      timeleft = alarm.timeleft
      
      if (timeleft ==  None) :
         return("")
         
      #timeleft is a "datetime.timedelta" object.
      #From this object, we can get the number of seconds and days.     
      seconds = timeleft.seconds
      days = timeleft.days
      
      #displaytime = str(seconds) + " s"
      displaytime = ""
      if (days > 0) :
         displaytime = str(days) + " days "
      
      if (seconds < 60) :
         displaytime = displaytime + str(seconds) + " sec"
          
      elif (seconds > 60 and seconds < 3600) :
         minutes = '{:0.2f}'.format(seconds / 60)
         displaytime = displaytime + minutes + " min"
      
      elif (seconds > 3600 and seconds < 86400) :
         if (days > 0) :
            hours = str(int(seconds/3600))
            GetManager().GetTable().horizontalHeader().setSectionResizeMode(3,
               QtWidgets.QHeaderView.ResizeToContents)
         else :
            hours = '{:0.2f}'.format(seconds / 3600)
         displaytime = displaytime + hours + " hours"
      
      return(displaytime)

       
#AlarmModel contains the data to disaply in the TableView widget    
class AlarmModel(ModelView) :
   def __init__(self,data=None,parent = None, *args) :
      super(AlarmModel,self).__init__(data,parent,*args) 
 
      self.columnconfig['timestamp'] = 150
      self.columnconfig['status'] = 75

      self.columns = ['type','priority','status','name','timestamp',
         'location', 'category']
 
      
   #Overloaded function that must be defined.      
   def data(self,index,role) :
      #The index (contains both x,y) and role are passed.  
      #The roles give instructions about how to display the model.
      row = index.row()
      col = index.column()
       
      #Center column 2, the timestamp
      if (role == Qt.TextAlignmentRole) : 
         return(Qt.AlignCenter)
      
      alarm = self.data[row] 
      (sevr,latch) = self.GetSevrDisplay(alarm) 
      
      if (col == self.GetColumnIndex('status')) :
         if (role == Qt.BackgroundRole) :
            if (latch != None) :
               return(GetQtColor(latch))
      
         if (role == Qt.DecorationRole) :
            image = GetStatusImage(sevr)
            if (image != None) :
               return(QIcon(image))
      
      #Insert the appropriate information into the display, based
      #on the column. Column "0" is handled by the StatusDelegate
      if role == Qt.DisplayRole :
         if (col == self.GetColumnIndex('status')) :
            return(sevr)         
         
         if (col == self.GetColumnIndex('name')) :
            return(alarm.GetName())
         
         if (col == self.GetColumnIndex('timestamp')) :
            
            timestamp = alarm.GetTimeStamp()  
            
            
            if (timestamp == None) :
               timestamp = alarm.GetAckTime()
            if (timestamp != None) :
               return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         
         
         if (col == self.GetColumnIndex('category')) :
            return(alarm.GetCategory())
         if (col == self.GetColumnIndex('location')) :
            return(alarm.GetLocation())  
   
   #Determine which images to use as the status indicators
   def GetSevrDisplay(self,alarm) :
      
      #latched and status column display are dependent
      sevrdisplay = None
      latchdisplay = None
      
      sevr = alarm.GetSevr()
      latched = alarm.GetLatchSevr()
      
      #Nothing to see here. No alarm, no latching
      if (sevr == "NO_ALARM" and latched == None) :
         sevrdisplay = None
         latchdisplay = None
      
      #Latch and alarm cleared   
      elif (sevr == "NO_ALARM" and latched == "NO_ALARM") :
         sevrdisplay = None
         latchdisplay = None
      
      #Alarm has cleared, but still latched   
      elif (sevr == "NO_ALARM") :
         sevrdisplay = sevr
         latchdisplay = latched
      
      #Alarm in and latched  
      elif (sevr != "NO_ALARM" and latched != "NO_ALARM") :
         sevrdisplay = sevr
         latchdisplay = latched
        
      else :
         
         print("UNNOWNDISPLAY: SEVR:",sevr,"LATCHED",latched)
     
      return(sevrdisplay,latchdisplay)
   
   


class ProxyModel(QtCore.QSortFilterProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(ProxyModel,self).__init__(*args,**kwargs)
      self.filtercol = None
      
   def setFilter(self,column,filtered=False) :
      if (not filtered) :
         self.filtercol = None
      else :
         self.filtercol = column

      self.sourceModel().headerDataChanged.emit(Qt.Horizontal,column,column)
   
#   def filterAcceptsRow(self,row,parent) :
 #     super(ProxyModel,self).__init__()
      
      

      
