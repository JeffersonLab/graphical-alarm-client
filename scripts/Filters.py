from PyQt5 import QtCore, QtGui, QtWidgets

from jlab_jaws_helper.JAWSConnection import *

from utils import *

#Filter Objects used to sort and filter the model view
def getFilterByHeader(header) :
   """ Get the filter object by the column header
       Args:
         header : the column header text
   """
   #turn the header title into the same format as filter names.
   header = header.replace(" ","_")
      
   result = None
   filters = getManager().getFilters()
  
   #Iterate the the list.
   for filter in filters :     
      
      if (filter.getName() == header) :
         return(filter)
   return(result)


      
class Filter(object) :
   """ Abstract Filter Class 
   """
   def __init__(self,name=None,config=None,**kwargs) : 
      """ Create an instance
          Args:
            name : name of the filter (example "category")
            
      """
      #Filter's state
      self.filtered = False  #Has the filter been limited by ANY selections.
      
      #The name of the filter ("category")  
      self.options = None          #example: ['RF','BCM']
      self.optionstate = None      #example {'RF' : True, 'BCM' : False} True = show 
      self.filtername = name
      
      self.config = config #Filters can be made passing in a config dictionary
      self.debug = False
      
      #Initialize the set of options available
      self.updateOptions()
   
   def updateOptions(self) :
      """ Create the list of options for the filter
      """
      options = ['All']
      if ('empty' in self.config) :
         options.append('Empty')
      

      filteroptions = self.getOptions()
      
      options.extend(filteroptions)

      self.setFilterOptions(options)
      
      #Stores whether or not the option has been filtered
      self.optionstate  = self.initState()
 
   def initState(self) :
      """ Initialize each option as "True" 
      """     
      optionstate = self.getCurrentState()
      if (optionstate == None) :
         optionstate = {}
         for option in self.options :
            optionstate[option] = True    #optionstate['RF'] = True (check box is checked)
      return(optionstate)
   
   def getFilterOptions(self) :
     self.updateOptions()
     return(self.options)   
   
   
   def setFilterOptions(self,options) :
      self.options = options
   
   def getProperty(self,prop) :
      
      propval = None
      if (self.config != None and prop in self.config) :
         propval = self.config[prop]
      return(propval)  

   
   #Get the setting of a specific option in the filter
   def getOptionState(self,option) :
      """ Get the current state of the option" 
      """  
      optionstate = self.getCurrentState()
      if (optionstate == None) :
         
         return(True)
      checked = False
      if (option in optionstate) :
         val = optionstate[option]
         checked = val      
      return(checked)
  
   def setFilterState(self) :
      """If one option is filtered out, the filter is "filtered"
      """
      
      
      filtered = False
      if (not self.optionstate == None and len(self.optionstate) > 0) :
         for option in self.optionstate :
            val = self.getOptionState(option)
            if (val == 0) :
               filtered = True
               break
   
      self.filtered = filtered
   
   def setFilter(self,option,value) :      
      """ Applies the filter to the model
          Args:
            option : A filter choice (examples: [RF] [Injector])
            value  : Qt.checked or Qt.Unchecked
      """
      #Get the current setting configuration and set the option's
      #value as appropriate
      optionstate = self.getCurrentState()
      optionstate[option] = value
      
      #Warn the the proxymodel that something is going to change
      #and the table needs to redraw...and thus refilter
      getModel().layoutAboutToBeChanged.emit() 
      #Assign the new setting configuration
      self.setState(optionstate) 
      
      #Let the proxy model know we're done.
      getModel().layoutChanged.emit()  


   def getName(self) :
      """ Access the filter name (same as header column)
      """
      return(self.filtername)
   
   #Access the filter state
   def isFiltered(self) :
      """ Has this filter been applied? 
      """
      optionstate = self.getCurrentState()
      filtered = False
      if (optionstate != None) :
         for option in optionstate :
            if (optionstate[option] == False) :
               filtered = True
               break
      
      self.filtered = filtered
      
      return(self.filtered)
   
   #Get the filter's current optionstate
   def getCurrentState(self) :     
      """ The most recent state of the filter options
      """
      return(self.optionstate)
    
     
   def setState(self,optionstate) :
      """ Assign the optionstate (state of each option in filter)
      """ 
      self.optionstate = optionstate
      #Whenever the optionstate are set, determine the new
      #filter state
      self.setFilterState()
   
   
   def setHeader(self) :
      """ Determine whether or not we add the filter icon to
          the column header.
      """
      #Iterate through each option
      #If at least one options value is 0, filter is applied.
      #Display the filter icon on the header      
      optionstate = self.getCurrentState()     
      headerfilter = False
      if (not optionstate == None) :
         for prop in optionstate :
            if (optionstate[prop] == 0) :
               headerfilter = True
               break   
      
      #Call the model with the results
      getModel().configureHeader(self.getName(),headerfilter)   
     
      #Update the Manager's filter action on ToolBar      
      getManager().getRemoveFilterAction().setState()
 
   
   
   def selectAll(self,check) :
      """ Apply "check" to all filter options
          Args:
            check: option is checked (True/False)
      """
      for option in self.options :        
         self.setFilter(option,check)
      self.setHeader()      
      
     
   def getFilterVal(self,alarm) :
      """ Get the value of the alarm property associated
          with this filter
      """
      prop = self.getName()
      return(alarm.get_property(prop,name=True))
      

   def applyFilter(self,alarm) :
      """ Apply the filter to this alarm
          This is called by the model's "filterAcceptRow" method.
          Which compare the filter configuration to the alarm's value.
            Args:
               alarm : JAWSAlarm 
      """     
      #Assume we'll keep the alarm.
      keepalarm = True
      #Access the current configuration.
      optionstate = self.getCurrentState()
      if (optionstate == None) :
         return(True)
      #Go through each filter option
      for option in self.options :
         #Just in case, check that the option is in the 
         #optionstate configuration.
         if (option in optionstate) :
            #The desired state of the user. 
            state = optionstate[option]
 
            #If the state of the setting is 0 or False,
            #Need to check the alarm value.
            if (state == 0 or not state) :
               #access the value of the alarm
               alarmval = self.getFilterVal(alarm)

               #If user doesn't want "empty", and the alarmval is not set
               if (option.lower() == "empty" and alarmval == None) :
                  #Don't want the alarm
                  keepalarm = False
               elif (alarmval != None) :
                  #If the alarm has a value, compare it to the unwanted
                  #option, if it's the same, we will not keep the alarm
                  if (option.lower() == alarmval.lower()) :
                     keepalarm = False
         if (not keepalarm) :
            break
           
 
      #return the result.
      return(keepalarm)
    
   def reset(self) :
      """ Reset the options in the filter
      """
      pass
   
   def saveFilter(self) :
      """ Save the user's filter options
      """
      optionstate = {}
      for option in self.options :
         val = self.getOptionState(option)
         optionstate[option] = val
      return(optionstate)

   

   
   


