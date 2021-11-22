"""
.. module:: OverrideModel
   :synopsis : ModelView for Overridden Alarms
.. moduleauthor:: Michele Joyce <erb@jlab.org>
"""
from JAWSModel import *



class OverrideModel(JAWSModel) :
   def __init__(self,data=None,parent = None, *args) :
      super(OverrideModel,self).__init__(data,parent,*args) 

   def data(self,index,role) :
      row = index.row()
      col = index.column()
      
      if (role == Qt.TextAlignmentRole) :
         return(Qt.AlignCenter) 
      
      alarm = self.data[row]
      display = self.getDisplay(alarm) 
      
      if (col == self.getColumnIndex('status')) :
         if (role == Qt.DecorationRole) :
            image = GetStatusImage(display) 
            if (image != None) :
               return(QIcon(image))
            else :
               print("NO IMAGE FOR ",display)
      
      #Insert the appropriate information into the display, based
      #on the column. Column "0" is handled by the StatusDelegate
      if role == Qt.DisplayRole :
         if (col == self.getColumnIndex('status')) :
            #Does the alarm have a severity?
            
            if (display == None) :
               return            
            return(display)
         
         if (col == self.getColumnIndex('name')) :
            
            return(alarm.get_name())
         
         alarmprop = self.getColumnName(col)
         
         if ("date" in alarmprop or "expiration" in alarmprop) :
            val = alarm.get_property(alarmprop)
            if (val != None) :
               return(val.strftime("%Y-%m-%d %H:%M:%S"))
         
         elif ("left" in alarmprop) : 
            timeleft = alarm.get_property('timeleft')       
            return(self.displayTimeLeft(timeleft))
       
         
         else :
            val = alarm.get_property(alarmprop,name=True)
            
         return(val)
       
   def getDisplay(self,alarm) :
      display = "ALARM"
      state = alarm.get_state(name=True)
      
      if ("normal" in state.lower()) :
         display = "NORMAL"
     
      return(display)
   
   def displayTimeLeft(self,timeleft) :
      if (timeleft == None) :
         return("")
   
      seconds = timeleft.seconds
      days = timeleft.days
      
      displaytime = "" 
      if (days > 0) :
         displaytime = str(days) + " days "
      
      if (seconds < 60) :
         displaytime = displaytime + str(seconds) + " sec"
      elif (seconds > 60 and seconds < 3600) :
         minutes = '{:0.2f}'.format(seconds / 60)
         displaytime = displaytime + minutes + " min"
      
      elif (seconds > 3600 and seconds < 86400) :
         if (days > 0) :
            hours = str(int(seconds/3600))
            getTable().horizontalHeader().setSectionResizeMode(3,
               QtWidgets.QHeaderView.ResizeToContents)
         else :
            hours = '{:0.2f}'.format(seconds / 3600)
         displaytime = displaytime + hours + " hours"
      
      
      return(displaytime)
     
 class OverrideProxy(JAWSProxyModel) :
   def __init__(self,*args,**kwargs) :
      super(OverrideProxy,self).__init__(*args,**kwargs) 
   
   def getDisplay(self,alarm) :
      return(self.sourceModel().getDisplay(alarm))  
