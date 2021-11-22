
#Contains the JAWSModel class inherited by AlarmModel and OverrideModel

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QObject,QThreadPool,QThread
from utils import *

from Filters import *

#Parent JAWSModel. AlarmModel and OverrideModel inherit         
class JAWSModel(QtCore.QAbstractTableModel) :
   """ 
      JAWSModel - parent for AlarmModel and OverrideModel
   """
   def __init__(self,data=None,parent = None, *args) :
      super(JAWSModel,self).__init__(parent,*args) 
      
      self.data = data or []   #Data passed in upon construction
      self.columnconfig = getManager().columns  #Column definitions 
      self.columnlist = list(self.columnconfig) #List of columns
      self.filtercols = {}
            
   def rowCount(self,index) :
      """ QAbstractTabelModel virtual method
      """
      return(len(self.data))
   
   def columnCount(self,index) :      
      """ QAbstractTabelModel virtual method
      """
      return(len(self.columnlist))
   
   #Display headers for the columns
   def headerData(self,section,orientation,role) :
      """ QAbstractTabelModel virtual method
      """
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
         return(self.makeHeaderTitle(section))      
      return(QtCore.QAbstractTableModel.headerData(self,section,orientation,role))

   def getColumnName(self,col) :
       """ Get the column header name for the col
       """
       return(self.columnlist[col])
   
   def getColumnIndex(self,alarmproperty) :
      """ Get the column index for the alarm property
      """
      alarmindex = None
      if (alarmproperty in self.columnlist) :
         alarmindex = self.columnlist.index(alarmproperty)
     
      return(alarmindex)
   
   def getColWidth(self,propertycolumn) :
      """ Some of the columns are defined with an initial width
          Args:
            propertycolumn : The property associated with the column
      """
      #initial width
      width = None
      #
      if (propertycolumn in self.columnconfig) :
         if ('size' in self.columnconfig[propertycolumn]) :
            width = self.columnconfig[propertycolumn]['size']
         
      return(width)   
   
   
   def configureColumns(self) :
      """  Configure widths for the columns
      """
      modelindex = self.getColumnIndex      
      for prop in self.columnlist :
         width = self.getColWidth(prop)
         if (width != None) :
            getTable().setColumnWidth(modelindex(prop),width)

   def visibleColumnOrder(self) :
      """ Return the list of columns in the order that they are visible
      """
      options = []
      hidden = []
      horizheader = getTable().horizontalHeader()
      
      #Traverse each column in the table/model
      for col in range(self.columnCount(0)) :        
         
         #The "visualindex" is the column index that the user 
         #is actually seeing. We want the combobox to be in the same
         #order as the columns
         #if the user changes the order in the "show display" box.
         visualindex = horizheader.visualIndex(col)
         
         #Get the header text for this column
         header = self.headerData(col,Qt.Horizontal,Qt.DisplayRole)
         if (getTable().isColumnHidden(col)) :
            hidden.append(header.lower())
         else :
            #Insert the header at the visible index.        
            options.insert(visualindex,header.lower())
      
      for header in hidden :         
         options.append(header)
      return(options)

   def configureHeader(self,columname,filtered) :           
      """ Configure the column's header
          Details: 
            If the data has been filtered, add filter icon to
            the associated header 
          Args:
            columnname : header column label
            filtered   : is the property associated with this
                         header filtered?
      """
      col = getModel().getColumnIndex(columname)
      
      self.filtercols[col] = filtered
      if (filtered) :
         getManager().getRemoveFilterAction().setChecked(True)
      else :
         getManager().getRemoveFilterAction().setState()
      self.headerDataChanged.emit(Qt.Horizontal,col,col)     
   
   def makeHeaderTitle(self,column) : 
      """ Determine the header display text
      """
      header = self.columnlist[column]
      header = header.replace("_"," ")
      return(header.title())

   #####    THIS MAYBE SHOULD BE MOVED SINCE SPECIFIC TO GUI       
   def applyDisplayPrefs(self,showlist=None) :
      """ Apply preferences to the model 
      """
      if (showlist == None) :
         showlist = []
         
      #The horizontal header for our table model
      horizheader = getTable().horizontalHeader()
      
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
            getTable().horizontalHeader().showSection(col)
            #Now, move the visual column to the new index.
            getTable().horizontalHeader().moveSection(visualindex,index)          
         else :
            #If in the "hide" list, simply hide the column
            getTable().horizontalHeader().hideSection(col)
      
      #Some columns are wider than others, make sure the header has the
      #correct width for the property
      self.configureColumns()
      
      #Force the manager to resize to the new size of the table.
      getManager().setSize()
   
   #Add alarm to the data. 
   def addAlarm(self,alarm) :
      """ Add the alarm to the model
      """
      #warn the model of the change
      self.layoutAboutToBeChanged.emit()    
      
      #Remove the alarm from the data first.
      if (alarm in self.data) :
         self.data.remove(alarm)
      
      #add the alarm to to the model data.
      self.data.append(alarm)
      #Emit signal to the TableView to redraw
      self.layoutChanged.emit()
      
      getManager().configureManager(alarm)
           
   #Remove the alarm. 
   def removeAlarm(self,alarm) :
      """ Remove the alarm from the model
      """
      #Double check that the alarm is in the dataset.
      if (alarm in self.data) :        
         #Warn the TableView
         self.layoutAboutToBeChanged.emit()
         #Actually remove the alarm
         self.data.remove(alarm)   
         #Emit signal to TableView to redraw
         self.layoutChanged.emit()
      
      getManager().configureManager(alarm) 



