#Contains the AlarmTable and the AlarmModel

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette

from Actions import *
from PropertyDialog import *
from utils import *

#Parent tableview 
#AlarmTable and ShelfTable inherit
class TableView(QtWidgets.QTableView) :
   def __init__(self,*args,**kwargs) :
      super(TableView,self).__init__(*args,**kwargs)
      
      #Adjusts columns to contents
      self.setSizeAdjustPolicy(
        QtWidgets.QAbstractScrollArea.AdjustToContents)
      
      #Expands table if more rows added.
      self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
         QtWidgets.QSizePolicy.MinimumExpanding)
      
      self.horizontalHeader().setSectionsMovable(True)
   
   #User can acknowledge the selected alarms
   def AddPropertyAction(self,menu) :
      action = PropertyAction(menu)
      alarmlist = GetSelectedAlarms()
      text = "Show Properties"
      if (len(alarmlist) == 1) :
         text = "Properties: " + alarmlist[0].GetName()
         menu.addAction(action)
         action.setText(text)
      return(action)
   
   #User can also shelve selected alarms
   def AddShelfAction(self,menu) :
      action = ShelfAction(menu)
      
      alarmlist = GetSelectedAlarms()
      text = "Shelve Selected"
      
      if(len(alarmlist) == 1) :
         text = "Shelve: " + alarmlist[0].GetName()
      if (len(alarmlist) > 0) :
         menu.addAction(action)       
         action.setText(text)
      return(action)

      
#Create the ShelfTable
class ShelfTable(TableView) :
   def __init__(self,*args,**kwargs) :
      super(ShelfTable,self).__init__(*args,**kwargs)
   
   #Context menu when user right-mouse clicks in a cell. 
   #Multiple rows/columns/cells can be selected   
   def contextMenuEvent(self,event) :      
      
      menu = QtWidgets.QMenu(self)
      self.AddUnShelveAction(menu) 
      self.AddShelfAction(menu)
      self.AddPropertyAction(menu) 
          
      action = menu.exec_(self.mapToGlobal(event.pos()))
      
   
   #User can unshelve selected alarms
   def AddUnShelveAction(self,menu) :
      
      action = UnShelveAction(menu)
      
      alarmlist = GetSelectedAlarms()
      text = "Unshelve Selected"
      if (len(alarmlist) == 1) :
         text = "Unshelve: " + alarmlist[0].GetName()
     
      if (len(alarmlist) > 0) :
         menu.addAction(action)
         action.setText(text)
      return(action)
 
   
#Extend the table view for our own AlarmTable
class AlarmTable(TableView) :
   def __init__(self,*args,**kwargs) :
      super(AlarmTable,self).__init__(*args,**kwargs)


   #Context menu when user right-mouse clicks in a cell. 
   #Multiple rows/columns/cells can be selected   
   def contextMenuEvent(self,event) :
      
      menu = QtWidgets.QMenu(self)                
      self.AddAckAction(menu)
      self.AddShelfAction(menu)
      self.AddPropertyAction(menu)
      action = menu.exec_(self.mapToGlobal(event.pos()))
      #action.PerformAction()
 
   #User can acknowledge the selected alarms
   def AddAckAction(self,menu) :
      action = AckAction(menu)      
      needsack = action.GetAlarmsToBeAcknowledged()   
      text = "Ack Selected"
      if (len(needsack) == 1) :
         text = "Ack: " + needsack[0].GetName()
      if (len(needsack) > 0) :         
         menu.addAction(action)
         action.setText(text)
      
      return(action)
   


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
      alarm = GetModel().data[row]
      (sevr,latch) = GetSevrDisplay(alarm)
      
      #The data is the value from the "data" subroutine.
      #In this case the "latched" and "sevr" status'
      data = index.data()
      
      #The alarm associated with this col=0 or col=1
      if (col == 0 or col == 1) :
         if (data != None) :                                
            
            image = GetStatusImage(data)
            if (image == None) :
               return
            #print(alarm.GetName(),"SEVR:",sevr,"LATCH:",latch)
            
          #  if (latch == None) :
           #    print("DRAWING CIRCLE FOR",alarm.GetName(),latch)
               #Calculate the location of the image.
            x = option.rect.center().x() - image.rect().width() / 2
            y = option.rect.center().y() - image.rect().height() / 2
            painter.drawPixmap(x, y, image)
       #     painter.setBrush
            #super().paint(painter,option,index)
                  
          #     except e :
           #       print("NOPE",e)
            

