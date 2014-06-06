#!/usr/bin/env python

########### SVN repository information ###########
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###########

'''
A CLI (command-line interface) for Kevin's monthly-reporting package
'''

import sys
import os
import readline
import time
import datetime
import string
import textwrap
import os.path

import config
import entry
import log
import mkrep

#!import logging

# Log file is necessary for debugging tab-completion problems
#!LOG_FILENAME = 'completer.log'
#!logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

class ReportCli:
  '''
  The command-line interface class, which interacts with the log module.
  
  Known problems: groups with strings can only be tab-completed before the first space is typed.
  '''
  def __init__(self):
    # Remove '-' from delim list so entries with dashes tab-complete properly
    delims = readline.get_completer_delims()
    #!print ",".join(["%x" % ord(x) for x in delims])
    # Allow dashes to be included in tab-completed words. Spaces can't be handled here since they are word separators part of the time.
    new_delims = delims.replace("-",'')
    readline.set_completer_delims(new_delims)
    #!delims2 = readline.get_completer_delims()
    #!print ",".join(["%x" % ord(x) for x in delims2])

    self.commands = { 
         "help": self.displayHelp,
            "h": self.displayHelp,  
        "print": self.displayLog,
            "p": self.displayLog,
          "add": self.addEntry,
            "a": self.addEntry,
         "corr": self.correctEntry,
            "c": self.correctEntry,
           "ch": self.changeTitle,
          "day": self.displayDay,
            "d": self.displayDay,
         "wtab": self.displayWeekTable,
           "wt": self.displayWeekTable,
         "wsum": self.displayWeekSummary,
           "ws": self.displayWeekSummary,
         "wrep": self.displayWeekReport,
           "wr": self.displayWeekReport,
         "dsum": self.displayDaySummary,
           "ds": self.displayDaySummary,
         "save": self.saveLog,
            "s": self.saveLog,
         "exit": self.quit,
         "quit": self.quit,
            "q": self.quit,
          "sum": self.displaySummary,
         "psum": self.displayPercentSummary,
          "rep": self.displayReport,
         "prep": self.displayPercentReport,
         "list": self.listLabels,
            "l": self.listLabels,
          "xml": self.createReportXml,
        "mkrep": self.makePdfReport,
         }
    
    self.possibleActivities = config.possible_activities[:]
    self.possibleGroups = config.possible_groups[:]
    
    self.logFilename = "work_log.xml"
    self.terminalWidth = 132
    self.tabSize = 8
    self.showCorrectDefaults = False
    self.showCorrectDescLen = 40
    self.wrDateSort = True
    
    # Override the above definitions
    self.definitions()
    
    # Flag to continue prompting for commands
    self.run = True
    # Dirty flag to indicate unsaved changes
    self.dirty = False

    # Get log filename
    self.filepath, self.directory, self.filename = self._getLogFilename()

    if self.run == True:
      # Let the user know which file is being used
      print "Reading %s" % self.filepath
      # Read log file into persistent log object
      self.logObj = self.createReportLog(self.filepath)
      self.logEntryDef = self.logObj.getLogEntryDef()
      
      # Run the main loop
      self.main()


  def createReportLog(self, filepath):
    '''
    Method called by __init__ to create the ReportLog instance. Designed to be overriden without having to reimplement __init__.
    '''
    return log.ReportLog(filepath)


  def definitions(self):
    '''
    Method called by __init__ to define the default work log file name and allow commands to be added.  Designed to be overridden without having to reimplement __init__.
    '''
    pass


  def displayHelp(self, *args):
    '''
    Called when "help" or "h" is typed.  Prints a help message.
    '''
    #!print "displayHelp(", args, ")"
    print """
 Commands:
   print (p) [#] prints info from the log file (default=everything)
   save (s)         saves changes to the log file
   add (a)         adds an entry to the log file
   corr (c) [#]  corrects the specified entry (default=last)
   help (h)      displays this help
   day (d) [#]   prints list of entries for a given day (default=today)
   dsum (ds) [#] prints summary of entries for a given day (default=today)
   wtab (wt) [#] prints a table of hours in green-sheet format
   wsum (ws) [#] displays the week summary w/o details (hours)
   wrep (wr) [#] displays the week summary w/ details (hours)
   sum [cat]          displays the month summary w/o details (hours)
   psum [cat]         displays the month summary w/o details (percent)
   rep [cat]          displays the month summary w/ details (hours)
   prep [cat]         displays the month summary w/ details (percent)

   list [label ...] list the labels used in the log. Default labels are
                activity, group and title.

   xml                Generates a skeleton xml report in the same directory
                   as the work log. Categories and keywords in the work log
                correspond to titles and subjects in the xml report.  
                Details must be MANUALLY entered after examining output
                of the 'prep' command.
                
   mkrep        Converts an xml file into a pdf. Titles are optional 
                   and do not currently appear in the pdf.
                
   ch                Bulk title change. Make a BACKUP of your log before using
                   this feature, since it hasn't been extensively tested yet.
    """
    return True


  def _removeHistoryEntry(self):
    '''
    Remove an entry from the readline input history
    '''
    pos = readline.get_current_history_length()-1
    #!print "Removing %s from history, pos=%i" % (readline.get_history_item(pos+1), pos+1)
    readline.remove_history_item(pos)
    

  def makePdfReport(self, *args):
        '''
        Convert a report xml file into a pdf.
        
        Calls mkrep.makeReport()
        '''
        # Interpret empty directory as pwd
        if self.directory == '':
          directory = "."
        else:
          directory = self.directory
          
        # Create a list of xml files in the same directory as the work_log
        files = os.listdir(directory)
        xmlFiles = []
        #!print files
        for f in files:
          if f[-4:] == ".xml" and f != self.filename:
            xmlFiles.append(f)
        
        # Print xml files in the directory that aren't the work_log
        print "Found XML files:", ", ".join(xmlFiles)
        # Prompt user for desired xml file with autocomplete
        try:
          # Turn on tab complete
          readline.parse_and_bind("tab: complete")
          completer = _TabCompleter(xmlFiles[:])
          readline.set_completer(completer.complete)
                
          # Get xml file
          desiredXml = raw_input("XML file to convert: ")
                
          if desiredXml != '':
            self._removeHistoryEntry()
          else:
            #!print "You didn't specify a file, assuming you want dummy.xml"
            desiredXml = "dummy.xml"
                        
        # Catch KeyboardInterrupt to allow the user to exit the entry process
        except (KeyboardInterrupt, EOFError):
                print ""
                print "Aborting..."
                return True
        finally:
                # Restore main completer
                readline.set_completer(self.mainCompleter.complete)

        #!print "desiredXml", desiredXml

        # Verify that the file exists
        #!print "%s/%s" % (directory, desiredXml)
        fullFilePath = "%s/%s" % (directory, desiredXml)
        if os.path.exists(fullFilePath) == False:
                print "The desired xml file (%s) doesn't exist." % fullFilePath
                return True

        # Call mkrep.makeReport()
        status = mkrep.makeReport(fullFilePath)
        
        return True


  def createReportXml(self, *args):
    '''
    Method responsible for creating a skeleton xml report based on the work log.
    
    Calls mkrep.makeXml()
    '''
    #!print "createReportXml(", args, ")"
    analysis = self.logObj.getAnalysis()
    
    if analysis == None:
      print "! The log is empty."
      return True

    # Prompt user for desired filename (Assume just a filename, not a path)
    try:
      desiredFilename = raw_input("XML report filename: ")

      # Remove text entry from history
      if desiredFilename != "":
        self._removeHistoryEntry()

    # Catch Ctrl+c and Ctrl+d to allow the user to exit the entry process
    except (KeyboardInterrupt, EOFError):
      print ""
      print "Aborting..."
      return True
    
    # Use a default filename if it was left blank
    if desiredFilename == "":
      desiredFilename = "skeletonReport.xml"
    # Make sure file has xml extension
    fparts = desiredFilename.split(".") 
    if len(fparts) >= 2 and fparts[len(fparts)-1] == "xml":
      pass
    else:
      desiredFilename = desiredFilename + ".xml"
    # Abort rather than overwrite an existing file
    if os.path.exists("%s/%s" % (self.directory, desiredFilename) ):
      print "Can't write xml report.  %s/%s already exists." % (self.directory, desiredFilename)
      return True
        
    try:
      # Prompt user for their name
      fullName = raw_input("Your name: ")

      # Remove text entry from history
      if fullName != "":
        self._removeHistoryEntry()

    # Catch Ctrl+c and Ctrl+d to allow the user to exit the entry process
    except (KeyboardInterrupt, EOFError):
      print ""
      print "Aborting..."
      return True

    status = mkrep.makeXml(analysis, self.directory, desiredFilename, fullName)    

    return True


  def _recursiveDisplayLabels(self, struct, level=0):
    '''
    Display the labels used in the report
    '''
    #!print "Displaying stuff", struct
    indentStr = "   "
    if type(struct) is dict:
      keys = struct.keys()
      keys.sort()
      for k in keys:
        print indentStr * level + k
        self._recursiveDisplayLabels(struct[k], level+1)
    
    if type(struct) is list:
      for item in struct:
        print indentStr * level + item


  def listLabels(self, *args):
    '''
    Method to display the heirarchy of labels used for the entries in the log
    
    args is a tuple of the labels that defines the nesting used when displaying the results.
    '''
    #!print "listLabels(", args, ")"
    
    defaultLabels = ['activity', 'group', 'title']
    
    if args == ():
      labels = defaultLabels[:]
    else:
      # only include valid arguments
      labels = []
      for label in args:
        if label in self.logEntryDef:
          labels.append(label)
        else:
          print "! %s is not a valid label." % label

    #!print labels
    
    #!print "Listing the following:"
    print ""
    for i in range(len(labels)):
      print "   " * i + labels[i]
    
    if len(labels) != 0:
      struct = self.logObj.collectLabels(labels)
    
      print "---" * (len(labels) + 1 )
      self._recursiveDisplayLabels(struct)
      print ""
    
    return True
    

  def displayReport(self, *args):
    '''
    Method to display the summary with details in hours.
    
    args is an tuple of group strings to display. If no groups are specified, all groups are displayed.
    '''
    #!print "displayReport(", args, ")"
    analysis = self.logObj.getAnalysis()
    
    if analysis != None:
      self._displayAnalysis(analysis, True, False, False, args)
    else:
      print "! The log is empty."
    
    return True


  def displayPercentReport(self, *args):
    '''
    Method to display the summary with details in percents.
    
    args is an tuple of group strings to display. If no groups are specified, all groups are displayed.
    '''
    #!print "displayPercentReport(", args, ")"
    analysis = self.logObj.getAnalysis()
    
    if analysis != None:
      self._displayAnalysis(analysis, True, True, False, args)
    else:
      print "! The log is empty."
    
    return True


  def displaySummary(self, *args):
    '''
    Method to display the summary in hours.
    
    args is an tuple of group strings to display. If no groups are specified, all groups are displayed.
    '''
    #!print "displaySummary(", args, ")"
    analysis = self.logObj.getAnalysis()
    
    if analysis != None:
      self._displayAnalysis(analysis, False, False, False, args)
    else:
      print "! The log is empty."
    
    return True


  def displayPercentSummary(self, *args):
    '''
    Method to display the summary in percents.
    
    args is an tuple of group strings to display. If no groups are specified, all groups are displayed.
    '''
    #!print "displayPercentSummary(", args, ")"
    analysis = self.logObj.getAnalysis()
    
    if analysis != None:
      self._displayAnalysis(analysis, False, True, False, args)
    else:
      print "! The log is empty."
    
    return True


  def _displayAnalysis(self, analysis, verbose=False, percents=False, dateSort=False, desiredGroups=()):
    '''
    Method that actually displays the analysis
    '''
    #!print analysis
    details = analysis[0]
    groupTotals = analysis[1]
    titleTotals = analysis[2]
    recordedTotal = analysis[3]
    theoreticalHours = analysis[4]
    percent = analysis[5]
    
    groups = titleTotals.keys()
    groups.sort()
    
    partialGroupStr = ""
    groupsWithSpaces = []
    # Make sure desired group(s) exist when allowing group to be specified
    for desiredGroup in desiredGroups:
      if desiredGroup not in groups:
        #!print "! %s is not a valid group." % desiredGroup
        # word might be part of a group name with a space in it
        if len(partialGroupStr) == 0:
          partialGroupStr = desiredGroup
        else:
          partialGroupStr = partialGroupStr + " " + desiredGroup
          # Check to see if the string is now a valid group
          if partialGroupStr in groups:
            groupsWithSpaces.append(partialGroupStr)
            # reset the partialGroup string
            partialGroupStr = ""
      else:
        # When a desiredGroup is valid, reset the partialGroup string
        partialGroupStr = ""

    # Remove the individual words from the groupsWithSpaces from the list of desiredGroups
    desiredGroupList = list(desiredGroups)
    for groupWithSpaces in groupsWithSpaces:
      wordList = groupWithSpaces.split(" ")
      for word in wordList:
        desiredGroupList.remove(word)
      # Append the words that were just removed as a single string
      desiredGroupList.append(groupWithSpaces)

    #!print "desiredGroups", desiredGroups
    #!print "desiredGroupList", desiredGroupList
    #!print "groups", groups
    
    print ""
    for group in groups:
      if desiredGroups == () or group in desiredGroupList:
        titles = titleTotals[group].keys()
        titles.sort()
      
        # Print group total
        if percents == False:
          print "%5.2f %s" % (groupTotals[group], group)
        else:
          print "%4.1f%% %s" % (groupTotals[group] / recordedTotal * 100.0, group)
        
        # Loop over titles printing totals
        for title in titles:
          if percents == False:
            print "\t%5.2f %s" % (titleTotals[group][title], title)
          else:
            print "\t%4.1f%% %s" % (titleTotals[group][title] / recordedTotal * 100.0, title)
            
          if verbose == True:
            lastDate = ""
            for e in details[group][title]:
              if dateSort == False:
                # Use the old, monthly-report approach
                line = "\t\t%s ; %s ; %s ; %s" % (e.date, e.duration, e.activity, e.description)
                print textwrap.fill(line, width=(self.terminalWidth-14), subsequent_indent="\t\t")
                print ""
              else:
                # Indent based on date
                if lastDate != e.date:
                  print "\t\t%s" % e.date
                  lastDate = e.date
                # Include index instead of date
                line = "\t\t\t%s ; %s ; %s ; %s" % (e.index, e.duration, e.activity, e.description)
                print textwrap.fill(line, width=(self.terminalWidth-21), subsequent_indent="\t\t\t")
                print ""

    print ""
    
    if desiredGroups == ():
      # Print total hours, theoretical hours, and percent
      print "Recorded:", recordedTotal, "hrs" 
      print "Possible:", theoreticalHours, "hrs"
      print "Complete: %0.1f%%" % percent
      print ""


  def displayLog(self, *args):
    '''
    Called when "print" or "p" is typed.
    
    args is a tuple of index strings (numbers starting from 1).  If no indices are specified, the whole log is displayed.
    '''
    #!print "displayLog(", args, ")"
    if len(args) == 0:
      # Display the entire log
      self.logObj.printLog()
    else:
      # Display a specific item or specific items
      print ""
      
      for x in args:
        try:
          index = int(x)
          if self.logObj.isValidIndex(index):
            tempObj = self.logObj.getEntry(index-1)
            tempObj.printEntry()
          else:
            print "!", x, "is outside the valid index range."
        except ValueError:
          print "!", x, "is not a valid index (integer)."
          print ""
          continue
        
        print ""
    
    return True


  def displayDay(self, *args):
    '''
    Called when "day" or "d" is typed.
    
    args is a tuple of day strings.  If no days are specified, the current day is displayed.
    '''
    #!print "displayDay(", args, ")"
    if len(args) == 0:
      dArgs = (time.strftime("%d"),)
    else:
      dArgs = args

    print ""
      
    for x in dArgs:
      try:
        day = "%02i" % int(x)
        dayArray, dayHours, percentRecorded = self.logObj.getDay(day)
        
        print "selected day: %s" % x
        print ""
        
        for x in dayArray:
          # Should probably use the get() methods, but that adds overhead
          print "%s ; %s ; %s - %s ; %s ; %s" % (x.index, x.duration, x.group, x.title, x.activity, x.description)
          
        print ""
        print "Hours: %.2f" % dayHours
        print "Percent: %.1f%%" % percentRecorded
        print ""
      except ValueError:
        print "!", x, "is not a valid day (integer)."
        print ""
        continue
        
    return True


  def displayWeekReport(self, *args):
    '''
    Called when "wr" is typed.
    '''
    #!print "dayTest(", args, ")"

    if len(args) == 0:
      wArgs = self._getWeek(0)
    else:
      try:
        wArgs = ["%02i" % int(x) for x in args]
      except ValueError:
        print "Error: Days must be integers"
        return True

    print
    print "Selected days: %s" % " ".join(wArgs)

    analysis = self.logObj.getAnalysis(wArgs)
    
    #!print analysis
    
    if analysis != None:
      if self.wrDateSort == False:
        self._displayAnalysis(analysis, True, False, False)
      else:
        self._displayAnalysis(analysis, True, False, True)
    else:
      print "! No entries for selected day(s)."

    return True

  def displayWeekSummary(self, *args):
    '''
    Called when "ws" is typed.
    '''
    #!print "dayTest(", args, ")"

    if len(args) == 0:
      wArgs = self._getWeek(0)
    else:
      try:
        wArgs = ["%02i" % int(x) for x in args]
      except ValueError:
        print "Error: Days must be integers"
        return True

    print
    print "Selected days: %s" % " ".join(wArgs)

    analysis = self.logObj.getAnalysis(wArgs)
    
    #!print analysis
    
    if analysis != None:
      self._displayAnalysis(analysis, False, False, False)
    else:
      print "! No entries for selected day(s)."

    return True


  def displayDaySummary(self, *args):
    '''
    Called when "dsum" or "ds" is typed.
    
    args is a tuple of day strings.  If no days are specified, the current day is displayed.
    '''
    #!print "displayDaySummary(", args, ")"
    if len(args) == 0:
      dArgs = (time.strftime("%d"),)
    else:
      dArgs = args

    print ""
      
    for x in dArgs:
      try:
        day = "%02i" % int(x)
        groups, totals, entries, dayHours, percentRecorded = self.logObj.getDaySummary(day)
        
        print "selected day: %s" % x
        
        for group in groups:
          print ""
          print "%s: %s hours" % (group, totals[group])
          print ""
          
          for x in entries[group]:
            # Should probably use the get() methods, but that adds overhead
            line = "  %s ; %s ; %s - %s ; %s ; %s" % (x.index, x.duration, x.group, x.title, x.activity, x.description)
            print textwrap.fill(line, width=(self.terminalWidth), subsequent_indent="    ")
        
        print ""
        print "Hours: %.2f" % dayHours
        print "Percent: %.1f%%" % percentRecorded
        print ""
      except ValueError:
        print "!", x, "is not a valid day (integer)."
        print ""
        continue
        
    return True


  def _getWeek(self, num):
    '''
    Internal function to return current or previous weeks
    '''
    currentDate = datetime.date.today()
    dayOfMonth = currentDate.day
    # 0=monday
    dayOfWeek = currentDate.weekday()
    
    # current Monday DOM (Day Of Month) = dayOfMonth - dayOfWeek
    currentMonday = currentDate.replace(day=(dayOfMonth - dayOfWeek))
    
    weekTimeDelta = datetime.timedelta(7)
    
    # num is a negative number and weekTimeDelta is positive, which results in subtracting time
    desiredMonday = currentMonday + num * weekTimeDelta
    desiredMondayDOM = desiredMonday.day

    weekDayList = []

    for i in range(5):
      weekDayList.append( desiredMonday.replace(day=(desiredMondayDOM + i)).strftime("%d") )

    return weekDayList[:]


  def _calcTabs(self, max, group):
    '''
    '''
    # max / 8 + 1 = num tabs max group name uses
    # (len(group) / 8) + 1 = num tabs group name uses
    # (max / 8) - (len(group) / 8) + 1 = num tabs to add
    return ((max / 8) - (len(group) / 8) + 1)


  def displayWeekTable(self, *args):
    '''
    Called when "wt" is typed.  Prints a table with data for green sheets.
    
    args is a tuple of day strings.  If no days are specified, the current week is displayed.
    '''
    #!print "displayDaySummary(", args, ")"

    if len(args) == 0:
      wArgs = self._getWeek(0)
    else:
      try:
        wArgs = ["%02i" % int(x) for x in args]
      except ValueError:
        print "Error: Days must be integers"
        return True
    
    #!print wArgs
    
    wList = []
    for day in wArgs:
      #  groups, totals, entries, dayHours, percentRecorded = self.logObj.getDaySummary(day)
      wList.append(self.logObj.getDaySummary(day))
      
    #!print wList
    
    groups = []
    groupWeekTotals = {}
    weekHourTotal = 0.0
    # Collect groups and calculate totals
    for i in range(len(wList)):
      dayList = wList[i]

      weekHourTotal += wList[i][3]

      groupList = dayList[0]
      groupDayTotals = dayList[1]
      
      for group in groupList:
        if group not in groups:
          groups.append(group)
          groupWeekTotals[group] = groupDayTotals[group]
        else:
          groupWeekTotals[group] += groupDayTotals[group]

    groups.sort()
    #!print groups
    #!print groupWeekTotals

    # Find longest group name
    maxGroupLen = 0
    for group in groups:
      if len(group) > maxGroupLen:
        maxGroupLen = len(group)
    #!print "maxGroupLen", maxGroupLen

    ### Build hours table

    headString = "Group" + '\t' * self._calcTabs(maxGroupLen, "Group")
    separator =  "-----" + '\t' * self._calcTabs(maxGroupLen, "-----")
    totalStr = "Total" + '\t' * self._calcTabs(maxGroupLen, "Total")

    for i in range(len(wArgs)):
      headString += " %s\t" % wArgs[i]
      separator += "----\t"
      totalStr += "%0.2f\t" % wList[i][3]
    headString += "Total"
    separator += "-----"
    totalStr += "%0.2f" % weekHourTotal
 
    # Display first two rows
    print headString
    print separator

    # Build group rows
    for group in groups:
      grpStr = group[:]
      # Add fewer tabs for longer group names
      grpStr += '\t' * self._calcTabs(maxGroupLen, grpStr)

      for i in range(len(wList)):
        if group in wList[i][1]:
          grpStr += "%0.2f\t" % wList[i][1][group]
        else:
          grpStr += "\t"
        
      grpStr += "%0.2f" % groupWeekTotals[group]
      # Display group strings as they're built
      print grpStr

    # Display last two rows
    print separator
    print totalStr

    return True


  def _getUserInput(self, entry, requireInput=False):
    '''
    Internal routine responsible for prompting the user for input.  Returns a status of True unless the user aborts data entry with Ctrl+C.
    '''
    status = True
    skipRemainingInput = False
    # Loop over items in a entry
    for item in self.logEntryDef:
      #!print item
      # Get the get and set functions for this item
      getFun, setFun, verifyFun = entry.getFunctions(item)

      if requireInput == False and self.showCorrectDefaults == True:
        entryStr = getFun()
        if len(entryStr) > self.showCorrectDescLen:
          entryStr = entryStr[:self.showCorrectDescLen] + "..."
        promptStr = "%s [%s]: " % (item, entryStr)
      else: 
        promptStr = "%s: " % item
      
      # Set tab-complete based on which item is being input
      if item == 'activity':
        print "  Possible activities:   %s" % ", ".join(self.possibleActivities[1:])
        readline.parse_and_bind("tab: complete")
        completer = _TabCompleter(self.possibleActivities[:])
        readline.set_completer(completer.complete)
      if item == 'group':
        # Combine default groups (likely a subset of valid groups) with collected groups (possibly containing non-default, but still valid groups)
        #!print "  Used groups:   %s" % ", ".join(self.logObj.collectGroups())
        #!print "  Possible groups:   %s" % ", ".join(self.possibleGroups[1:])
        totalGroups = list(set(self.logObj.collectGroups()) | set(self.possibleGroups[:]))
        totalGroups.sort()
        print "  Possible groups:   %s" % ", ".join(totalGroups[1:])
        readline.parse_and_bind("tab: complete")
        #!completer = _TabCompleter(self.possibleGroups[:])
        completer = _TabCompleter(totalGroups)
        readline.set_completer(completer.complete)
      if item == 'title':
        #existingTitles = self.logObj.getElementList(item)
        existingTitles = self.logObj.collectEntries(entry.group, item)
        print "  Existing titles for %s:   %s" % (entry.group, ", ".join(existingTitles)) 
        readline.parse_and_bind("tab: complete")
        completer = _TabCompleter(existingTitles)
        readline.set_completer(completer.complete)

      # Prompt user for input
      try:
        validResponse = False
        while not validResponse:
          userInput = raw_input(promptStr)

          validResponse = verifyFun(userInput)
          if validResponse == False:
            # There is probably a better way to specify correct forms of arguments
            if item != "date":
              print "! %s is not a valid %s." % (userInput, item)
            else:
              print "! %s is not a valid %s. Required %s format: YYYY-MM-DD" % (userInput, item, item)

          # Force the user to manually enter fields (with exceptions)
          if userInput == '':
            # User input is blank
            if requireInput == True and item != 'date' and item != 'duration':
              print "! %s can't be empty." % item
              validResponse = False
          else:
            # User input is NOT blank and has already been verified.
            pass
            
          # Remove text from command history
          if userInput != "":
            self._removeHistoryEntry()

      except KeyboardInterrupt:
        status = False
        
        # It may be neccessary to clear this.  Test it
        userInput = ''
        
        print ""
        print "Aborting..."
        break
        
      except EOFError:
        # Abort if adding, Finish if correcting
        if requireInput == True:
          status = False
          
          userInput = ''
          
          print ""
          print "Aborting (until sensible defaults can be determined)..."
          break
        else:
          print ""
          print "Finishing..."
          skipRemainingInput = True
        
      finally:
        # Turn off tab complete
        if item in ['activity', 'group', 'title']:
          ## Restore smart completer
          readline.set_completer(self.mainCompleter.complete)
        
      #  Break the loop before userInput is set since we received the Ctrl+D for the next item and userInput is stale.
      if skipRemainingInput == True:
        #!print '\t', item, userInput
        break
        
      # Only change entries from the default if user input isn't blank
      if userInput != "":
        setFun(userInput)

    return status

      
  def addEntry(self, *args):
    '''
    Called when "add" or "a" is typed.  Allows a user to add a single entry.
    
    args is ignored.
    '''
    #!print "addEntry(", args, ")"
    
    # Create a blank entry -- may need to make this a function so it can be more easily overridden
    newEntry = entry.ReportEntry()

    #!newEntry.printEntry()

    print ""
    # Populate the entry
    status = self._getUserInput(newEntry, True)
    print ""

    #!newEntry.printEntry()
    #!print ""
    
    # Only add the entry if the user didn't Ctrl+c out of it
    if status == True:
      self.logObj.addEntry(newEntry)
      self.dirty = True
      #!newEntry.printEntry()
    else:
      #!print "addEntry canceled"
      pass
    
    return True


  def correctEntry(self, *args):
    '''
    Called when "correct" or "c" is typed.  Allows a user to correct an entry or multiple entries.
    
    args is a tuple of index strings (numbers starting from 1).  If no indices are specified, the last entry is corrected.
    '''
    #!print "correctEntry(", args, ")"
    
    # Get the entry to be corrected
    
    # If no arguments specified, correct the last entry
    if args == ():
      cArgs = (self.logObj.getLogLength(),)
    else:
      cArgs = args
    
    print ""
    
    for x in cArgs:
      try:
        index = int(x)
        if self.logObj.isValidIndex(index):
          # Backup the values of the object in case the user cancels the correction
          # This getEntry() should probably return a deepcopy of the obj, but that fails at the moment
          tempObj = self.logObj.getEntry(index-1)
          valueBackup = tempObj.getAll()

          print "Editing entry #%s" % x
          print ""
          tempObj.printEntry()
          print ""
          
          # Correct the entry
          status = self._getUserInput(tempObj)
          print ""
          
          # Only correct the entry if the user didn't Ctrl+c out of it
          if status == True:
            #
            self.logObj.replaceEntry(index-1, tempObj)
            self.dirty = True
          else:
            # This may need to change to continue in the future, depending on what comes after it
            #!print "correctEntry canceled"
            # restore the value backup
            tempObj.setAll(valueBackup)
          
        else:
          print "!", x, "is outside the valid index range."
      except ValueError:
        print "!", x, "is not a valid index (integer)."
        print ""
        continue

    return True


  def _getChangeInput(self):
    # Prompt for old group
    # Prompt for old title
    # Prompt for new group (optional)
    # Prompt for new title
    
    promptAdj = ['Old', 'Old', 'New', 'New']
    promptItem = ['group', 'title', 'group', 'title']
    itemRequired = [True, True, False, True]
    verifyItem = [True, True, False, False]
    changeInput = []
    
    for i in range(len(promptItem)):
      item = promptItem[i]

      promptStr = "%s %s: " % (promptAdj[i], item)
      
      if item == 'group':
        # Combine default groups (likely a subset of valid groups) with collected groups (possibly containing non-default, but still valid groups)
        if i == 2:
          existingGroups = list(set(self.logObj.collectGroups()) | set(self.possibleGroups[1:]))
        else:
          existingGroups = self.logObj.collectGroups()
        existingGroups.sort()
        print "  Possible groups:   %s" % ", ".join(existingGroups)
        readline.parse_and_bind("tab: complete")
        completer = _TabCompleter(existingGroups)
        readline.set_completer(completer.complete)
      if item == 'title':
        # Group is element of list before the current one
        existingTitles = self.logObj.collectEntries(changeInput[i-1], item)
        print "  Existing titles for %s:   %s" % (changeInput[i-1], ", ".join(existingTitles)) 
        readline.parse_and_bind("tab: complete")
        completer = _TabCompleter(existingTitles)
        readline.set_completer(completer.complete)

      # Prompt user for input
      try:
        validResponse = False
        while not validResponse:
          userInput = raw_input(promptStr)

          # 
          if userInput == '':
            # User input is blank
            if itemRequired[i] == True:
              print "! %s %s can't be empty." % (promptAdj[i], item)
              validResponse = False
            elif i == 2:
              # Set new group to old group if none is specified
              desiredInput = changeInput[0]
              validResponse = True
          else:
            # User input is NOT blank
            if verifyItem[i]:
              if item == 'group':
                validResponse = userInput in existingGroups
              else:
                validResponse = userInput in existingTitles
            elif i == 2:
              # verify optional new group to make sure it is valid
              validResponse = userInput in config.possible_groups[1:]
            else:
              validResponse = True

            if validResponse == False:
              if i == 2:
                print "! %s is not a valid %s." % (userInput, item)
              else:
                print "! %s is not an existing %s." % (userInput, item)
            else:
              desiredInput = userInput
          
          # Remove text from command history
          if userInput != "":
            self._removeHistoryEntry()
          
          if validResponse:  
            changeInput.append(desiredInput)

      except (KeyboardInterrupt, EOFError):
        userInput = ''
        changeInput = []
        
        print ""
        print "Aborting..."
        break
        
      finally:
        # Turn off tab complete
        if item in ['activity', 'group', 'title']:
          ## Restore smart completer
          readline.set_completer(self.mainCompleter.complete)
        
    return changeInput


  def changeTitle(self, *args):
    '''
    Called when "ch" is typed.  Allows bulk change of titles.
    
    args: None
    '''
    #!print "changeTitle(", args, ")"
    changeResponse = self._getChangeInput()
    #!print changeResponse
    oldGroup, oldTitle, newGroup, newTitle = changeResponse
    
    if changeResponse != []:
      # 
      existingTitles = self.logObj.collectEntries(newGroup, 'title')
      if newTitle in existingTitles:
        # If merging titles, tag descriptions of renamed title with old title
        self.logObj.changeTitle(changeResponse, True)
      else:
        self.logObj.changeTitle(changeResponse, False)
      self.dirty = True
      
    return True


  def saveLog(self, *args):
    '''
    Called when "save" or "s" is typed.  Causes the log to be saved and the dirty flag to be cleared.
    '''
    #!print "saveLog(", args, ")"
    self.logObj.saveLog()
    self.dirty = False
    return True


  def quit(self, *args):
    '''
    Called when "quit" or "q" is typed.  Takes into account whether there are unsaved changes before quitting the program.
    '''
    #!print "quit(", args, ")"
    if self.dirty == False:
      print "Quitting..."
      retval = False
    else:
      rawAck = raw_input("You have unsaved changes, are you sure you want to quit without saving? ")
      ack = string.strip(rawAck)
      if ack == "Yes" or ack == "yes" or ack == "Y" or ack == "y":
        print "Discarding unsaved changes and quitting..."
        retval = False
      else:
        print "A very wise choice!"
        retval = True

    return retval


  def _getLogFilename(self):
    '''
    Internal routine that determines the user's desired log file name.
    '''
    # Allow the user to specify an log file when running the script
    if len(sys.argv) > 1:
      filepath = sys.argv[1]
    else:
      filepath = "%s/%s" % (os.getcwd(), self.logFilename)
      # Alternately could use the script location (sys.argv[0]), but that seems like a bad decision

    #
    directory = os.path.split(filepath)[0]
    filename = os.path.split(filepath)[1]

    # Check to see if the file exists
    if not os.path.isfile(filepath):
      print filepath, "DOES NOT EXIST!"

      # Ask the user if the file should be created
      try:
        decision = raw_input("Would you like to create it? (y/n) ")
      except KeyboardInterrupt:
        print
        decision = "No"

      if decision in ("Yes", "yes", "Y", "y"):
        # Create the file
        print "Creating %s" % filepath
      else:
        self.run = False

    return (filepath, directory, filename)


  def main(self):
    '''
    The main loop of the CLI.  Responsible for interpreting commands typed by the user.
    '''
    # print only the long form of the commands
    longCommandList = sorted([c for c in self.commands.keys() if len(c) > 1])
    #!print longCommandList
    # print groups that have been used so far
    #!print self.logObj.collectGroups()

    # Set up the smart tab completer
    readline.parse_and_bind("tab: complete")
    self.mainCompleter = _SmartTabCompleter(longCommandList, self.logObj)
    readline.set_completer(self.mainCompleter.complete)
    
    # Enter command interpreter mode
    while ( self.run ):
      try:
        command = raw_input(" > ")
      except KeyboardInterrupt:
        print ""
        command = "quit"
      except EOFError:
        print ""
        continue

      cmnd = string.strip(command)
      if len(cmnd) > 0:
        cmndKey = cmnd.split(" ")[0]
        args = cmnd.split(" ")[1:]
        #!print cmnd, cmndKey, commands.keys()
        if cmndKey in self.commands.keys():
          #!print commands[cmndKey]
          self.run = self.commands[cmndKey](*args)
        else:
          print "\"%s\" is not a valid command" % cmnd


