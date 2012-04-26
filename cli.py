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
import string
import textwrap
import os.path

import config
import entry
import log
import mkrep

#!import logging

#!LOG_FILENAME = 'completer.log'
#!logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

class ReportCli:
  '''
  The command-line interface class, which interacts with the log module
  '''
  def __init__(self):
    # Remove '-' from delim list so entries with dashes tab-complete properly
    delims = readline.get_completer_delims()
    #!print ",".join(["%x" % ord(x) for x in delims])
    # Allow dashes and spaces to be included in tab-completed words
    new_delims = delims.replace("-",'')
    # Handle spaces in the tab-completer code, since this simple approach doesn't handle everything properly
    #!!!new_delims = new_delims.replace(" ",'')
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
	  "day": self.displayDay,
	    "d": self.displayDay,
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
	 
    self.possibleCustomers = config.possible_customers[:]
    self.possibleActivities = config.possible_activities[:]
    self.possibleGroups = config.possible_groups[:]
    
    self.logFilename = "work_log.xml"
    self.terminalWidth = 132
    
    # Override the above definitions
    self.definitions()
    
    # Flag to continue prompting for commands
    self.run = True
    # Dirty flag to indicate unsaved changes
    self.dirty = False

    # Get log filename
    self.filepath, self.directory, self.filename = self._getLogFilename()

    if self.run == True:
      # Read log file into persistent log object
      self.logObj = self.createReportLog(self.filepath)
      self.logEntryDef = self.logObj.getLogEntryDef()

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
   save (s)	 saves changes to the log file
   add (a)	 adds an entry to the log file
   corr (c) [#]  corrects the specified entry (default=last)
   help (h)      displays this help
   day [#]       prints list of entries for a given day (default=today)
   sum [cat] 	 displays the summary w/o details (hours)
   psum [cat]	 displays the summary w/o details (percent)
   rep [cat] 	 displays the summary w/ details (hours)
   prep [cat]	 displays the summary w/ details (percent)

   list [label ...] list the labels used in the log. Default labels are
                customer, activity, group and title.

   xml		Generates a skeleton xml report in the same directory
   		as the work log. Categories and keywords in the work log
		correspond to titles and subjects in the xml report.  
		Details must be MANUALLY entered after examining output
		of the 'prep' command.
		
   mkrep	Converts an xml file into a pdf. Titles are optional 
   		and do not currently appear in the pdf.
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
	except KeyboardInterrupt:
		print ""
		print "Aborting..."
		return False
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
    # Should probably catch Ctrl+C and Ctrl+D here
    desiredFilename = raw_input("XML report filename: ")
    
    # Remove text entry from history
    if desiredFilename != "":
      self._removeHistoryEntry()
    
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
	
    # Prompt user for their name
    fullName = raw_input("Your name: ")

    # Remove text entry from history
    if fullName != "":
      self._removeHistoryEntry()

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
    
    defaultLabels = ['customer', 'activity', 'group', 'title']
    
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
      self._displayAnalysis(analysis, True, False, args)
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
      self._displayAnalysis(analysis, True, True, args)
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
      self._displayAnalysis(analysis, False, False, args)
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
      self._displayAnalysis(analysis, False, True, args)
    else:
      print "! The log is empty."
    
    return True


  def _displayAnalysis(self, analysis, verbose=False, percents=False, desiredGroups=()):
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
	    for e in details[group][title]:
	      line = "\t\t%s ; %s ; %s - %s ; %s" % (e.date, e.duration, e.customer, e.activity, e.description)
              print textwrap.fill(line, width=(self.terminalWidth-16), subsequent_indent="\t\t")
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
	  print "%s ; %s ; %s - %s ; %s - %s ; %s" % (x.index, x.duration, x.group, x.title, x.customer, x.activity, x.description)
	  
	print ""
	print "Hours: %.2f" % dayHours
	print "Percent: %.1f%%" % percentRecorded
	print ""
      except ValueError:
	print "!", x, "is not a valid day (integer)."
	print ""
	continue
	
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
      
      promptStr = "%s: " % item
      
      # Set tab-complete based on which item is being input
      if item == 'customer':
        print "  Possible customers:   %s" % ", ".join(self.possibleCustomers[1:])
        readline.parse_and_bind("tab: complete")
        completer = _TabCompleter(self.possibleCustomers[:])
        readline.set_completer(completer.complete)
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
            print "! %s is not a valid %s." % (userInput, item)

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
        print ""
	print "Finishing..."
        skipRemainingInput = True
	
      finally:
        # Turn off tab complete
	if item in ['customer', 'activity', 'group', 'title']:
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
          tempObj = self.logObj.getEntry(index-1)
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
	    pass
	  
        else:
          print "!", x, "is outside the valid index range."
      except ValueError:
        print "!", x, "is not a valid index (integer)."
        print ""
        continue

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
	      #!logging.debug('COLLECTING CANDIDATES!!! %s', candidates)
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


if __name__ == "__main__":
  cli = ReportCli()			  
  cli.main()

