from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QMimeData
import datetime
import time
import pytz
from csv import reader,writer,DictReader,DictWriter

from utils import *
from Actions import *
from FilterMenu import *
from JAWSDialog import *

#The Preferences Dialog widget.
#The dialog is made up of individual preference widgets that 
#manage themselves
class PrefDialog(JAWSDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(PrefDialog,self).__init__(parent,*args,**kwargs)
      
      
      vlayout = self.vlayout
      filterprefs = FilterPrefs(self)
      vlayout.addWidget(filterprefs)
      self.filterprefs = filterprefs
      self.prefwidgets.append(filterprefs)
      
 #     timefilter = TimeFilterButton(self) 
  #    vlayout.addWidget(timefilter) 
      
   #   defaultrows = DefaultRowPrefs(self)
    #  vlayout.addWidget(defaultrows)
     # self.defaultrows = defaultrows
      #self.prefwidgets.append(defaultrows)
      
      #Allow the user to select the default sort column
      sortprefs = SortPrefs(self)
      vlayout.addWidget(sortprefs)
      self.sortprefs = sortprefs
      self.prefwidgets.append(sortprefs)
      
      #Allow the user to hide and display the columns that they want
      displayprefs = DisplayPrefs(self)
      vlayout.addWidget(displayprefs)
      self.displayprefs = displayprefs
      self.prefwidgets.append(displayprefs)

      #The "apply" and "close" buttons.
      buttons = self.makeButtons()
      vlayout.addWidget(buttons)
      
      self.setLayout(vlayout)
      self.layout().setAlignment(Qt.AlignTop)
      self.show()
   
   #Configure prefwidgets (if defined) 
   def configureDialog(self) :
      for prefwidget in self.prefwidgets :
         prefwidget.configureDialog()
      
   #Called to reset preferences
   def reset(self) :
      
      for pref in self.prefwidgets :
         pref.reset()      
   
   #The accessible buttons on the dialog
   def makeButtons(self) :
      
      layout = QtWidgets.QHBoxLayout()
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
      
      acceptbutton = QtWidgets.QPushButton("Apply Changes")
      acceptbutton.clicked.connect(self.applyChanges)
      layout.addWidget(acceptbutton) 
      getManager().setButtonStyle(acceptbutton)
      #acceptbutton.setStyleSheet('QPushButton{background-color: darkRed; color: white}')
      
      cancelbutton = QtWidgets.QPushButton("Close")
      cancelbutton.clicked.connect(self.Close)
      layout.addWidget(cancelbutton)
     # cancelbutton.setStyleSheet('QPushButton{background-color: darkRed; color: white}')
      getManager().setButtonStyle(cancelbutton)
      return(widget)
   
   #Apply changes for each applicable section
   def applyChanges(self) :            
      
      #Does the user also want to save the changes?
      save = self.SaveChanges()      
      for pref in self.prefwidgets :
         if (save) :
            pref.SaveChanges()
         pref.applyChanges()
      
      if (save) :
         getManager().savePrefs()
         
   #Ask if the user wants to save the changes
   def SaveChanges(self) :
      
      save = False
      msgBox = QtWidgets.QMessageBox.question(self,"Save?",
         "Save your preferences?",
         QtWidgets.QMessageBox.Save| QtWidgets.QMessageBox.No,
         QtWidgets.QMessageBox.Save)
      
      #If so, get the pref file name, and if it already exists,
      #remove it, so it can be replaced. 
      
      if (msgBox == QtWidgets.QMessageBox.Save) :
         save = True
      return(save)
      
   #Close the dialog     
   def Close(self) :
      self.close()  



class TimeFilterButton(QtWidgets.QPushButton) :
   def __init__(self,parent=None,*args,**kwargs) :
      super(TimeFilterButton,self).__init__("Timestamp",parent)
      
      self.clicked.connect(self.timeButtonPushed)

   def timeButtonPushed(self) :
      self.timewidget = TimeWidget()
      self.timewidget.show()
      
class TimeWidget(QtWidgets.QWidget) :
   def __init__(self) :
      super(TimeWidget,self).__init__()
      
      widgetlayout = QtWidgets.QVBoxLayout()
      self.setLayout(widgetlayout)
      
      fromlayout = QtWidgets.QHBoxLayout()
      fromwidget = QtWidgets.QWidget()
      fromwidget.setLayout(fromlayout)
      
      fromlabel = QtWidgets.QLabel("To")
      fromlayout.addWidget(fromlabel)
      
      
      datetime = QtCore.QDateTime.currentDateTime()
      timezone = QtCore.QTimeZone(b'America/New_York')
    
      newdatetime = datetime.toTimeZone(timezone)




 
      
      fromchooser = QtWidgets.QDateTimeEdit(newdatetime)
  
      
      
 #     print("TIMESPEC",fromchooser.timeSpec())
      fromlayout.addWidget(fromchooser)
  #    fromchooser.setDisplayFormat("HH:MM")
      
      widgetlayout.addWidget(fromwidget)
      now = QtCore.QDateTime.currentDateTime()
     
      #print(now.toString(Qt.DefaultLocaleLongDate))
      zonelist = QtCore.QTimeZone.availableTimeZoneIds(QtCore.QLocale.UnitedStates)
    #  for zone in zonelist :
         
class PrefGroupBox(QtWidgets.QGroupBox) :
   def __init__(self,text,parent,*args,**kwargs) :
      super(PrefGroupBox,self).__init__(text)      
      
      getManager().setGroupBoxStyle(self) 
      self.parent = parent
  
   def reset(self) :
      pass
   
   def configureDialog(self) :
      pass
   
   def SaveChanges(self) :
      pass
       

      
      


#Display the filter preferences.
class FilterPrefs(QtWidgets.QGroupBox) :
   def __init__(self,parent=None,name="Default Filters",*args,**kwargs) :
      super(FilterPrefs,self).__init__(name,parent)
      
      getManager().setGroupBoxStyle(self)
      self.parent = parent
      #Each filter will have a button that will need to be configured
      self.filterbuttons = []
     
      
      vlayout = QtWidgets.QVBoxLayout()
      vlayout.setSpacing(1)
      self.layout = vlayout
      self.setLayout(vlayout) 
      
      #Widget that contains a button for each filter
      filterwidget = self.AddFilterWidgets()
      vlayout.addWidget(filterwidget)
      self.filterwidget = filterwidget
      
      self.filteraction = getManager().getRemoveFilterAction()
      
      #Use the filteraction's icon
      icon = self.filteraction.icon
      
      #User can remove all filters from here.
      button = QtWidgets.QPushButton(icon,"Remove All Filters")
      button.clicked.connect(self.RemoveFilters)
      self.removebutton = button
      self.layout.addWidget(self.removebutton)
      
      #Configure the remove and filter buttons
      self.configureDialog()
   
   #Enable/disable the removebutton, and add/remove icon for each
   #filter button   
   def configureDialog(self) :
      filtered = self.filteraction.getFilterState()
      
      self.removebutton.setEnabled(filtered)
      for button in self.filterbuttons :
         
         button.configureDialog()
      
   #Called by the Remove Filters button  
   def RemoveFilters(self) :
      filteraction = self.filteraction   
      filteraction.removeAllFilters()
  
      
   #We want to add the filter buttons in the order that
   #they appear on the table. Each time the pref dialog is 
   #opened, remove the previous set, and then add them back in
   #the right order.
   def RemoveFilterWidgets(self) :
      #All of the filter buttons are associated with this widget.
      self.filterwidget.deleteLater()
 
   #Sort filters in the order that they are visible in the table
   def SortFilters(self) :
      sorted = []
      #Get the header text in visible order
      visualorder = getModel().visibleColumnOrder() 
      
      #Add the filter for each header to the sorted list
      for header in visualorder :
         
         filter = getFilterByHeader(header)
         
         if (filter != None) :
            sorted.append(filter)
      return(sorted) 
   
   #Save the user's preferences to their pref file.
   def SaveChanges(self) :
      prefs = getManager().getPrefs()
      if (not 'filters' in prefs) :
         prefs['filters'] = {}
      
    
      
      for filter in getManager().getFilters() :
         
         filtername = filter.getName()
         prefs['filters'][filtername] = filter.saveFilter()
    
   #Don't need this method since changes are applied immediately.
   def applyChanges(self) :
      pass
   
   #Called when the dialog has been RE-opened.
   def reset(self) :
     
      #Remove the filter buttons
      self.RemoveFilterWidgets()
      #Add them back in visible column order
      self.filterwidget = self.AddFilterWidgets()
      #Add the new widget to the layout
      self.layout.addWidget(self.filterwidget)
      #Replace the removebutton
      self.layout.addWidget(self.removebutton)
      #Configure all of the buttons
      self.configureDialog()

   #Add a button for each available filter
   def AddFilterWidgets(self) :
      #Empty out the filter button list, since we keep creating
      #new ones.
      self.filterbuttons = []
      
      
      #The filterbuttons are associated with another widget
      widget = QtWidgets.QWidget()
      filterlayout = QtWidgets.QHBoxLayout()
      filterlayout.setSpacing(1)
      widget.setLayout(filterlayout)
      filterlayout.setAlignment(Qt.AlignCenter)
      for filter in self.SortFilters() :
         headeronly = filter.getProperty('headeronly')
         if (headeronly == None or not headeronly) :
            filterwidget = FilterButton(filter,widget)
            filterlayout.addWidget(filterwidget,Qt.AlignCenter)      
            self.filterbuttons.append(filterwidget)
      return(widget) 
   
#A button that displays the filter menu.
class FilterButton(QtWidgets.QPushButton) :
   def __init__(self,filter,parent,*args,**kwargs) :
      filtername = filter.getName() 
      if (filtername == "timestamp") :
         filtername = "timespan"
      super(FilterButton,self).__init__(filtername,parent) 
      
     # self.setFixedWidth(15)
      #return
      
      self.filter = filter
      self.parent = parent
      
      layout = QtWidgets.QVBoxLayout()          
      self.setLayout(layout)
      self.clicked.connect(
         lambda checked : self.ShowFilterMenu(checked,filter))
      
      self.icon = QtGui.QIcon("funnel--plus.png")
      self.configureDialog()
      
   #Create a filternmenu and display it.
   def ShowFilterMenu(self,checked,filter) :
      if (isinstance(filter,ExclusiveFilter)) :
         menu = ExclusiveFilterMenu(filter)
      else :
         menu = FilterMenu(filter)
      menu.exec_(self.mapToGlobal(self.parent.pos()))
     # return(menu)
   
   #If filter is applied, the filter button will have the filter icon
   def configureDialog(self) :
      filter = self.filter      
      filtered = filter.isFiltered()
      
      if (filtered) :
         self.setIcon(self.icon)
      else :
         self.setIcon(QtGui.QIcon());

class DefaultRowPrefs(PrefGroupBox) :
   """ Allows user to limit then number of rows """
   def __init__(self,parent,*args,**kwargs) :
      super(DefaultRowPrefs,self).__init__("Display Rows",parent)
           
      self.parent = parent
     
      #Each filter will have a button that will need to be configured
      self.filterbuttons = []
      
      #Create an exclusive button group.
      #...more than one of the radiobuttons cannot be selected at once
      #Have to have buttongroup as a member of the group box (self),
      #or method will not recognize it.
      self.buttongroup = QtWidgets.QButtonGroup()

      
      #This set of prefs has two associated filters. 
      layout = QtWidgets.QHBoxLayout()
      self.setLayout(layout) 
      self.layout = layout
      layout.setSpacing(50)
      self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
       
      #Widget that contains a button for each filter
      filterwidget = self.AddFilterWidgets()
      layout.addWidget(filterwidget)
      self.filterwidget = filterwidget
      
   def AddFilterWidgets(self) :
      
      #Empty out the filter button list, since we keep creating
      #new ones.
      self.filterbuttons = []
      
      
      #The filterbuttons are associated with another widget
      widget = QtWidgets.QWidget()
      filterlayout = QtWidgets.QHBoxLayout()
      filterlayout.setSpacing(1)
      widget.setLayout(filterlayout)
      filterlayout.setAlignment(Qt.AlignCenter)
      
      nolimits = QtWidgets.QRadioButton('All')  
      filterlayout.addWidget(nolimits) 
      self.buttongroup.addButton(nolimits)

      countfilter = getFilterByHeader('name')
      filterwidget = CountLimit(countfilter,widget)
      filterlayout.addWidget(filterwidget)
      self.buttongroup.addButton(filterwidget.countlimit)
      self.filterbuttons.append(filterwidget)
      
      return(widget)
      
      
      """
   
      for filter in self.SortFilters() :
         print(filter)
         break
         headeronly = filter.getProperty('headeronly')
         if (headeronly == None or not headeronly) :
            filterwidget = FilterButton(filter,widget)
            filterlayout.addWidget(filterwidget,Qt.AlignCenter)      
            self.filterbuttons.append(filterwidget)
      return(widget) 
      
      
      """
class CountLimit(QtWidgets.QWidget) :
   def __init__(self,filter,parent,*args,**kwargs) :
      super(CountLimit,self).__init__(parent)
      
      self.filter = filter
     
      layout = QtWidgets.QHBoxLayout()
      layout.setSpacing(4)
      self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Preferred)
      
      self.setLayout(layout)
      #Limit to X alarms
      countlimit = QtWidgets.QRadioButton("Limit to")
      layout.addWidget(countlimit)
      self.countlimit = countlimit

       
      countval = QtWidgets.QLineEdit()
      countval.setAlignment(Qt.AlignRight)
      countval.returnPressed.connect(self.trigger)
      countval.setFixedWidth(45)
      countvalidator = QtGui.QIntValidator()
      countvalidator.setBottom(0)
      countval.setValidator(countvalidator)
      layout.addWidget(countval)
      self.countval = countval
      
      alarmlabel = QtWidgets.QLabel("Alarms")
      alarmlabel.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Preferred)
      layout.addWidget(alarmlabel)
  
   
   def getRadioButton(self) :
      return(self.countlimit)
   
   def getMaxTextEdit(self) :
      return(self.countval)
      
   def configAllOption(self) :
      return
   
   def trigger(self,checked=None) :
      
      #The sender will be the checkbox from which the signal came
      sender = self.sender()  
      value = sender.text()    
      #Actually set the filter 
      self.filter.setFilter('max',value)
 
      #Redetermine the value of the "all" option
      self.configAllOption()
      
      #Set the column header based on the new state
      self.filter.setHeader()
   



