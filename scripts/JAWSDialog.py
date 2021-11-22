from PyQt5.QtWidgets import *

from utils import *
from Actions import *


class JAWSDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super().__init__()
      
      print("CREATE JAWS")
      getManager().setDialogStyle(self)
      
      self.setModal(False)
      self.setSizeGripEnabled(True)
      self.setSizePolicy(
         QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
      
      self.prefwidgets = []
            
      getManager().setDialogStyle(self)
      
      self.setModal(False)
      self.setSizeGripEnabled(True)
      self.setSizePolicy(
         QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
            
      #List of preferences to apply
      self.prefwidgets = []
      
      #prefs in a vlayout    
      self.vlayout = QtWidgets.QVBoxLayout()
      print("DONE JAWS")
      

      