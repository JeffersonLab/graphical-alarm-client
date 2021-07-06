from ModelView import *

#The model used with the OverrideManager.
class OverrideModel(ModelView) :
   def __init__(self,data=None,parent=None,*args) :
      super(OverrideModel,self).__init__(data,parent,*args)
      
      self.columnconfig['override date'] = 150
      self.columnconfig['exp date'] = 150
      self.columnconfig['reason'] = 250


   #Overloaded function that must be defined.      
   def data(self,index,role) :
      #The index (contains both x,y) and role are passed.  
      #The roles give instructions about how to display the model.
      row = index.row()
      col = index.column()
            
      #Center columns
      if (role == Qt.TextAlignmentRole) : 
         return(Qt.AlignCenter)
         
      #Insert the appropriate information into the display, based
      #on the column. 
      if role == Qt.DisplayRole :
         alarm = self.data[row] 
         
         #This is the expiration countdown
         if (col == self.GetColumnIndex("time left")) :
            timedisplay = self.DisplayTimeLeft(alarm)
            return(timedisplay)

         if (col == self.GetColumnIndex("name")) :
            
            return(alarm.get_name())
         
         if (col == self.GetColumnIndex("override date")) :
            timestamp = alarm.GetShelfTime()
            if (timestamp != None) :
               return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         
         if (col == self.GetColumnIndex("exp date")) :
            timestamp = alarm.GetShelfExpiration()
            if (timestamp != None) :
               return(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
         
         if (col == self.GetColumnIndex("category")) :
            return(alarm.get_category(name=True))
         if (col == self.GetColumnIndex("location")) :
            return(alarm.get_location(name=True))  
         if (col == self.GetColumnIndex("reason")) :
            return(alarm.GetShelfReason())
   
   #Figure out a pretty way to display the time left until
   #expiration  
   def DisplayTimeLeft(self,alarm) :
      
      #How much time left? A disabled alarm will not have alarm.timeleft 
      #defined
      timeleft = alarm.timeleft
      
      if (timeleft ==  None) :
         return("")
         
      #timeleft is a "datetime.timedelta" object.
      #From this object, we can get the number of seconds and days.     
      seconds = timeleft.seconds
      days = timeleft.days
      
      #displaytime = str(seconds) + " s"
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
            getManager().getTable().horizontalHeader().setSectionResizeMode(3,
               QtWidgets.QHeaderView.ResizeToContents)
         else :
            hours = '{:0.2f}'.format(seconds / 3600)
         displaytime = displaytime + hours + " hours"
      
      return(displaytime)