class OverrideTypeFilter(Filter) :
   """ Filter on the alarm's OverrideType
   """

   def __init__(self,filtername='override_type',config=None) :
      super(OverrideTypeFilter,self).__init__(filtername,config)
      
   def getOptions(self) :
      """ Request list of override types from JAWS
      """
      return(get_override_types())
 
   
class OverrideReasonFilter(Filter) :
   """ Filter on the override reason         
   """
      
   def __init__(self,filtername='reason',config=None) :
      super(OverrideReasonFilter,self).__init__(filtername,config)
   
   def getOptions(self) :
      """ Request list of override reasons from JAWS
      """
      return(get_override_reasons())
      
   
class CategoryFilter(Filter) :
   """ Filter on the list of categories     
   """
   def __init__(self,filtername='category',config=None) :
      super(CategoryFilter,self).__init__(filtername,config)
      
   def getOptions(self) :
      """ Request list of categories from JAWS
      """
      
      return(get_category_list())
   

class LocationFilter(Filter) :
   """ Filter on the list of locations   
   """
   def __init__(self,filtername='location',config=None) :
      super(LocationFilter,self).__init__(filtername,config)
      
   #Get the valid locations from Kafka           
   def getOptions(self) :
      """ Request list of locations from JAWS
      """    
      return(get_location_list())   
      

class StatusFilter(Filter) :  
   """ Filter based on the current status of the alarm  
   """
   def __init__(self,filtername='status',config=None) :     
      super(StatusFilter,self).__init__(filtername,config)
      
      #Can't have an "Empty" alarm status
  #    self.options.remove("Empty")
   
   def getOptions(self) :
      #This list should be retrieved from JAWS.
      return(['LATCHED','MAJOR','ALARM','MINOR','NORMAL'] )
   
   #A little more processing on the return value.
   ### THIS MAY HAVE TO BE REVISITED ##      
   def getFilterVal(self,alarm) :
      #What's the state?
      state = alarm.get_state(name=True)
      val = alarm.get_sevr(name=True)      
      if ("latched" in state.lower()) :
         val = "LATCHED"      
      if ("normal" in state.lower()) :
         val = "NORMAL"
      
      return(val)
   
   
