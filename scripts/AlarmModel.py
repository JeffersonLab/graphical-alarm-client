"""
.. module:: AlarmModel
   :synopsis : ModelView for Active Alarms
.. moduleauthor:: Michele Joyce <erb@jlab.org>
"""
from JAWSModel import *


#AlarmModel contains the data to disaply in the JAWSTableView widget    
class AlarmModel(JAWSModel) :
   """ A JAWSModel to display active alarms
   """

   def __init__(self,data=None,parent = None, *args) :
      super(AlarmModel,self).__init__(data,parent,*args) 
      
   #Overloaded function that must be defined.      
   def data(self,index,role) :

      #The index (contains both x,y) and role are passed.  
      #The roles give instructions about how to display the model.
      row = index.row()
      col = index.column()
       
      
      if (role == Qt.TextAlignmentRole) : 
         return(Qt.AlignCenter)     
          
      alarm = self.data[row] 
      (sevr,latch) = self.getDisplay(alarm) 

      #Status display is a little more complex
      if (col == self.getColumnIndex('status')) :
         if (role == Qt.BackgroundRole) :
            if (latch != None) :
               return(GetQtColor(latch))
      
         if (role == Qt.DecorationRole) :
            image = GetStatusImage(sevr)
            if (image != None) :
               return(QIcon(image))
         
         if (role == Qt.DisplayRole) :
            if (sevr == None) :
               sevr = "ALARM"
            return(sevr)
      
      #Insert the appropriate information into the display, based
      #on the column. Column "0" is handled by the StatusDelegate 
      if role == Qt.DisplayRole :
         if (col == self.getColumnIndex('name')) :
            return(alarm.get_name())
               
         alarmprop = self.getColumnName(col)
         if (col == self.getColumnIndex('timestamp')) :
            timestamp = alarm.get_property('effective_state_change')
           
            if (timestamp != None) :
               return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         elif (col == self.getColumnIndex('type')) :
            
            return(alarm.get_property('alarm_class',name=True))
         else :
           
            val = alarm.get_property(alarmprop,name=True)
            return(val)

   def getDisplay(self,alarm) :
      """ Get the display for the status column.
          Note: The display is determined by the alarm and latching status
                well as the latching 
          Args:
            alarm : The alarm being displayed.
      """

      state = alarm.get_state(name=True)
      latching = alarm.get_latching()
      sevr = alarm.get_sevr(name=True)
  
        
        
      latch = None    
      if (latching) :
         if ("latched" in state.lower()) :
            latch = sevr
         
         elif(state.lower() == "normallatched") :
            latch = sevr
            sevr = "NO_ALARM"
         elif (state.lower() == "active") :
            latch = None
         
      return(sevr,latch)
  
       
class AlarmProxy(JAWSProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(AlarmProxy,self).__init__(*args,**kwargs)
      
   def getDisplay(self,alarm) :
      return(alarm.get_sevr(name=True))
     
   