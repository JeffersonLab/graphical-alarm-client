
#Contains the AlarmTable and the AlarmModel

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette

from FilterMenu import *
from Actions import *
from PropertyDialog import *
from utils import *

#Parent tableview 
class JAWSTableView(QtWidgets.QTableView) :
   """ 
      JAWSTableView - parent for AlarmTable and OverrideTable
   """

   def __init__(self,*args,**kwargs) :
      super(JAWSTableView,self).__init__(*args,**kwargs)
      
      #Adjusts columns to contents
      self.setSizeAdjustPolicy(
        QtWidgets.QAbstractScrollArea.AdjustToContents)
      
      #Expands table if more rows added.
      self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
         QtWidgets.QSizePolicy.MinimumExpanding)
      
      #Allow the sections (columns) to be rearranged
      header = self.horizontalHeader()
      header.setSectionsMovable(True)
      
      #Add a context menu (3rd mouse) to the header
      header.setContextMenuPolicy(Qt.CustomContextMenu)
      header.customContextMenuRequested.connect(self.selectHeader)
      
 
   #Get the single alarm that is selected.
   def getSelectedAlarm(self) :
      """ 
         Get the single selected alarm 
         :returns JAWSAlarm
      """
      alarmlist = self.getSelectedAlarms()
      
      alarm = None
      if (len(alarmlist) > 0) :
         alarm = alarmlist[0]
      return(alarm)
        

   def getSelectedAlarms(self) :
      """ 
         Get the list of alarms that have been selected on the table
         :returns list of JAWSAlarms
      """
      alarmlist = []
   
      #Access both the proxy model and the sourcemodel
      proxymodel = getProxy() 
      sourcemodel = getModel()     
   
      #The indices returned are that of the proxymodel, which is what 
      #the table LOOKS like. We need the source model index to identify the
      #actual selected alarm.
      indices = self.selectedIndexes()
   
      for index in indices :
         proxy_index = index
         #convert the proxy_index into a source_index, 
         #and find the row that is associated with the selected alarm(s)
         source_row = proxymodel.mapToSource(proxy_index).row()
         alarm = sourcemodel.data[source_row]         
         alarmlist.append(alarm)
      return(alarmlist)

   
   def rowSelected(self) :
      """ #If a row is selected, configure tool bar as appropriate. """
      getManager().getToolBar().configureToolBar()

  
   def selectHeader(self,vis) :
      """ 
         User has requested the contextmenu
         signal passes in the header position (visible column index)  
         If the columns have been rearranged, 
         they will have a "visualIndex" and a "logicalIndex" 
         Need to know what the logicalIndex is of the passed in vis 
     
     """
      col = self.horizontalHeader().logicalIndexAt(vis)
      
      #Most columns have a filter associated with it 
      name = getModel().getColumnName(col)
      jawsfilter = getFilterByHeader(name)      
      
      #If there is a filter, show the filter menu
      if (jawsfilter != None) :
         if (jawsfilter.getName() == 'timestamp') :
            menu = ExclusiveFilterMenu(jawsfilter)
         else :
            menu = FilterMenu(jawsfilter) 
         action = menu.exec_(self.mapToGlobal(vis))
   
   
   #Action common to JAWSTables
   def addPropertyAction(self,menu) :
      """ Display the properties of the select alarm
      """
      alarm = self.getSelectedAlarm()    
      PropertyAction(menu,alarm).addAction()
   
   def getDefaultSort(self) :
      """ Determine the default sort if not in user prefs
      """
      sortcolumn = getModel().getColumnIndex(self.defaultsort)
      return(sortcolumn,self.defaultorder)

 
#Extend the table view for our own AlarmTable
class AlarmTable(JAWSTableView) :
   """ Extend JAWSTableView for viewing the ActiveAlarms
   """
   def __init__(self,*args,**kwargs) :
      super(AlarmTable,self).__init__(*args,**kwargs)
      
      self.defaultsort = "timestamp"
      self.defaultorder = 1
   


   def contextMenuEvent(self,event) :
      """  
         Context menu when user right-mouse clicks in a cell. 
         Multiple rows/columns/cells can be selected   
      """
      menu = QtWidgets.QMenu(self)  
      
      #TitleAction is a placeholder for the title of the context menu
      self.addTitleAction(menu)
      
      #separator between the title and actions.
      separatorbg = "background: red"   
      style = "QMenu::separator {background: red;}"
      menu.setStyleSheet(style)
      separator = menu.addSeparator()
      
      self.mainmenu = menu
      
      self.addAckAction(menu)
      self.addPropertyAction(menu)
      self.addOverrideAction(menu)
      
      action = self.performAction(event)
      
      if (action != None) :        
         
         action.performAction(self.getSelectedAlarms())
   
   def performAction(self,event) :
      #Not sure why (ugh) but if the menu calls 
      #mapToGlobal directly, the focus remains on the 
      #AlarmTable...instead of the potential dialog
      action = self.mainmenu.exec_(self.mapToGlobal(event.pos()))
      return(action)
      
   def addTitleAction(self,menu) :
      TitleAction(menu).addAction()
   
   def addOverrideAction(self,menu) :
      OverrideAction(menu).addAction()

   #User can acknowledge the selected alarms
   def addAckAction(self,menu) :
      AckAction(menu).addAction()

#The latched and status column (col=0, col=1) 
#Displays the status indicators.
#Must create our own delegate.     
class StatusDelegate(QtWidgets.QStyledItemDelegate) :
   def __init__(self,statusindex) :
      super(StatusDelegate,self).__init__()
      
      self.statusindex = statusindex 
      
      
   #Size of the column
   def sizeHint(self,option,index) :
      return(QtCore.QSize(50,50))
   
   #Must override this method to use an image   
   def paint(self,painter,option,index) :
      
      row = index.row()
      col = index.column()
      alarm = getModel().data[row]
      
      
      #The data is the value from the "data" subroutine.
      #In this case the "latched" and "sevr" status'
      data = index.data()
      
      #The alarm associated with this col=0 or col=1
      if (col == self.statusindex) :
         if (data != None) :                                
            image = GetStatusImage(data)
            if (image == None) :
               return
            small = image.scaled(
               option.rect.size(),Qt.KeepAspectRatio);   
            x = option.rect.center().x() - small.rect().width() / 2 + 5
            y = option.rect.center().y() - small.rect().height() / 2 + 2
            painter.drawPixmap(x, y, small)

      
#Create the ShelfTable
class OverrideTable(JAWSTableView) :
   def __init__(self,*args,**kwargs) :
      super(OverrideTable,self).__init__(*args,**kwargs)
      
      self.defaultsort = "timeleft"
      self.defaultorder = 1
      self.columnlist = list(getManager().columns)
      statusindex = self.columnlist.index("status")
      
      self.setItemDelegateForColumn(statusindex, StatusDelegate(statusindex))
 
   #Context menu when user right-mouse clicks in a cell. 
   #Multiple rows/columns/cells can be selected   
   def contextMenuEvent(self,event) :      
      return
      menu = QtWidgets.QMenu(self)
      self.AddUnShelveAction(menu) 
      self.AddShelfAction(menu)
      self.addPropertyAction(menu) 
          
      action = menu.exec_(self.mapToGlobal(event.pos()))
 
   
