from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QMimeData

from utils import *
from Actions import *
      
#The Preferences Dialog widget
class PrefDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super().__init__()
      
      self.setModal(False)
      self.setSizeGripEnabled(True)
      self.setSizePolicy(
         QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
            
      #List of preferences to apply
      self.prefs = []
      
      #Allow the user to hide and display the columns that they want
      displaycolumns = DisplayColumnsBox(self)
      vlayout = QtWidgets.QVBoxLayout()
      vlayout.addWidget(displaycolumns)
      self.displaycolumns = displaycolumns
      
      self.prefs.append(displaycolumns)
      
      #The "apply" and "close" buttons.
      buttons = self.MakeButtons()
      vlayout.addWidget(buttons)
      self.setLayout(vlayout)
      self.layout().setAlignment(Qt.AlignTop)
      self.show()
   
   
   def Reset(self) :
      for pref in self.prefs :
         pref.Reset()      
   
   #The accessible buttons on the dialog
   def MakeButtons(self) :
      
      layout = QtWidgets.QHBoxLayout()
      widget = QtWidgets.QWidget()
      widget.setLayout(layout)
      
      acceptbutton = QtWidgets.QPushButton("Accept Changes")
      acceptbutton.clicked.connect(self.ApplyChanges)
      layout.addWidget(acceptbutton) 
      
      cancelbutton = QtWidgets.QPushButton("Close")
      cancelbutton.clicked.connect(self.Close)
      layout.addWidget(cancelbutton)
      return(widget)
   
   #Apply changes for each applicable section
   def ApplyChanges(self) :
      for pref in self.prefs :
         pref.ApplyChanges()
   
   #Close the dialog     
   def Close(self) :
      self.close()  

#The widget from which the user can decide which columns to display
#and which to hide
class DisplayColumnsBox(QtWidgets.QGroupBox) :
   def __init__(self,parent, *args,**kwargs) :
      super(DisplayColumnsBox,self).__init__("Display Columns",parent)      
      
      #Using a gridlayout, so will keep track of the rows.
      self.row = None
      self.showlist = []
      
      layout = QtWidgets.QGridLayout()
      layout.setHorizontalSpacing(5)
      layout.setVerticalSpacing(0)
      layout.setColumnStretch(0,0)
      self.setLayout(layout)
      self.layout = layout
      
      #Store the listwidgets for the Show and Hide options.
      self.options = {}
              
      #The "Show" option default is all of the columns in the table.
      self.DisplayOptions("Show")
      self.FillShowBox()
      
      #Hide listwidget is empty by default.
      self.DisplayOptions("Hide") 
   
   #All preferences sections have a Reset method.
   #For the "Display Columns" section, we want to fill up the 
   #Show List Widget in the same order as the columns
   def Reset(self) :
      self.FillShowBox()
   
   #Fill the "Show" listwidget with the properties that are 
   #shown, in the order they are shown      
   def FillShowBox(self) :
      
      #The "show" listwidget
      optionlist = self.options['show']
      
      #Clear out the "show options"
      optionlist.clear()
      
      #Fill it back up, with the list of properties shown,
      #in the VISIBLE column order
      list = self.GetShowOptions()      
      for item in list :
         QtWidgets.QListWidgetItem(item,optionlist)

   #Get the list of properties available to show, in the
   #current column order.  
   def GetShowOptions(self) :
      
      #The horizontal header for our table model
      horizheader = GetTable().horizontalHeader()
      
      list = []
      for col in range(GetModel().columnCount(0)) :        
         #The "visualindex" is the column index that the user 
         #is actually seeing. We want to move the visual index
         #if the user changes the order in the "show" box.
         visualindex = horizheader.visualIndex(col)
         
         #Get the header text for this column
         header = GetModel().headerData(col,Qt.Horizontal,Qt.DisplayRole)
         list.insert(visualindex,header.lower())
      return(list)
   
      
   #This a row with a label (Show/Hide) and an associated listbox
   def DisplayOptions(self,text) :      
      row = NextRow(self)
      
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
  
   #Called when the "Apply" button on the preferences dialog 
   #is pushed.
   def ApplyChanges(self) :
      
      #Which properties to show, and which to hide.
      hidelist = self.GetDisplayList("hide")
      showlist = self.GetDisplayList("show")
      
      #The horizontal header for our table model
      horizheader = GetTable().horizontalHeader()
      
      #The col, is the "logical" index for the model.
      #it's the one that stays constant, no matter what the 
      #user sees.
      for col in range(GetModel().columnCount(0)) :        
         #The "visualindex" is the column index that the user 
         #is actually seeing. We want to move the visual index
         #if the user changes the order in the "show" box.
         visualindex = horizheader.visualIndex(col)
         
         #Get the header text for this column
         header = GetModel().headerData(col,Qt.Horizontal,Qt.DisplayRole)
         
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
      GetModel().ConfigureColumns()
      
      #Force the manager to resize to the new size of the table.
      GetManager().SetSize()

      
     
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
      
      self.setSpacing(GetManager().PrefSpacing())
      #fix the height or the listwidgets are too tall.
      self.setFixedHeight(50)
      
   
   #Override the widget's sizeHint. Want to make sure that
   #it is at least big enough to hold all of the column headers.
   def sizeHint(self) :
      num = self.count()
      #extra = num * 20
      extra = num * GetManager().PrefMultiplier()
      size = QtCore.QSize()
      height =1 
     
      width = super(QtWidgets.QListWidget,self).sizeHint().width()
      if (num > 0) :
         width = width + extra
      size.setHeight(height)
      size.setWidth(width)      
      return(size)


