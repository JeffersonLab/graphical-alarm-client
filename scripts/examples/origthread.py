import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRunnable,QThreadPool, \
   QTimer

from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QMainWindow,\
   QVBoxLayout, QLabel
   
import traceback

import time 


class WorkerSignals(QObject) :
   finished = pyqtSignal()
   error = pyqtSignal(tuple)
   result = pyqtSignal(object)
   progress = pyqtSignal(int)
   
class Worker(QRunnable) :
   def __init__(self,fn,*args,**kwargs) :
      super(Worker,self).__init__()
      self.fn = fn
      
      self.args = args
      self.kwargs = kwargs
      self.signals = WorkerSignals()
      
      self.kwargs['progress_callback'] = self.signals.progress
   def run(self) :
      try:
         
         result = self.fn(*self.args,**self.kwargs)
      except:
         traceback.print_exc()
         exctype,value = sys.exc_info()[:2]
         self.signals.error.emit((exctype,value,traceback.format_exc()))
      else :
         self.signals.result.emit(result)
      finally:
         self.signals.finished.emit()


class MainWindow(QMainWindow) :
   def __init__(self,*args,**kwargs) :
      super(MainWindow,self).__init__(*args,**kwargs)
      
      self.counter = 0
      layout = QVBoxLayout()
      self.l = QLabel("Start")
      b = QPushButton("DANGER")
      b.pressed.connect(self.oh_no)
      
      layout.addWidget(self.l)
      layout.addWidget(b)
      
      w = QWidget()
      w.setLayout(layout)
      
      self.setCentralWidget(w)
      self.show()
      
      self.threadpool = QThreadPool()
      self.timer = QTimer()
      self.timer.setInterval(1000)
      self.timer.timeout.connect(self.recurring_timer)
      self.timer.start()
   
   def progress_fn(self,n):
      print("%d%% done" %n )
   
   def execute_this_fn(self,progress_callback) :
      for n in range(0,5) :
         time.sleep(1)
         progress_callback.emit(n*100/4)
      return "Done"
      
   def print_output(self,s) :
      print(s)
   
   def thread_complete(self) :
      print("THREAD COMPLETE")
   
   def oh_no(self) :
      worker = Worker(self.execute_this_fn)
      worker.signals.result.connect(self.print_output)
      worker.signals.finished.connect(self.thread_complete)
      worker.signals.progress.connect(self.progress_fn) 
      
      self.threadpool.start(worker)
   
   def recurring_timer(self) :
      self.counter += 1
      self.l.setText("Counter: %d" % self.counter)
      
      
app = QtWidgets.QApplication([])
window = MainWindow()
app.exec_()
           
   