#Type of alarm (epics,nagios,smart)
class TypeFilter(Filter) :
   """ Filter on the type of alarm (epics,nagios,smart..)  
   """
   def __init__(self,filtername='type',config=None) :
      super(TypeFilter,self).__init__(filtername,config)
   
   def getOptions(self) :
      classlist = getManager().getProcessor().get_classname_list()
      
      #This list should be retrieved from JAWS.
      return(classlist)   
   
   def getFilterVal(self, alarm) :
      return(alarm.get_property('alarm_class',name=True))

#Alarm priority      
class PriorityFilter(Filter) :
   """ Filter on the alarms' priority of alarm
   """   
   def __init__(self,filtername='priority',config=None) :
      super(PriorityFilter,self).__init__(filtername,config)
            
   def getOptions(self) :
      """ Request list of priorities from JAWS
      """    

      return(get_priority_list())


   
      
      
class ExclusiveFilter(Filter) :
   def __init__(self,filtername=None,config=None) :
      super(ExclusiveFilter,self).__init__(filtername,config)
      
   def initState(self) :
      """ Initialize each option
          For a exclusive filter, if All = True -- all others are False
      """     
      optionstate = self.getCurrentState()
      
      if (optionstate == None) :
         optionstate = {}
         for option in self.options :
            state = False
            if (option.lower() == "all") :
               state = True       
            optionstate[option] = state  
      return(optionstate)
   
   def setFilterState(self) :
      """ If "All" is selected filterstate = False
      """
      filtered = False
      state = self.getOptionState("All")
      if (not state) :
         filtered = True
              
      self.filtered = filtered
      
   def selectAll(self,check) :
      """ No action necessary to set the "all state" for
          Exclusive filter
          But need to overload parent Filter
      """
      """ Apply "check" to all filter options
          Args:
            check: option is checked (True/False)
      """


      self.setFilter("All",check)
      checkothers = True
      if (check) :
         checkothers = False
      for option in self.options : 
         if (option.lower() != "all") :
            self.setFilter(option,checkothers)
      self.setHeader()      

      return
  
   
   def setHeader(self) :
      """ Determine whether or not we add the filter icon to
          the column header.
      """
      #Exclusive filter only depends on the state of the "All" options
      headerfilter = False
      
      allstate = self.getOptionState("All")
      if (not allstate) :
         headerfilter = True
      #Call the model with the results
      getModel().configureHeader(self.getName(),headerfilter)      
      #Update the Manager's filter action on ToolBar      
      getManager().getRemoveFilterAction().setState()
    
   def applyFilter(self,alarm) :
      """ Apply the filter to this alarm
          This is called by the model's "filterAcceptRow" method.
          Which compare the filter configuration to the alarm's value.
            Args:
               alarm : JAWSAlarm 
      """     
      #Assume we'll keep the alarm.
      keepalarm = True
      #Access the current configuration.
      optionstate = self.getCurrentState()
      if (optionstate == None) :        
         return(True)
      
      #Go through each filter option
      for option in self.options :        
         #For a ExclusiveFilter, we only want the option that is "True"
         #optionstate configuration.
         if (option in optionstate) :
            #The desired state of the user. 
            state = optionstate[option]           
            if (not state) : 
               continue
            #If "All" is selected...keep all alarms.
            if (option.lower() == "all") :
               keepalarm = True
            else :
               #alarmval = self.getFilterVal(alarm)      
               keepalarm = self.keepAlarm(alarm,option)         
      return(keepalarm)
   
   #Access the filter state
   def isFiltered(self) :
      """ Has this filter been applied? 
      """
      filtered = True
      allstate = self.getOptionState("All")
      if (allstate) :
         filtered = False
      self.filtered = filtered     
      return(self.filtered)

      