#Section of prefdialog dealing with sorting preferences.      
class SortPrefs(QtWidgets.QGroupBox) :
   def __init__(self,parent,*args,**kwargs) :
      super(SortPrefs,self).__init__("Default Sort",parent)
      
      getManager().setGroupBoxStyle(self)
      self.prefs = getManager().getPrefs()
      layout = QtWidgets.QHBoxLayout()
      self.setLayout(layout)
      
      label = QtWidgets.QLabel("Sort By:")
      label.setFixedWidth(50)
      layout.addWidget(label)
      layout.setSpacing(5)
               
      #combo box with all headers
      self.combo = QtWidgets.QComboBox()
      layout.addWidget(self.combo)
      
      #Create an exclusive button group.
      #...two of the radiobuttons cannot be selected at once
      #Have to have buttongroup as a member of the group box (self),
      #or method will not recognize it.
      self.buttongroup = QtWidgets.QButtonGroup()
      
      #Sort ascending direction
      sortacscending = QtWidgets.QRadioButton()
      sortacscending.setIcon(QtGui.QIcon("sort-alphabet.png"))
      sortacscending.setFixedWidth(50)

      sortacscending.clicked.connect(self.SelectSortOrder)
      layout.addWidget(sortacscending) #add the radiobutton to the layout!
      
      #Add it to the buttongroup. Button group is NOT a widget
      self.buttongroup.addButton(sortacscending)
      self.sortacscending = sortacscending
      
      #Now the descending option
      sortdescending = QtWidgets.QRadioButton()
      sortdescending.setIcon(QtGui.QIcon("sort-alphabet-descending.png"))
      sortdescending.setFixedWidth(50)
    
      sortdescending.clicked.connect(self.SelectSortOrder)
      layout.addWidget(sortdescending)
      self.buttongroup.addButton(sortdescending)
      self.sortdescending = sortdescending
      
      #Fill the combo box with the header options
      self.FillCombo()
      self.configureDialog()
      self.combo.currentIndexChanged.connect(self.applyChanges)
   
   #Fill the combo with the sortoptions         
   def FillCombo(self) :
      combo = self.combo
      
      #Clear the combo box out. 
      #We will fill it up in the visible order of the column headers
      combo.clear()
      
      #Get the headers (in visible order)
      options = getModel().visibleColumnOrder()
     
      #Add the current sort column as the combo box value    
      header = self.CurrentSortOption()
      options.insert(0,header.lower())
      
      #Add each option to the combo box
      for option in options :
         combo.addItem(option) 

   #Configure the section
   def configureDialog(self) :
      #What is the column currently being used to sort?        
      currentsort = getProxy().sortColumn()
      
      #Ascending or descending? 
      currentorder = getProxy().sortOrder()
      self.sort = currentorder
      if (currentorder == 1) :
         self.sortdescending.setChecked(True)
      else :
         self.sortacscending.setChecked(True)
  
   #Which header is currently being used to sort?
   def CurrentSortOption(self) :
      sortcolumn = getProxy().sortColumn()
      
      #return the header text for the column
      sortoption = getModel().headerData(sortcolumn,Qt.Horizontal,Qt.DisplayRole)      
      return(sortoption)
   

   #Get the column number that is being used to sort.
   def GetSortColumn(self) :
      sortby = self.combo.currentText().lower()    
      sortcolumn = getModel().getColumnIndex(sortby)    
      return(sortcolumn)  

   #Add this preference widget's properties to the 
   #managerprefs to be saved
   def SaveChanges(self) :
      prefs = getManager().getPrefs()
      
      prefs['sort'] = {}
      prefs['sort']['column'] = self.GetSortColumn()
      prefs['sort']['order'] = self.sort
    
   #Called when user selects a sort column from the combo box
   def applyChanges(self) :
      #Column number
      sortcolumn = self.GetSortColumn()
      #Sort order
      sortorder = self.sort
      
      #Request table to sort by column
      if (sortcolumn != None and sortorder != None) :
         getTable().sortByColumn(sortcolumn,sortorder)
      

   #Called when the user selects a sort order radiobutton
   def SelectSortOrder(self) :
      sort = 0
      button = self.buttongroup.checkedButton()      
      if (button == self.sortdescending) :
         sort = 1
      self.sort = sort      
      self.applyChanges()
   

   #All preferences sections have a Reset method.
   #For the "Sort Preferencses" section, we want to fill up the 
   #combo list in the same order as the columns
   def reset(self) :      
     
      self.FillCombo()
      self.configureDialog()
      

