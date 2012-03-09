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
  '''
  def __init__(self, logFile):
    self.definitions()
    
    # import xml log file?
    self.logFile = xmllog.XmlLog(logFile, self.logEntryDef[:])
    
    # log file in array of entry objs form
    self.entryArray = self.getLog()

  def definitions(self):
    '''
    Method called by __init__ to define the fields users will have to input.  Designed to be overridden without having to reimplement __init__.
    '''
    # These must match the fields available in entry.ReportEntry
    # Title is currently dependent on group. Moving title before group in the list will break tab completion in the cli
    self.logEntryDef = [
        "date",
        "duration",
        "customer",
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
    print "INDEX ", index
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
    
  def getAnalysis(self):
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
    
    # List of days in the log
    days = []
    # Dictionary of dictionaries. Outer level has group keywords, inner dict has title keywords, values of inner dict are duration totals for that group-title combo
    titleTotals = {}
    # Dictionary of dictionaries, similiar to titleTotals.  Instead of totals, it has arrays of entry objects.
    details = {}
    # 
    groupTotals = {}
    
    for x in self.entryArray:
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