class RelativeTimeFilter(ExclusiveFilter) :
   def __init__(self,filtername='timestamp',config=None) :
      
      super(RelativeTimeFilter,self).__init__(filtername,config)
   
   def getOptions(self) :
      """ Get the options to display the relative time filter
      """
      options = []
      for duration in QUICKDURATIONS :
         text = "< " + QUICKDURATIONS[duration]['text']
         options.append(text)      
      return(options)
   
   def getFilterVal(self, alarm) :
      val =  alarm.get_state_change()
      return(val)

   def keepAlarm(self,alarm,option) :
      keepalarm = True
      
      #If "All" is selected...keep all alarms.
      if (option.lower() == "all") :
         keepalarm = True
      else :
         alarmval = self.getFilterVal(alarm)      
              
         #If user doesn't want "empty", and the alarmval is not set
         if (option.lower() == "empty" and alarmval == None) :
            #Don't want the alarm
            keepalarm = False
               
         #Process the alarmval to see if it applies 
         elif (alarmval != None) :
            #QUICKDURATIONS has the a label, and number of seconds
            #for the option.
            for choice in QUICKDURATIONS :
               label = QUICKDURATIONS[choice]['text']
               filterseconds = QUICKDURATIONS[choice]['seconds']
               
               #Label may not be exact for options...but if
               #the label is in the option text, we found it.
               if (label in option) :
                  #What time is it now (unixseconds)
                  now = convert_timestamp(int(time.time()) * 1000).timestamp()
                  #The alarm's timestamp in unixseconds
                  alarmseconds = alarmval.timestamp()
                  diff = now - alarmseconds
                  #Keep the alarm if the alarm timestamp is LESS than the
                  #number of seconds associated with the option 
                  if (diff <= filterseconds ) :
                     keepalarm = True
                  else :
                     keepalarm = False
      return(keepalarm)
                        
      
class CountFilter(Filter) :
   def __init__(self,name='name',config=None) :
      super(CountFilter,self).__init__(name,config)
   
      self.hiderows = False
   
   def getFilterVal(self,alarm) :
      
      data = getModel().data
      alarmindex = data.index(alarm)
        
         
      #vertheader = getTable().verticalHeader()
      #The number of rows that are currently VISIBLE
      wantrows = 2
  #    print("GETFILTER VAL",self.hiderows)
    #  visiblerows = vertheader.count()
      for row in reversed(range(getModel().rowCount(0))) :
       #  if (not self.hiderows) :
        #    getTable().setRowHidden(row,False)
         if (row >= wantrows) :
            
            getTable().setRowHidden(row,True)
         else :
            getTable().setRowHidden(row,False)
      
      return
 
      
   def keepAlarm(self,alarm,option) :
      keepalarm = True
      
      #If "All" is selected...keep all alarms.
      if (option.lower() == "all") :
         keepalarm = True
      else :
         alarmval = self.getFilterVal(alarm)      
              
         #If user doesn't want "empty", and the alarmval is not set
         if (option.lower() == "empty" and alarmval == None) :
            #Don't want the alarm
            keepalarm = False
               
         #Process the alarmval to see if it applies 
         elif (alarmval != None) :
            #QUICKDURATIONS has the a label, and number of seconds
            #for the option.
            for choice in QUICKDURATIONS :
               label = QUICKDURATIONS[choice]['text']
               filterseconds = QUICKDURATIONS[choice]['seconds']
               
               #Label may not be exact for options...but if
               #the label is in the option text, we found it.
               if (label in option) :
                  #What time is it now (unixseconds)
                  now = convert_timestamp(int(time.time()) * 1000).timestamp()
                  #The alarm's timestamp in unixseconds
                  alarmseconds = alarmval.timestamp()
                  diff = now - alarmseconds
                  #Keep the alarm if the alarm timestamp is LESS than the
                  #number of seconds associated with the option 
                  if (diff <= filterseconds ) :
                     keepalarm = True
                  else :
                     keepalarm = False
      return(keepalarm)

   def applyFilter(self,alarm,row) :
      """ Apply the filter to this alarm
          This is called by the model's "filterAcceptRow" method.
          Which compare the filter configuration to the alarm's value.
            Args:
               alarm : JAWSAlarm 
      """     
      #Assume we'll keep the alarm.
      keepalarm = True
      #Only need the "max" option value
      
   
      
  #    getModel().VisibleRowOrder()
      maxalarms = self.getOptionState('max')
      if (maxalarms == 0) :
         return(True)
      
      if (row >= int(maxalarms)) :
         return(False)
      
      return(True)
      
      optionstate = self.getCurrentState()
      if (optionstate == None) :        
         return(True)
      
      #Go through each filter option
      for option in self.options :        
         #For a ExclusiveFilter, we only want the option that is "True"
         #optionstate configuration.
         if (option in optionstate) :
            #The desired state of the user. 
            state = optionstate[option]           
            if (not state) : 
               continue
            #If "All" is selected...keep all alarms.
            if (option.lower() == "all") :
               keepalarm = True
            else :
               #alarmval = self.getFilterVal(alarm)      
               keepalarm = self.keepAlarm(alarm,option)         
      return(keepalarm)

   def setHeader(self) :
      """ Determine whether or not we add the filter icon to
          the column header.
      """
      #Exclusive filter only depends on the state of the "All" options
      headerfilter = self.isFiltered()
 
      #Call the model with the results
      getModel().configureHeader(self.getName(),headerfilter)      
      #Update the Manager's filter action on ToolBar      
      getManager().getRemoveFilterAction().setState()
   
   def selectAll(self,check) :
      """ 
      """
      self.resetFilter() 
 #     for option in self.options :        
  #       self.setFilter(option,check)
      self.setHeader()      

   def resetFilter(self) :
      #Reset optionstate when filter removed
      currentstate = self.getCurrentState()
      currentstate['max'] = 0
      self.setState(currentstate)
      return(currentstate)
      
   #Access the filter state
   def isFiltered(self) :
      """ Has this filter been applied? 
      """
      
      filtered = False
      maxrows = self.getOptionState("max") 
      if (int(maxrows) > 0) :
         filtered = True
      
      self.filtered = filtered
      
      return(self.filtered)
 
   #Get the filter's current optionstate
   def getCurrentState(self) :     
      """ The most recent state of the filter options
      """
      #CountFilter - 2 options "All" and 'max'
      #All = True, max = 0 or #All=False,max>0
      
      currentstate = self.optionstate
      if (currentstate == None) :
         return(currentstate)
      return(self.optionstate)
 
   def initState(self) :
      """ Initialize each option as "True" 
      """     
      optionstate = self.getCurrentState()
      if (optionstate == None) :
         optionstate = {}
         
         optionstate['max'] = 0
         
      
      return(optionstate)
   
   def getOptions(self) :
      options = {}
      options['max'] = 0
      return(options)

   def updateOptions(self) :
      """ Create the list of options for the filter
      """
      options = self.getOptions()
      self.setFilterOptions(options)
      
      #Stores whether or not the option has been filtered
      self.optionstate  = self.initState()

   
   def setFilter(self,option,value) :      
      
      """ Applies the filter to the model
          Args:
            option : A filter choice (examples: [RF] [Injector])
            value  : Qt.checked or Qt.Unchecked
      """
 
      if (option == "max" and value == True) :
         return
      
      #Get the current setting configuration and set the option's
      #value as appropriate
     
      optionstate = self.getCurrentState()
      
      optionstate[option] = value
      
      #Warn the the proxymodel that something is going to change
      #and the table needs to redraw...and thus refilter
      getModel().layoutAboutToBeChanged.emit() 
      #Assign the new setting configuration
      self.setState(optionstate) 
      
      #Let the proxy model know we're done.
      getModel().layoutChanged.emit()  
      

       

