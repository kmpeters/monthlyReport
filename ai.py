#!/usr/bin/env python3

'''
Kevin's custom cli customizations:
  1. Reduced the group list to only those groups I actually use.
  2. Rearrange the order of the fields so that activity is prompted after the description is entered.
'''

import sys
import os

import pa
import log

from collections import namedtuple

Ignore = namedtuple("Ignore", "group title")
# >>> bcda = Ignore(None, None, ["email", "discussion"])
# >>> bcda
# Ignore(group=None, title=None, keyword=['email', 'discussion'])
# >>> bcda.group
# >>> bcda.title
# >>> bcda.keyword
# ['email', 'discussion']
# >>> 

class AICli(pa.PerfAppCli):
  def definitions(self):
    # Call base class method
    pa.PerfAppCli.definitions(self)
    
    # Re-add the save command, which was removed from PerfAppCli
    self.commands["save"] = self.saveLog
    self.commands["s"] = self.saveLog

    # Specify a list of groups, titles and keywords to ignore
    self.ignores = [Ignore("BCDA", ["email", "discussion", "misc", "training", "IT", "meetings", "feedback", "interviews"]),
      Ignore("19ID", "meetings"),
      Ignore("XSD", None),
      Ignore("Jira", None),
      Ignore("Training", None),
      Ignore("Leave", None)]
    
    self.outputFilename = "ai_work_log.xml"

  
  # Override the createReportLog function so that AILog is used instead of ReportLog
  def createReportLog(self, filepaths):
    # Don't create the log file here. Create it when the file is saved instead
    return AILog(filepaths) 
  
  # Override runMainLoop to allow handling multiple filenames
  def runMainLoop(self):
    # Get log filenames
    filepaths = self._getLogFilenames()
    
    if len(filepaths) > 0:
      self.run = True
      
      self.logObj = self.createReportLog(filepaths)
      self.logEntryDef = self.logObj.getLogEntryDef()
      
      # Run the main loop
      self.main()

  def _checkIgnore(self, e):
    '''
    Called when pruning the list of events before saving.
    '''
    retval = None
    
    for i in self.ignores:     
      if e.group != i.group:
        # This ignore rule doesn't apply to this event
        continue
      
      if i.title == None:
        # All events of a given title are being ignore
        retval = True
        break
      elif isinstance(i.title, list):
        # Compare event title to all ignored titles
        if e.title in i.title:
          retval = True
          break
        else:
          retval = False
      else:
        # Compare event title to ignored title
        if e.title == i.title:
          retval = True
          break
        else:
          retval = False
    
    return retval

  def saveLog(self, *args):
    '''
    Called when "save" or "s" is typed.  Causes the log to be saved and the dirty flag to be cleared.
    '''
    #!print("saveLog(", args, ")")
    
    # Check to see if the file exists
    if os.path.isfile(self.outputFilename):
      print("{} already exists! Cowardly refusing to do anything".format(self.outputFilename))
    else:
      eventsToKeep = []
      
      # It might be better to filter events when reading in the files, rather than at the time of saving, but this is a simpler approach for now.
      for e in self.logObj.entryArray:
        if not self._checkIgnore(e):
          #!print(e, e.group, e.title)
          eventsToKeep.append(e)
      
      # Create an empty xml file and the xml object with all the entries in it
      self.logObj.createLogFromEntries(self.outputFilename, eventsToKeep)
      
      # Actually save the entries to disk
      self.logObj.saveLog()

      # TODO: handle being called multiple times
    
    return True


class AILog(log.ReportLog):
  def __init__(self, logFiles):
    self.definitions()
    
    # Note: the ReportLog class also defines a logFile member, but that isn't needed here;
    #       all of the commands that use it have been removed.
    
    self.entryArray = []
    
    for logFile in logFiles:
      print("Reading {}".format(logFile))
      # Append the entries from each log file to the entry array
      self.entryArray += (self.createLogFileObj(logFile, self.logEntryDef[:])).convertLogToObjs()
      
  # Override the definition function to reduce the amount of data written to the json file
  def definitions(self):
    self.logEntryDef = [
        "date",
        "duration",
        "group",
        "title",
        "description"
      ]

    
if __name__ == '__main__':
  aiCli = AICli()
