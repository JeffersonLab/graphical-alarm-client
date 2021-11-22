from PyQt5.QtWidgets import *

from utils import *
from Actions import *


class SearchDialog(QtWidgets.QDialog) :
   def __init__(self,parent=None,*args,**kwargs) :
      super().__init__()
      
      