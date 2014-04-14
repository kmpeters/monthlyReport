#!/usr/bin/env python

########### SVN repository information ###########
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###########

'''
The heart of Kevin's monthly-report software.

Connects the interface to the log-file backend.
'''

import xmllog

class ReportLog:
  '''
  Class representing a monthly-report log.
  
  :param str logFile: file name
  :returns: ReportLog object
  :rtype: complex structure from :meth:`getLog()`
  
  .. alternate form, use when the "type" is more than one word
  ..  :param other: this is not used
  ..  :type other: list of **objects**
  '''
  def __init__(self, logFile):
    self.definitions()
    
    # import xml log file?
    self.logFile = self.createLogFileObj(logFile, self.logEntryDef[:])
    
    # log file in array of entry objs form
    self.entryArray = self.getLog()


  def createLogFileObj(self, logFile, logEntryDef):
    '''
    Method called by __init__ to create the log file instance. Designed to be overriden without having to reimplement __init__.
    '''
    return xmllog.XmlLog(logFile, logEntryDef)


  def definitions(self):
    '''
    Method called by __init__ to define the fields users will have to input.  Designed to be overridden without having to reimplement __init__.
    '''
    # These must match the fields available in entry.ReportEntry
    # Title is currently dependent on group. Moving title before group in the list will break tab completion in the cli
    self.logEntryDef = [
        "date",
        "duration",
        "activity",
        "group",
        "title",
        "description"
      ]

  def getLogEntryDef(self):
    '''
    Retuns the log entry definition list.  Called by user interfaces and file-writing modules.
    '''
    return self.logEntryDef[:]

  def _recursiveCollectLabels(self, ent, labels, struct, level=0):
    '''
    A recursive funtion is needed to hand the arbitrary number of levels.
    
    Creates dictionaries for the higher levels and populates the list at the lowest level.
    '''
    #!print ent, labels, struct, level
    getFun, setFun, verifyFun = ent.getFunctions(labels[level])
    label = getFun()
    
    numLabels = len(labels)
    lastIndex = numLabels - 1
    
    if level == lastIndex:
      if label not in struct:
    	struct.append(label)
    else:
      if level == lastIndex - 1:
    	if label not in struct:
          struct[label] = []
      else:
        if label not in struct:
    	  struct[label] = {}

      self._recursiveCollectLabels(ent, labels, struct[label], level+1)


  def collectLabels(self, labels):
    '''
    Collects the labels on entries from the work log.
    
    Returns nested dictionaries of labels, with lists at the lowest level.
    '''
    levels = len(labels)
    if levels == 1:
      struct = []
    else:
      struct = {}

    for x in self.entryArray:
      #!print x
      self._recursiveCollectLabels(x, labels[:], struct)
     
    return struct
        

  def collectGroups(self):
    '''
    Return a list of groups that already exist in the log.
    
    Used by high-level interfaces for tab-completion.
    '''
    groups = []
    # loop over all entries in the log
    for x in self.entryArray:
      if x.group not in groups:
        groups.append(x.group)

    return groups[:]
  

  def collectEntries(self, group, field):
    '''
    Return a list of responses to the prompt for field (choice for field are defined in self.logEntryDef) for entries matching the given group.  
    
    group and field are both strings.
    
    Used by high-level interfaces to tab-complete previously-entered titles based on the chosen group.
    '''
    entries = []
    # loop over all entries in the log
    for x in self.entryArray:
      getFun, setFun, verifyFun = x.getFunctions(field)
      # if the group of an entry matches the desired group...
      if group == x.group or group == "":
        entry = getFun()
	# ...and the text of the desired field isn't already in the list...
	if entry not in entries:
	  # add it to the list
	  entries.append(entry)

    return entries[:]

  def addEntry(self, entry):
    '''
    Method that actually calls the backend to add the entry.
    
    entry is an ReportEntry object.
    '''
    #!print entry
    self.logFile.addEntry(entry)
    # update the entry array
    self.entryArray = self.getLog()
    
  def getEntry(self, index):
    '''
    Returns a single ReportEntry object.
    
    index is an integer (numbering from 0)
    '''
    #!print "INDEX ", index
    return self.entryArray[index]

  def replaceEntry(self, index, entry):
    '''
    Tells the backend to replace the desired entry and updates the array of entries.
    
    index is an integer (numbered from 0)
    entry is a ReportEntry object
    '''
    # Sanity check, display the changed entry
    #entry.printEntry()
    
    self.logFile.replaceEntry(index, entry)
    # update the entry array
    self.entryArray = self.getLog()

  def changeTitle(self, changeList, tag=False):
    '''
    Execute a bulk title change.
    
    changeList is a list: [oldGroup, oldTitle, newGroup, newTitle]
    '''
    
    oldGroup, oldTitle, newGroup, newTitle = changeList
    
    for x in self.entryArray:
      if x.group == oldGroup and x.title == oldTitle:
        groupGetFun, groupSetFun, groupVerifyFun = x.getFunctions('group')
        titleGetFun, titleSetFun, titleVerifyFun = x.getFunctions('title')
	
	# Is it worth it to test to see if the group or title are different before setting?
	# Should a copy of the object be modified instead of the object itself?
	groupSetFun(newGroup)
	titleSetFun(newTitle)
	
	if tag == True:
	  descGetFun, descSetFun, descVerifyFun = x.getFunctions('description')
	  oldDesc = descGetFun()
	  newDesc = "(%s/%s) %s" % (oldGroup, oldTitle, oldDesc)
	  descSetFun(newDesc)
	
	# Actually replace the entry with the modified entry
        self.logFile.replaceEntry(int(x.index)-1, x)
	
    # update the entry array
    self.entryArray = self.getLog()

  def getLog(self):
    '''
    Tell the backend to update the array of entries.
    '''
    return self.logFile.convertLogToObjs()

  def getLogLength(self):
    '''
    Returns the number of entries in the log (Integer).  Useful when validating indices.
    '''
    return len(self.entryArray)

  def isValidIndex(self, index):
    '''
    Returns True if there is a log entry for the desired index.
    
    index is an integer (numbering from 1)
    '''
    logLength = self.getLogLength()
    if index > 0 and index <= logLength:
      valid = True
    else:
      valid = False
    return valid
    
  def getAnalysis(self, dayList=None):
    '''
    Do the analysis.
    
    Returns this tuple
    (details, groupTotals, titleTotals, recordedTotal, theoreticalHours, percent)
    
    ================  ===================================================================================
    variable          description
    ================  ===================================================================================
    detail            A dictionary of dictionaries. Outer dict keys are groups, inner dict
                      keys are titles, and values of inner dict are ReportEntry objects.
    groupTotals       A dictionary with keys that are groups. Values are recorded hours for that group.
    titleTotals       A dictionary of dictionaries. Outer dict keys are groups, inner dict
                      keys are titles, and values of inner dict are recorded hours for that title.
    recordedTotal     Total recorded hours
    theoreticalHours  Total theoretical hours assuming eight hours per day and at least one entry per day
    percent           recordedTotal / theoreticalHours * 100.0
    ================  ===================================================================================
    '''
    # Make sure there is something to analyze
    if self.getLogLength() == 0:
      #!print "There is nothing to analyze!"
      return None
    
    if dayList == None:
      entryList = self.entryArray
    else:
      entryList = []
      for x in self.entryArray:
        if x.date[-2:] in dayList:
	  entryList.append(x)
    
    if len(entryList) == 0:
      return None

    # List of days in the log
    days = []
    # Dictionary of dictionaries. Outer level has group keywords, inner dict has title keywords, values of inner dict are duration totals for that group-title combo
    titleTotals = {}
    # Dictionary of dictionaries, similiar to titleTotals.  Instead of totals, it has arrays of entry objects.
    details = {}
    # 
    groupTotals = {}

    for x in entryList:
    	# Count the days for total work-day calculation
	if x.date not in days:
	  days.append(x.date)
        
	if x.group not in titleTotals:
	  titleTotals[x.group] = {}
	  details[x.group] = {}
	  
	if x.title not in titleTotals[x.group]:
	  titleTotals[x.group][x.title] = 0.0
	  details[x.group][x.title] = []
	  
	numDuration = float(x.duration)
	
	details[x.group][x.title].append(x)
	titleTotals[x.group][x.title] += numDuration
	  
    #!print "titleTotals", titleTotals
    #!print "groupTotals", groupTotals

    groups = titleTotals.keys()
    groups.sort()
    
    # Compute group totals after all groups and titles have been collected.
    recordedTotal = 0.0
    for group in groups:
      titles = titleTotals[group].keys()
      titles.sort()
        
      # Loop over titles to get a group total
      groupTotal = 0.0
      for title in titles:
        groupTotal += titleTotals[group][title]
      
      groupTotals[group] = groupTotal
      recordedTotal += groupTotal

    # Compute theoretical work hours, assuming 8hr days and at least one entry for each work day
    workDays = len(days)
    theoreticalHours = workDays * 8.0
    percent = recordedTotal / theoreticalHours * 100.0
    
    # Not the best way to return the analysis.  In the future there should probably be an analysis class.
    return (details, groupTotals, titleTotals, recordedTotal, theoreticalHours, percent)

  def getDay(self, day):
    '''
    Returns info for a given day.
    
    day is a zero-padded, two-character string represting the day of the month.
    
    Returns the following tuple: (dayArray[:], dayHours, percentRecorded)
    
    ===============  =======================================================
    variable         description
    ===============  =======================================================
    dayArray         Array of ReportEntry objects matching the specified day
    dayHours         Total hours recorded for the specified day
    percentRecorded  Percent recorded, assuming an eight-hour day
    ===============  =======================================================
    
    '''
    # day is a zero padded string
    dayArray = []
    dayHours = 0.0
    percentRecorded = 0.0
    for x in self.entryArray:
      if day == x.date[-2:]:
        dayArray.append(x)
	dayHours += float(x.duration)
    percentRecorded = dayHours / 8.0 * 100.0
    
    return (dayArray[:], dayHours, percentRecorded)

  def getDaySummary(self, day):
    '''
    Returns summary for a given day.
    
    day is a zero-padded, two-character string represting the day of the month.
    
    Returns the following tuple: (dayArray[:], dayHours, percentRecorded)
    
    ===============  =======================================================
    variable         description
    ===============  =======================================================
    groups           Array of groups from the specified day
    totals           Dict of totals with groups as keys
    entries          Dict of lists of entries with groups as keys
    dayHours         Total hours recorded for the specified day
    percentRecorded  Percent recorded, assuming an eight-hour day
    ===============  =======================================================
    
    '''
    dayArray, dayHours, percentRecorded = self.getDay(day)

    dayArraySorted = sorted(dayArray, key=self._customSortKey)

    runTot = 0.0
    lastGroup = None
    groups = []
    totals = {}
    entries = {}
    
    for item in dayArraySorted:
      # Add the group to the group list
      if item.group not in groups:
	groups.append(item.group)
      
      # Keep a running total for the group
      if item.group not in totals:
        totals[item.group] = float(item.duration)
      else:
        totals[item.group] += float(item.duration)
	
      # Categories the entries
      if item.group not in entries:
        entries[item.group] = [item]
      else:
        entries[item.group].append(item)
        
    # [[group, hours, [entry1, entry2]], [], 
    return (groups[:], totals, entries, dayHours, percentRecorded)
    
  def _customSortKey(self, entry):
    '''
    Custom sort routine for entry objects
    '''
    return (entry.group, entry.title, entry.index)

  def printLog(self):
    '''
    Prints the entire log
    '''
    #log = self.logFile.convertLogToObjs()
    for x in self.entryArray:
      print ""
      x.printEntry()
    print ""

  def saveLog(self):
    '''
    Tell the backend to save the log file.
    '''
    self.logFile.save()
