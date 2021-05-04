#NOTE ABOUT METHOD AND VARIABLE NAMES
# --- self.myvariable     -- variable for this application
# --- def MyMethod()      -- method implemented for this application
# --- def libraryMethod() -- method accessed/overloaded from a python library

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
      
      self.columnconfig = GetManager().columns
      self.columnlist = list(self.columnconfig)
      self.filtercols = {}
      
   #rowCount must be overloaded. 
   #Overload it here, since the same for all children 
   def rowCount(self,index) :
      return(len(self.data))
   
   #columnCount must be overloaded
   def columnCount(self,index) :      
      
      return(len(self.columnlist))
   
   def GetColumnName(self,col) :
       return(self.columnlist[col])
   
   def SetHeader(self,columname,filtered) :      
      headercol = GetModel().GetColumnIndex(columname)
      if (filtered) :         
         self.SetFilter(headercol,True)  
         GetManager().GetRemoveFilterAction().setChecked(True)
      else :                  
         GetManager().GetRemoveFilterAction().SetState()
         self.SetFilter(headercol,False)

        
   def GetColumnIndex(self,property) :
      
      if (not property in self.columnlist) :
         index = None
      else :
         index = self.columnlist.index(property)
      
      return(index)
   
   def GetColWidth(self,property) :
      width = None
      
      if (property in self.columnconfig) :
         if ('size' in self.columnconfig[property]) :
            width = self.columnconfig[property]['size']
         
      return(width)   
   
          
   def ApplyChanges(self,showlist=None) :
      
      if (showlist == None) :
         showlist = []
         
      #The horizontal header for our table model
      horizheader = GetTable().horizontalHeader()
      
      #The col, is the "logical" index for the model.
      #it's the one that stays constant, no matter what the 
      #user sees.
      for col in range(self.columnCount(0)) :        
         #The "visualindex" is the column index that the user 
         #is actually seeing. We want to move the visual index
         #if the user changes the order in the "show" box.
         visualindex = horizheader.visualIndex(col)
         
         #Get the header text for this column
         header = self.headerData(col,Qt.Horizontal,Qt.DisplayRole)
         
         #If the header (lower case) is in the list of properties
         #to show...
         if (header.lower() in showlist) :
            #Where in the showlist is it? 
            index = showlist.index(header.lower())
            
            #Make sure the "logical" column is showing.
            GetTable().horizontalHeader().showSection(col)
            #Now, move the visual column to the new index.
            GetTable().horizontalHeader().moveSection(visualindex,index)          
         else :
            #If in the "hide" list, simply hide the column
            GetTable().horizontalHeader().hideSection(col)
      
      #Some columns are wider than others, make sure the header has the
      #correct width for the property
      self.ConfigureColumns()
      
      #Force the manager to resize to the new size of the table.
      GetManager().SetSize()
   
   #Return the list of columns in the order that they are visible.
   def VisibleColumnOrder(self) :

      options = []
      hidden = []
      horizheader = GetTable().horizontalHeader()
      
      #Traverse each column in the table/model
      for col in range(self.columnCount(0)) :        
         
         #The "visualindex" is the column index that the user 
         #is actually seeing. We want the combobox to be in the same
         #order as the columns
         #if the user changes the order in the "show display" box.
         visualindex = horizheader.visualIndex(col)
         
         #Get the header text for this column
         header = self.headerData(col,Qt.Horizontal,Qt.DisplayRole)
         if (GetTable().isColumnHidden(col)) :
            hidden.append(header.lower())
         else :
            #Insert the header at the visible index.        
            options.insert(visualindex,header.lower())
      
      for header in hidden :
         
         options.append(header)
      
      
      
      return(options)
  
   def ConfigureColumns(self) :
      modelindex = self.GetColumnIndex
      for prop in self.columnlist :
         width = self.GetColWidth(prop)
         if (width != None) :
            GetTable().setColumnWidth(modelindex(prop),width)
   
   def UpdateModel(self) :
      GetManager().SetSize()   

   #Add alarm to the data. 
   def AddAlarm(self,alarm) :
      #Remove the alarm from the data first.
      if (alarm in self.data) :
         self.data.remove(alarm)
      
      
      #Need to emit this signal so that the TableView will be ready
      self.layoutAboutToBeChanged.emit()    
      #add the alarm to to the model data.
      self.data.append(alarm)
      #Emit signal to the TableView to redraw
      self.layoutChanged.emit()
      
      GetManager().GetToolBar().Configure()
      GetManager().SetSize()
      
         
   #Remove the alarm. 
   def RemoveAlarm(self,alarm) :
      
      #Double check that the alarm is in the dataset.
      if (alarm in self.data) :        
         #Warn the TableView
         self.layoutAboutToBeChanged.emit()
         #Actually remove the alarm
         self.data.remove(alarm)   
         #Emit signal to TableView to redraw
         self.layoutChanged.emit()
         
      GetManager().GetToolBar().Configure()
      GetManager().SetSize()
     
   #Configure the header if the data is filtered      
   def SetFilter(self,column,filtered=False) :
      
      #If the user filters the data from a filter menu.
      #indicate that on the column header by adding a little
      #filter icon to the columns that have been filtered.
      #try :
      if (not filtered) :
         self.filtercols[column] = False
      else :
         self.filtercols[column] = True
      self.headerDataChanged.emit(Qt.Horizontal,column,column)
 
   
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
         return(self.columnlist[section].title())
      
      return(QtCore.QAbstractTableModel.headerData(self,section,orientation,role))


#The model used with the ShelfManager.
class ShelfModel(ModelView) :
   def __init__(self,data=None,parent=None,*args) :
      super(ShelfModel,self).__init__(data,parent,*args)
      
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
   
   

#proxyModel->invalidate();
class ProxyModel(QtCore.QSortFilterProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(ProxyModel,self).__init__(*args,**kwargs)
      
      self.sortpriority = []
   
   #Sorting by status is a custom sort, so need to override proxymodel's
   #lessThan method
   def lessThan(self,leftindex,rightindex) :
      #The sort column 
      col = leftindex.column()
      
      #Get the header text for this column
      header = self.sourceModel().headerData(col,Qt.Horizontal,Qt.DisplayRole)
      
      #If not the status column, just sort as normal
      if (not header.lower() == "status") :
         return(super(ProxyModel,self).lessThan(leftindex,rightindex))
      
      #These values will be put somewhere better...
      statusvals = ['LATCHED','MAJOR','MINOR']
      
      #Get the status of the "left" and "right" alarm
      leftalarm = self.sourceModel().data[leftindex.row()].GetStatus()
      rightalarm = self.sourceModel().data[rightindex.row()].GetStatus()
      
      #The statusvals list is in order of importance. 
      #So, compare the index for the alarm's status. Lower wins
      leftrank = statusvals.index(leftalarm)
      rightrank = statusvals.index(rightalarm)
      
      if (leftrank < rightrank) :
         return(True)
      else :
         return(False)
    
   def filterAcceptsRow(self,row,parent) :
      
      filters = GetManager().filters
      if (len(filters) == 0) :
         
         GetManager().MakeFilters()
      
      index = self.sourceModel().index(row,0,parent)      
      alarm = self.sourceModel().data[row]
      
      keep = True
      for filter in GetManager().filters :
         
         keep = filter.ApplyFilter(alarm)
               
         if (not keep) :
            return(False)
      if (keep) :
         return (super(ProxyModel,self).filterAcceptsRow(row,parent))
      
      

      