class _SmartTabCompleter:
  '''
  A custom tab-completer class for the main loop.  Needs to be smart (auto-complete commands and then groups based on the command).
  '''
  def __init__(self, commandList, logObj):
    self.commands = commandList
    self.logObj = logObj
    self.currentCandidates = []
    
  def complete(self, text, state):
    '''
    A mandatory method that returns the subset of strings to be tab-completed.
    
    NOTE: this doesn't work well if spaces are not word delimiters
    '''
    response = None
    if state == 0:
      originalLine = readline.get_line_buffer()
      begin = readline.get_begidx()
      end = readline.get_endidx()
      wordToComplete = originalLine[begin:end]
      words = originalLine.split(" ")
      
      #!logging.debug('originalLine=%s', repr(originalLine))
      #!logging.debug('begin=%s', begin)
      #!logging.debug('end=%s', end)
      #!logging.debug('wordToComplete=%s', wordToComplete)
      #!logging.debug('words=%s', words)

      if not words:
        # If no words have been typed, then the long commands are candidates for tab-completion
        self.currentCandidates = self.commands[:]
      else:
        try:
          if begin == 0:
            # first word (command is being tab-completed)
            candidates = self.commands[:]
          else:
            if words[0] in ['sum', 'psum', 'rep', 'prep']:
              # later word (group is being tab-completed, but only if command is correct)
              try:
                candidates = self.logObj.collectGroups()
              except:
                #!logging.debug('Group collection failed:')
                candidates = []              
            else:
              # command doesn't require a group argument, so don't tab-complete anything
              candidates = []
              #!logging.debug("command doesn't require tab-completion")
             
          #!logging.debug('candidates=%s', candidates)

          if wordToComplete != "":
            # match commands with wordToComplete
            self.currentCandidates = [w for w in candidates if w.startswith(wordToComplete)]
          else:
            # matching empty string so use all candidates
            self.currentCandidates = candidates

          #!logging.debug('currentCandidates=%s', self.currentCandidates)
          
        except (KeyError, IndexError), err:
          #!logging.error('completion error: %s', err)
          self.currentCandidates = []
        except:
          #!logging.error('something is very wrong: %s', err)
          pass

    try:
      response = self.currentCandidates[state]
    except IndexError:
      response = None
    
    #!logging.debug('complete(%s, %s) => %s', repr(text), state, response)
    return response


class _TabCompleter:
  '''
  A custom class that allows the specification of a list of strings to be tab-completed.
  '''
  def __init__(self,items):
    self.items = items

  def complete(self,text,state):
    '''
    A mandatory method that returns the subset of strings to be tab-completed.
    '''
    #!logging.debug(text)
    results = [x for x in self.items if x.startswith(text)] + [None]
    #!logging.debug(results)
    return results[state]
    
    ###
    # results = [x for x in self.items if x.startswith(text)]
    # try:
    #     return results[state]
    # except IndexError:
    #     return None
    ###


if __name__ == "__main__":
  cli = ReportCli()

