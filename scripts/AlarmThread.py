import time 
import traceback
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRunnable

#NOTE ABOUT METHOD AND VARIABLE NAMES
# --- self.myvariable     -- variable for this application
# --- def MyMethod()      -- method implemented for this application
# --- def libraryMethod() -- method accessed from a python library


#Signals available from running worker.
#Must inherit from QObject, which can emit signals
class WorkerSignals(QObject) :
   output = pyqtSignal(object)
   
      
#worker thread (generic)    
class Worker(QRunnable) :
   def __init__(self,fn,delay = 0.5,*args,**kwargs) :
      super(Worker,self).__init__()
      
      #fn is the function in the GUI to call from the thread
      #In this case it is AlarmProcessor.GetAlarms()
      self.fn = fn
      self.delay = delay
      
      #Possible arguments
      self.args = args
      self.kwargs = kwargs
      self.running = True
      
      #Worker will emit a signal upon return from GUI call
      self.signals = WorkerSignals()
   
   def SetDelay(self,delay) :
      self.delay = delay   
   
   #The thread continues to run as long as the application is 
   #up. When user wants to quit, self.running is set to False 
   def run(self) :      
      while (self.running) :
         try :
            #Call the proscribed function
            result = self.fn(*self.args,**self.kwargs)
         except :
            traceback.print_exc()
         else :
            #emit the result. The GUI will pick up the result to process
            self.signals.output.emit(result)
         
         delay = self.delay  
         #Wait, and do it again
         time.sleep(delay)
   
   #Stop the thread   
   def Stop(self) :
      self.running = False
