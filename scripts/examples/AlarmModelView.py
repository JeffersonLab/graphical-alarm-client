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
      
      self.setItemDelegateForColumn(0,StatusDelegate(self))
      self.setColumnWidth(2,100)
      
#AlarmModel contains the data to disaply in the TableView widget    
class AlarmModel(QtCore.QAbstractTableModel) :
   def __init__(self,data=None,parent = None, *args) :
      super(AlarmModel,self).__init__(parent,*args) 
      
      self.data = data or []
      self.rowheight = 50
     
   #Add alarm to the data. 
   def addAlarm(self,alarm) :
      if (alarm in self.data) :
         self.data.remove(alarm)
         
      #add the alarm to to the model data.
      self.data.append(alarm)
      #Emit signal to the TableView to redraw
      self.layoutChanged.emit()
      #ensure the Main Gui is sized correctly.
      GetMain().resize()
   
   #Remove the alarm. 
   def removeAlarm(self,alarm) :
      #Double check that the alarm is in the dataset.
      if (alarm in self.data) :        
         self.data.remove(alarm)   
         self.layoutChanged.emit()
         #Resize the main window
         GetMain().resize(bigger=False)
            
   #Overloaded function that must be defined.      
   def data(self,index,role) :
      #The index (contains both x,y) and role are passed.  
      #The roles give instructions about how to display the model.
      row = index.row()
      col = index.column()
            
      #Center column 2, the timestamp
      if (role == Qt.TextAlignmentRole and (col == 2)) :
         return(Qt.AlignCenter)
         
      #Insert the appropriate information into the display, based
      #on the column. Column "0" is handled by the StatusDelegate
      if role == Qt.DisplayRole :
         alarm = self.data[row]         
         if (col == 1) :
            return(alarm.GetName())
         if (col == 2) :  
            return(alarm.GetTimeStamp())
         if (col == 3) :
            return(alarm.GetCategory())
         if (col == 4) :
            return(alarm.GetLocation())  
   
   #rowCount must be overloaded
   def rowCount(self,index) :
      return(len(self.data))
   
   #columnCount must be overloaded
   def columnCount(self,index) :      
      return(5)
   
   #Display headers for the columns
   def headerData(self,section,orientation,role) :
      if (role != Qt.DisplayRole) :
         return
      if (orientation != Qt.Horizontal) :
         return      
      if (section == 0) :
         return("Status")
      if (section == 1) :
         return("Name")
      if (section == 2) :
         return("TimeStamp")
      if (section == 3) :
         return("Category")
      if (section == 4) :
         return("Area")

#The status column (col=0) Displays the status indicator.
#Must create our own delegate.     
class StatusDelegate(QtWidgets.QStyledItemDelegate) :
   #Size of the column
   def sizeHint(self,option,index) :
      return(QtCore.QSize(50,50))
   
   #Must override this method to use an image   
   def paint(self,painter,option,index) :
      #The model that the delegate belongs to
      model = index.model()
      row = index.row()
      col = index.column()
      
      #Only for column 0
      if (col == 0) :
         #The alarm associated with this row of the model
         alarm = model.data[row]
         
         #Get the status of the alarm
         status = alarm.GetStatus()
         
         #What image (status indicator) will we use?
         image = alarm.GetDisplayIndicator()
         
         #Calculate the location of the image.
         x = option.rect.center().x() - image.rect().width() / 2
         y = option.rect.center().y() - image.rect().height() / 2
         painter.drawPixmap(x, y, image)