#The widget from which the user can decide which columns to display
#and which to hide
class DisplayPrefs(QtWidgets.QGroupBox) :
   def __init__(self,parent, *args,**kwargs) :
      super(DisplayPrefs,self).__init__("Display Columns",parent)      
      
      getManager().setGroupBoxStyle(self)
      #Using a gridlayout, so will keep track of the rows.
      self.row = None
      self.showlist = []
      self.prefs = getManager().getPrefs()
      
      self.parent = parent 
      
      layout = QtWidgets.QGridLayout()
      layout.setHorizontalSpacing(5)
      layout.setVerticalSpacing(0)
      layout.setColumnStretch(0,0)
      self.setLayout(layout)
      self.layout = layout
      
      #Store the listwidgets for the Show and Hide options.
      self.options = {}
              
      #The "Show" option default is all of the columns in the table.
      #But, user may have set "show/hide" preferences
      self.DisplayOptions("Show")            
      
      #Hide listwidget is empty by default (unless user has set prefs)
      self.DisplayOptions("Hide") 
      
      #Put the column headers in the correct boxes.
      self.FillDisplayBoxes()
   
   #All preferences sections have a Reset method.
   #For the "Display Columns" section, we want to fill up the 
   #Show List Widget in the same order as the columns
   def reset(self) :
      self.FillDisplayBoxes()
   
   #Fill the Show/Hide display boxes with the appropriate columns
   def FillDisplayBoxes(self) :
      #The current set of columns to show and hide
      (showlist,hidelist) = self.GetDisplayOptions()
 
      self.FillBox('show',showlist)
      self.FillBox('hide',hidelist)
      
   #Fill the box, in list order
   def FillBox(self,option,list) :
      
      #The display listwidget
      optionlist = self.options[option]
      
      #Clear out the display options
      optionlist.clear()
      
      #Add the items to the listwidget
      for item in list :
         QtWidgets.QListWidgetItem(item,optionlist)

   #Get the list of properties available to show, in the
   #current column order.  
   def GetDisplayOptions(self) :
      
      #The horizontal header for our table model
      horizheader = getTable().horizontalHeader()
      
      showlist = []
      hidelist = []
      for col in range(getModel().columnCount(0)) :        
         
         #The "visualindex" is the column index that the user 
         #is actually seeing. We want to move the visual index
         #if the user changes the order in the "show" box.
         visualindex = horizheader.visualIndex(col)
         
         #Get the header text for this column
         header = getModel().headerData(col,Qt.Horizontal,Qt.DisplayRole)
         #if the section is NOT hidden, add it to the showlist.
         #if hidden, add it to the hidelist
         if (not getTable().horizontalHeader().isSectionHidden(col)) :
            showlist.insert(visualindex,header.lower())
         else :
            hidelist.insert(visualindex,header.lower())
      
      #return the results.     
      return(showlist,hidelist)
   
      
   #This a row with a label (Show/Hide) and an associated listbox
   def DisplayOptions(self,text) :      
      row = nextRow(self)
      
      #The label, in column 0
      label = QtWidgets.QLabel(text)
      self.layout.addWidget(label,row,0)
      
      #The drag and drop listbox
      dragwidget = DragWidget(self)
      self.layout.addWidget(dragwidget,row,1) 
      
      #Assign the widget to the "options" dictionary
      self.options[text.lower()] = dragwidget
       
   
   #What properties are in the "Show" or "Hide" list widget, 
   #when "Apply" is pressed
   def GetDisplayList(self,forwhat) :
      list = []
      options = self.options[forwhat]
      for option in range(options.count()) :
         item = options.item(option)
         text = item.text()
         list.append(text)
      return(list)
   
   #Add this preference widget's properties to the 
   #managerprefs to be saved
   def SaveChanges(self) :
      #Which properties to show, and which to hide.
      prefs = getManager().getPrefs()
      prefs['display'] = {}
      prefs['display']['show'] = self.GetDisplayList("show")
      prefs['display']['hide'] = self.GetDisplayList("hide")
      
   #Called when the "Apply" button on the preferences dialog 
   #is pushed.
   def applyChanges(self) :
      #Which properties to show, and which to hide.
      hidelist = self.GetDisplayList("hide")
      showlist = self.GetDisplayList("show")
      getModel().applyDisplayPrefs(showlist)
 
   def configureDialog(self) :
      pass
      
