#! /Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import sys

from PyQt5 import QtCore,  QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt


class DragWidget(QtWidgets.QListWidget) :
   def __init__(self,parent,total=None) :
      super(DragWidget,self).__init__(parent)
      
      self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
         QtWidgets.QSizePolicy.Minimum)
      
      #Want horizontal listwidgets.
      self.setFlow(QtWidgets.QListView.Flow.LeftToRight)
      
      #Here's the attempt to configure dragging.
      self.setDragEnabled(True)
      self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
      self.setDropIndicatorShown(True) 
      self.setDefaultDropAction(Qt.MoveAction)

      self.viewport().setAcceptDrops(True)
       
      self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
     
      self.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
      
      self.setSpacing(2)
      self.setFixedHeight(50)

   
   #An attempt to overload the dragEnterEvent
   def dragEnterEvent(self,event) :
      #Use the InternalMove if the source = the drop site
      if (event.source() is self):        
         return
         self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
         
      else :
         #And regular ol' DragDrop if not.
         self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
      
      super().dragEnterEvent(event)
         
   #def sizeHint(self) :
    #  num = self.count()
     # extra = num * 20
     # size = QtCore.QSize()
      #height =1 
      
     # width = super(QtWidgets.QListWidget,self).sizeHint().width()
      #if (num > 0) :
       #  width = width + extra
      #size.setHeight(height)
      #size.setWidth(width)
      #return(size)
 
      
class ExampleDemo(QtWidgets.QMainWindow) :
   def __init__(self) :
      super().__init__() 
      self.UiComponents()
      
      self.show()
      
   def UiComponents(self) :
      list_widget = QtWidgets.QListWidget(self)
      list_widget.setGeometry(50, 70, 150, 60)
      
      item1 = QtWidgets.QListWidgetItem("A")
      item2 = QtWidgets.QListWidgetItem("B")
      item3 = QtWidgets.QListWidgetItem("C")
      
      list_widget.addItem(item1)
      list_widget.addItem(item2)
      list_widget.addItem(item3)
      
      list_widget. setDefaultDropAction(Qt.MoveAction)
      list_widget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
      
class DragDemo(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super().__init__()
   
      layout = QtWidgets.QGridLayout()
      groupbox = QtWidgets.QGroupBox("Display Columns")
      groupbox.setLayout(layout)

      showlist = DragWidget(groupbox)     
      options = ['type','name','timestamp']
      itemlist = []
      for option in options :       
         item = QtWidgets.QListWidgetItem(option,showlist)
         itemlist.append(item)          
      layout.addWidget(showlist,0,0)
      
      hidelist = DragWidget(groupbox)
      layout.addWidget(hidelist,1,0)
      
      vlayout = QtWidgets.QVBoxLayout()
      vlayout.addWidget(groupbox)
      
      self.setLayout(vlayout)
      self.show()

 

class PrefDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super().__init__()
      
      self.setModal(False)
      self.setSizeGripEnabled(True)
      self.setSizePolicy(
         QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
      
      
      layout = QtWidgets.QGridLayout()
      layout.setHorizontalSpacing(5)
      layout.setVerticalSpacing(0)
      layout.setColumnStretch(0,0)
      groupbox = QtWidgets.QGroupBox("Display Columns")

      groupbox.setLayout(layout)
      
      stylesheet = "QGroupBox:title {font-style: bold; font-size: 30pt;}"
      groupbox.setStyleSheet(stylesheet)
      
      showlabel = QtWidgets.QLabel("Show")
      layout.addWidget(showlabel,0,0)
      
      showframe = DragWidget(groupbox)     
      options = ['type','name','timestamp']
      itemlist = []
      for option in options :       
         item = QtWidgets.QListWidgetItem(option,showframe)
         itemlist.append(item)          
      layout.addWidget(showframe,0,1)
      
      hidelabel = QtWidgets.QLabel("Hide")
      layout.addWidget(hidelabel,1,0)
      hideframe = DragWidget(groupbox)
      layout.addWidget(hideframe,1,1)
      
        
      vlayout = QtWidgets.QVBoxLayout()
      vlayout.addWidget(groupbox)
      
      self.setLayout(vlayout)
      self.layout().setAlignment(Qt.AlignTop)
      self.show()
   
   def CalcWidth(self) :
      return
      max = 0
      options = GetModel().columns
      for option in GetModel().columns :
         length = len(option)
         if (length > max) :
            max = length
      
      total = len(options) * max
      return(max,total)
      
      
      

class AppDemo(QWidget):
   def __init__(self):
      super().__init__()
      PrefDialog()
      return
      layout = QtWidgets.QHBoxLayout()
      layout.addWidget(DragWidget(self))
      layout.addWidget(DragWidget(self))
      self.setLayout(layout)
      
      #Capture ctrl-c for quitting.
      QtWidgets.QShortcut("Ctrl+C", self, activated=self.closeEvent)

      self.show()
      
   def closeEvent(self,event) :
      print("CLOSE")
      sys.exit(0)
   

app = QApplication(sys.argv)

demo = DragDemo() #AppDemo()
demo.show()

sys.exit(app.exec_())       