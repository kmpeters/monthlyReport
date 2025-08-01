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
    self.ignores = [Ignore("BCDA", ["email", "discussion", "misc", "training", "IT", "meetings"]),
      Ignore("19ID", "meetings"),
      Ignore("XSD", None),
      Ignore("Jira", None),
      Ignore("Leave", None)]
  
  # Override the createReportLog function so that AILog is used instead of ReportLog
  def createReportLog(self, filepaths):
    return pa.PerfAppLog(filepaths) 
  
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
    
    eventsToKeep = []
    
    for e in self.logObj.entryArray:
      if not self._checkIgnore(e):
        print(e, e.group, e.title)
        eventsToKeep.append(e)
    
    # TODO:
    #   2. create the xmllog
    #   3. add all the entries to it
    #   4. save to a filename that doesn't conflict with the work log
    # TODO: handle being called multiple times
    
    return True

    
if __name__ == '__main__':
  aiCli = AICli()