#Dependent on current table values
class DynamicFilter(Filter) :
   """ Filter that displays choices based on the content of the table
   """
   def __init__(self,filtername=None,config=None) :
      """ Create an instance
          ARGS:
            filtername : Name of the filter/column
      """
      super(DynamicFilter,self).__init__(filtername,config)
      
      self.filtername = filtername
  #    if ('Empty' in self.options) :
   #      self.options.remove("Empty")
      
      
   def getOptions(self) :
      """ Every time the filter is invoked, it will refresh
          the options
      """
      options = []
      alarmlist = GetAlarmList()
      
      for alarm in alarmlist :
         user = alarm.get_property(self.filtername)
         if (user != None and len(user) > 0) :
            if (not user in options) :
               options.append(user)
      
      return(options)
  
  
   def updateOptions(self) :
      """ Create the list of options for the filter
      """
     
      #All filters get an "Empty". In case the alarm 
      #has not been defined with the filtered property
     
      #The specific filter options ['RF','Misc','BPM']
      filteroptions = self.getOptions()
      self.options = filteroptions
      
      #Stores whether or not the option has been filtered
      self.optionstate  = {}    
      
      self.initState()
 
   def initState(self) :
      """ Initialize each option as "True" 
      """     
      
      optionstate = {}
      for option in self.options :
         optionstate[option] = True    #optionstate['RF'] = True (check box is checked)
      self.optionstate = optionstate
   
   def saveFilter(self) :
      return
      
   def reset(self) :
      
      
      """ Called whenever the filter's parent (dialog/context menu)
      """
      #All filters get an "Empty". In case the alarm 
      #has not been defined with the filtered property
  #    options = ["Empty"]
      
      
      
      #The specific filter options ['RF','Misc','BPM']
      filteroptions = self.getOptions()
      #Add this to "Empty"
          
      self.options = filteroptions      
      if (not self.isFiltered()) :
         #Whether or not the option is filtered out or not
         self.optionstate  = {}
      
         self.initState()


      