class JAWSProxyModel(QtCore.QSortFilterProxyModel) :
   """ The JAWS QSortFilterProxyModel
       Using with the QAbstractTableModel, allows for sorting
       and filtering of the source model (JAWSModel)
   """
   
   def __init__(self,*args,**kwargs) :
      super(JAWSProxyModel,self).__init__(*args,**kwargs)
      
      self.leftalarm = None
      self.rightalarm = None
      self.sortpriority = []
   
   
   def lessThan(self,leftindex,rightindex) :
      """ QSortFilterProxyModel method for sorting
          Overload the method to perform non-standard sorting
      """
      
      #The sort column 
      col = leftindex.column()
      
      #Get the header text for this column
      header = self.sourceModel().headerData(col,Qt.Horizontal,Qt.DisplayRole)
      
      #The sorting depends on the column header.
      #Use special sorting when needed
      if (header.lower() == "name") :
         return(self.nameLessThan(leftindex,rightindex))
      
      if (header.lower() == "status") :
         return(self.statusLessThan(leftindex,rightindex))

      #If not so special, use the standard sorting
      return(super(JAWSProxyModel,self).lessThan(leftindex,rightindex))

         
   def nameLessThan(self,leftindex,rightindex) :
      """ Compare two alarm names - case insensitive.
      """
      leftalarm = self.sourceModel().data[leftindex.row()]
      rightalarm = self.sourceModel().data[rightindex.row()]
      
      leftname = leftalarm.get_name().lower()
      rightname = rightalarm.get_name().lower()
      if (leftname < rightname) :
         return(True)
      else:
         return(False)
   
   
   def statusLessThan(self,leftindex,rightindex) :
      """ Compare the status value of alarms 
      """
      #These values will be put somewhere better...
      statusvals = ['LATCHED','MAJOR','ALARM','MINOR','NORMAL',None]
      
      #Get the status of the "left" and "right" alarm
      leftalarm = self.sourceModel().data[leftindex.row()]
      rightalarm = self.sourceModel().data[rightindex.row()]
      leftdisplay = self.getDisplay(leftalarm)
      rightdisplay = self.getDisplay(rightalarm)
             
      leftrank = statusvals.index(leftdisplay)
      rightrank = statusvals.index(rightdisplay)
      
      if (leftrank < rightrank) :
         return(True)
      else :
         return(False)
      return(True)

   
   def filterAcceptsRow(self,row,parent) :
      """ QSortFilterProxyModel method for filtering
          Overload the method to perform non-standard filtering
      """
      
      # Access the list of filteres assigned to this manager 
      filters = getManager().filters
      
      #Just in case we haven't defined filters yet...go ahead and create them
      if (len(filters) == 0) :        
         getManager().makeFilters()
      
      #Use the SOURCE MODEL (the official list of alarms)
      alarm = self.sourceModel().data[row]
            
      #Assume the alarm will be kept
      keep = True
      
      #Search filters have to be applied together.
      #The alarm is kept if of the search filters pass
      keep = getManager().applySearchFilters(alarm)
 
      if (not keep) :
         return(False)
      
      #Iterate through the remaining filters 
      #and apply each
      for jawsfilter in getManager().filters :
         keep = jawsfilter.applyFilter(alarm)
         if (not isinstance(jawsfilter,SearchFilter)) :
            if (not keep) :
               return(False)
      return(keep)
     