#The drag/drop listwidget.       
class DragWidget(QtWidgets.QListWidget) :
   def __init__(self,parent) :
      super(DragWidget,self).__init__(parent)
      
      #User can expand horizontally, but not vertically
      self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
         QtWidgets.QSizePolicy.Minimum)
      
      #Want horizontal listwidgets.
      self.setFlow(QtWidgets.QListView.Flow.LeftToRight)
      
      #Configure the drag and drop
      self.setDragEnabled(True)
      self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
      self.setDropIndicatorShown(True) 
      self.setDefaultDropAction(Qt.MoveAction)
      self.viewport().setAcceptDrops(True)
      
      #Allow user to select multiple items
      self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)     
      self.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
      
      #Spacing between items
      #self.setSpacing(2)
      
      self.setSpacing(getManager().prefSpacing())
      #fix the height or the listwidgets are too tall.
      self.setFixedHeight(50)
      
   
   #Override the widget's sizeHint. Want to make sure that
   #it is at least big enough to hold all of the column headers.
   def sizeHint(self) :
      num = self.count()
      #extra = num * 20
      extra = num * getManager().prefMultiplier()
      size = QtCore.QSize()
      height =1 
     
      width = super(QtWidgets.QListWidget,self).sizeHint().width()
      if (num > 0) :
         width = width + extra
      size.setHeight(height)
      size.setWidth(width)      
      return(size)