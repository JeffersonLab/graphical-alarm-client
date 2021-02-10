#Contains the AlarmTable and the AlarmModel

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from utils import *
      
#Extend the table view for our own AlarmTable
class AlarmTable(QtWidgets.QTableView) :
   def __init__(self,*args,**kwargs) :
      super(AlarmTable,self).__init__(*args,**kwargs)
      
      #Adjusts columns to contents
      self.setSizeAdjustPolicy(
        QtWidgets.QAbstractScrollArea.AdjustToContents)
      
      #Expands table if more rows added.
      self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
         QtWidgets.QSizePolicy.MinimumExpanding)
      self.setItemDelegateForColumn(1,StatusDelegate(self))
      self.setItemDelegateForColumn(0,StatusDelegate(self))
   
   #Context menu when user right-mouse clicks in a cell. 
   #Multiple rows/columns/cells can be selected   
   def contextMenuEvent(self,event) :
      menu = QtWidgets.QMenu(self)
      row = self.rowAt(event.pos().y())
      
      proxymodel = self.model()
      sourcemodel = proxymodel.sourceModel()
      
      needsack = []
      #The indices returned are that of the proxymodel, which is what 
      #the table LOOKS like. We need the source model index to identify the
      #actual selected alarm.
      indexes = self.selectedIndexes()
      for index in indexes :
         proxy_index = index
         #convert the proxy_index into a source_index, 
         #and find the row that is associated with the selected alarm(s)
         source_row = proxymodel.mapToSource(proxy_index).row()
         alarm = sourcemodel.data[source_row]
         if (alarm.GetLatchSevr() != None and not "NO" in alarm.GetLatchSevr()) :
            needsack.append(alarm)
                
      ackaction = None
      if (len(needsack) > 0) :
         if (len(needsack) == 1) :
            ackaction = menu.addAction("Ack: " + needsack[0].GetName())
         else :
            ackaction = menu.addAction("Ack All")
    
      action = menu.exec_(self.mapToGlobal(event.pos()))
      if (action == ackaction) :
         self.AckAlarms(needsack) 
   
   #Acknowledge the list of alarms  
   def AckAlarms(self,alarmlist) :
      for alarm in alarmlist :
         alarm.AcknowledgeAlarm()
         
         
#AlarmModel contains the data to disaply in the TableView widget    
class AlarmModel(QtCore.QAbstractTableModel) :
   def __init__(self,data=None,parent = None, *args) :
      super(AlarmModel,self).__init__(parent,*args) 
      
      self.data = data or []
      
   #Add alarm to the data. 
   def addAlarm(self,alarm) :
      
      if (alarm in self.data) :
         self.data.remove(alarm)
      
      self.layoutAboutToBeChanged.emit()    
      #add the alarm to to the model data.
      self.data.append(alarm)
     
      #Emit signal to the TableView to redraw
      self.layoutChanged.emit()
      
      #Apply filters if applicable
      filters = GetMain().filterDialog
      if (filters != None) :
         filters.applyFilters()
         
   #Remove the alarm. 
   def removeAlarm(self,alarm) :
      
      #Double check that the alarm is in the dataset.
      if (alarm in self.data) :        
         self.layoutAboutToBeChanged.emit()
         self.data.remove(alarm)   
         self.layoutChanged.emit()
         
         #Apply filters.      
         filters = GetMain().filterDialog
         if (filters != None) :
            filters.applyFilters()

            
   #Overloaded function that must be defined.      
   def data(self,index,role) :
      #The index (contains both x,y) and role are passed.  
      #The roles give instructions about how to display the model.
      row = index.row()
      col = index.column()
            
      #Center column 2, the timestamp
      if (role == Qt.TextAlignmentRole) : # and (col == 2 or col == 3)) :
         return(Qt.AlignCenter)
         
      #Insert the appropriate information into the display, based
      #on the column. Column "0" is handled by the StatusDelegate
      if role == Qt.DisplayRole :
         alarm = self.data[row] 
         #How we display the sevr and latchsevr depend on eachother.
         (sevr,latch) = self.GetSevrDisplay(alarm)        
         
         if (col == 0) :
            return(latch)
         if (col == 1) :
            return(sevr)
         if (col == 2) :
            return(alarm.GetName())
         if (col == 3) :              
            timestamp = alarm.GetTimeStamp()
            
            if (timestamp == None) :
               timestamp = alarm.GetAckTime()
            return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         if (col == 4) :
            return(alarm.GetCategory())
         if (col == 5) :
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
   
   #rowCount must be overloaded
   def rowCount(self,index) :
      return(len(self.data))
   
   #columnCount must be overloaded
   def columnCount(self,index) :      
      return(6)
   
   #Display headers for the columns
   def headerData(self,section,orientation,role) :
      
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
         
         if (section == 0) :
            return("Latched")
         if (section == 1) :
            return("Status")
         if (section == 2) :
            return("Name")
         if (section == 3) :
            return("TimeStamp")
         if (section == 4) :
            return("Category")
         if (section == 5) :
            return("Area")
      return(QtCore.QAbstractTableModel.headerData(self,section,orientation,role))
   
   #Configure the header if filtered      
   def setFilter(self,column,filtered=False) :
      try :
         if (not filtered) :
            self.filtercols[column] = False
         else :
            self.filtercols[column] = True
         self.headerDataChanged.emit(Qt.Horizontal,column,column)
      except :
         pass

#The latched and status column (col=0, col=1) 
#Displays the status indicators.
#Must create our own delegate.     
class StatusDelegate(QtWidgets.QStyledItemDelegate) :
   
   #Size of the column
   def sizeHint(self,option,index) :
      return(QtCore.QSize(50,50))
   
   #Must override this method to use an image   
   def paint(self,painter,option,index) :
      
      row = index.row()
      col = index.column()
      
      #The data is the value from the "data" subroutine.
      #In this case the "latched" and "sevr" status'
      data = index.data()
      
      #The alarm associated with this col=0 or col=1
      if (col == 0 or col == 1) :
         if (data != None) :                    
            #What image (status indicator) will we use?
            image = GetStatusImage(data)
            if (image == None) :
               return
            #Calculate the location of the image.
            x = option.rect.center().x() - image.rect().width() / 2
            y = option.rect.center().y() - image.rect().height() / 2
            painter.drawPixmap(x, y, image)

class AlarmProxyModel(QtCore.QSortFilterProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(AlarmProxyModel,self).__init__(*args,**kwargs)
      self.filtercol = None
      
   def setFilter(self,column,filtered=False) :
      if (not filtered) :
         self.filtercol = None
      else :
         self.filtercol = column

      self.sourceModel().headerDataChanged.emit(Qt.Horizontal,column,column)
   
   def statusChanged(self,statuslist) :
      print("STATUS CHANGED",statuslist)