class SearchFilter(DynamicFilter) :
   def __init__(self,filtername=None,config=None) :
      super(SearchFilter,self).__init__(filtername,config)
      
      self.searchterm = ""
      
   def getSearchTerm(self) :
      return(self.searchterm)
      
      
   def getOptions(self) :
      pass
      alarmlist = getAlarmNames()
      return(alarmlist.sort())
      
   def updateOptions(self) :
      return(self.getOptions())
   
   def setSearchTerm(self,string) :
      
      self.searchterm = string
  #    print("SEARCHING FOR",self.searchterm)
   

   def isFiltered(self) :
      
      searchterm = self.getSearchTerm()
      if (len(searchterm) > 0) :
         filtered = True
      self.filtered = filtered
      return(filtered)
   
   def selectAll(self,check=None) :
      self.setSearchTerm("")
      self.setHeader()
      
   def setHeader(self) :
      """ Determine whether or not we add the filter icon to
          the column header.
      """
      headerfilter = self.isFiltered()
     # #Call the model with the results
      getModel().configureHeader(self.getName(),headerfilter)      
      #Update the Manager's filter action on ToolBar      
      getManager().getRemoveFilterAction().setState()
        


class NameFilter(SearchFilter) :
   def __init__(self,filtername='name',config=None) :
      super(NameFilter,self).__init__(filtername,config)
   
   def getOptions(self) :
      alarmnames = getAlarmNames()
      return(alarmnames)
   

   def isFiltered(self) :
      filtered = False
      searchterm = self.getSearchTerm()
      if (len(searchterm) == 0) :
         filtered = False
      else :
         filtered = False
         alarmnames = self.getOptions() 
         
         for name in alarmnames :
            
            keep = self.keepAlarm(name)
           
            if (not keep) :
               filtered = True
      self.filtered = filtered         
      return(filtered)
            
   def applyFilter(self,alarm) :
      return(self.keepAlarm(alarm))
      #searchterm = self.getSearchTerm()
   
   def keepAlarm(self,alarm) :
      alarmname = alarm
      if (not isinstance(alarm,str)) :
         alarmname = alarm.get_name()
     
      
      keepalarm = True
      
      searchterm = self.getSearchTerm()
      
      if (searchterm == None) :
         keepalarm = True
      elif (len(searchterm) == 0) :
         keepalarm = True
      elif (not searchterm.lower() in alarmname.lower()) :
         keepalarm = False      
      return(keepalarm)

class TriggerFilter(SearchFilter) :
   def __init__(self,filtername='trigger',config=None) :
      super(TriggerFilter,self).__init__(filtername,config)   
      
   def getOptions(self) :
      alarmnames = []
      alarmlist = GetAlarmList()
      for alarm in alarmlist :
         val = self.getFilterVal(alarm)
         if (val != None) :
            alarmnames.append(val)
      
      return(alarmnames)
   
   
   def isFiltered(self) :
      filtered = False
      searchterm = self.getSearchTerm()
      if (len(searchterm) == 0) :
         filtered = False
      
      else :
      
         filtered = False
         alarmlist = GetAlarmList() 
         for alarm in alarmlist :
            keep = self.keepAlarm(alarm)
           
         if (not keep) :
            filtered = True
         
      self.filtered = filtered
         
      return(filtered)
 
            
   def applyFilter(self,alarm) :
     
      return(self.keepAlarm(alarm))
 
   
   def keepAlarm(self,alarm) :
          
      searchterm = self.getSearchTerm()
      val = self.getFilterVal(alarm)
      
      keepalarm = True  
      if (len(searchterm) == 0) :
         return(True)
      
      if (val == None) :
         keepalarm = False
      elif (searchterm == None) :
         keepalarm = True
      elif (len(searchterm) == 0) :
         keepalarm = True
      elif (not searchterm.lower() in val.lower()) :
         keepalarm = False      
      return(keepalarm)


class UserFilter(DynamicFilter) :
   def __init__(self,filtername='overridden_by',config=None) :
      super(UserFilter,self).__init__(filtername,config)

   











           
