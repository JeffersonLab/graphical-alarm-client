import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject,QThreadPool
from PyQt5.QtWidgets import QAction, QToolBar, QSpacerItem, QDialog

from AlarmModelView import *
from utils import *

#Abstract listbox with filter choices
class FilterList(QtWidgets.QWidget) :
   def __init__(self,text,parent=None) :
      super(FilterList,self).__init__(parent)
      
      self.parent = parent
      #Create a VBoxLayout
      layout = QtWidgets.QVBoxLayout()
      
      #label
      labellayout = QtWidgets.QHBoxLayout()
      label = QtWidgets.QLabel(text)
      font = QtGui.QFont()
      font.setBold(True)
      label.setFont(font)
      label.setAlignment(Qt.AlignBottom)
      labellayout.addWidget(label,0,Qt.AlignBottom|Qt.AlignLeft)
      
      self.checkbox = QtWidgets.QCheckBox()
      self.checkbox.clicked.connect(self.selectAll)
      self.checkbox.setCheckState(Qt.Checked)
     
      labellayout.addWidget(self.checkbox)
      labelwidget = QtWidgets.QWidget()
      labelwidget.setLayout(labellayout)
      
      #list box:
      self.listbox = QtWidgets.QListWidget()
      self.listbox.setFixedWidth(100)
      
      layout.addWidget(labelwidget,0,Qt.AlignBottom)
      layout.addWidget(self.listbox)
      self.setLayout(layout)
      self.listbox.setSpacing(2)
      
      self.makeOptions()
  
   def selectAll(self) :
      for filter in self.filteritems :
         filter.setCheckState(self.checkbox.checkState())
      
      self.parent.applyFilters()
   
   
   #Create a checkbox for each item
   def makeOptions(self) :
      self.blankoption = None
      self.filteritems = []
      
      for status in self.options :
         item = QtWidgets.QListWidgetItem(status,self.listbox)
         item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  
         item.setCheckState(Qt.Checked)
         self.listbox.itemClicked.connect(self.parent.applyFilters)
         if (status == "blank") :
            self.blankoption = item
         self.filteritems.append(item)
   
   def getHeaderColumn(self) :
      return(self.column)
   
   def addHeader(self) :
      return(self.addheader)
   
   def keepBlank(self) :
      keepblank = True
      if (self.blankoption != None) :
         keepblank = self.blankoption.checkState()
         if (keepblank == 0) :
            keepblank = False
      return(keepblank)
      
   #Apply filters if applicable            
   def applyFilter(self,alarmlist) :
      
      #The alarms that pass the filter
      selected = []
          
      #If we end up filtering, update the header to indicate as such
      addheader = False
      
      #We'll go through each alarm and see if it passes the filter.
      numrows = GetModel().rowCount(0)
      
      keepblank = self.keepBlank()
      #Determine the check state of each of the filter items
      for filterstatus in self.filteritems :
         filter = filterstatus.text()
         checked = filterstatus.checkState()

         #If one has been DESELECTED, the user is filtering.
         if (not checked and numrows > 0) :
            #So add the filter icon to the header
            addheader = True
         
         #Go through the alarms, and determine whether or not the alarm
         #is included in the new model.
         for alarm in alarmlist :
            if (alarm in selected) :
               continue              
            val = self.GetFilterVal(alarm)
            if (val == None and keepblank) :
               selected.append(alarm)
            elif (checked and val == filter) :
               selected.append(alarm) 
      self.addheader = addheader
      
      
      return(selected)


class CategoryFilter(FilterList) :
   def __init__(self,parent=None) :
      self.options = list(GetConsumer().GetCategories())
      self.options.append("blank")
      
      super(CategoryFilter,self).__init__("Category",parent)
      
      self.column = 4
   
   def GetFilterVal(self,alarm) :
      return(alarm.GetCategory())
         
class LocationFilter(FilterList) :
   def __init__(self,parent=None) :
      
      self.options = list(GetConsumer().GetLocations())
      self.options.append("blank")
      self.options.reverse()
      super(LocationFilter,self).__init__("Location",parent)
      
      self.column = 5
     
   def GetFilterVal(self,alarm) :
      return(alarm.GetLocation())
        
#Choices for the status filter          
class StatusFilter(FilterList) :
  
   def __init__(self,parent=None) :
      
      self.options = ['MAJOR','MINOR']
      super(StatusFilter,self).__init__('Status',parent)
      
      self.column = 1
   
   def GetFilterVal(self,alarm) :
      return(alarm.GetSevr())
      
class FilterDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(FilterDialog,self).__init__(parent,*args,**kwargs)
      
      self.setModal(0)
      self.setSizeGripEnabled(True)
      
      self.filters = []
  
      statusfilter = StatusFilter(self)
      locationfilter = LocationFilter(self)
      categoryfilter = CategoryFilter(self)
      
      self.filters.append(statusfilter)
      self.filters.append(locationfilter)
      self.filters.append(categoryfilter)
      
      layout = QtWidgets.QGridLayout()     
      layout.addWidget(statusfilter,1,0)
      layout.addWidget(categoryfilter,1,1)
      layout.addWidget(locationfilter,1,2)
      
      
      groupbox = QtWidgets.QGroupBox("Filter Active Alarms")
      groupbox.setLayout(layout) 
      
      vlayout = QtWidgets.QVBoxLayout()
      vlayout.addWidget(groupbox)
      self.setLayout(vlayout) 
      self.setWindowTitle("Filter")
      self.show()
   
   def applyFilters(self) :
      alarmlist = GetModel().data[:]
      filtered = []
      
      for filter in self.filters :
         filtered = filter.applyFilter(alarmlist)
         alarmlist = filtered
      
      #Create a new alarm model with the selected data  
      alarmmodel = AlarmModel(alarmlist)
      for alarm in alarmmodel.data :
         print("KEEPING:",alarm.GetName())
      print("----")
      
 #     print("ALARMODEL:",alarmmodel)
      #Set this new model to as the source model for our proxy
      GetManager().proxymodel.setSourceModel(alarmmodel)
  #    print("MANGAER:",GetManager())
      alarmmodel.filtercols = {}
      #Add the filter icons if applicable
      for filter in self.filters :
         
         col = filter.getHeaderColumn()
        
         if (filter.addHeader()) :
            alarmmodel.setFilter(col,filtered=True) 
         else :
            alarmmodel.setFilter(col,filtered=False)

         
class FilterAction(QtWidgets.QAction) :
   def __init__(self,parent,*args,**kwargs) :
      super(FilterAction,self).__init__(parent,*args,**kwargs)
      
      self.parent = parent
      icon = QtGui.QIcon("funnel--plus.png")
      text = "Filter"
      tip = "Filter alarms"
      self.setIcon(icon)
      self.setIconText(text)
      self.setToolTip(tip)
      
      self.triggered.connect(parent.showFilter)
   
