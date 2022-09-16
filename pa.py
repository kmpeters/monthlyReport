#!/usr/bin/env python3

'''
Kevin's custom cli customizations:
  1. Reduced the group list to only those groups I actually use.
  2. Rearrange the order of the fields so that activity is prompted after the description is entered.
'''

import sys
import os

import cli
import log

class PerfAppCli(cli.ReportCli):
  def displayHelp(self, *args):
    '''
    Called when "help" or "h" is typed.  Prints a help message.
    '''
    #!print("displayHelp(", args, ")")
    print("""
 Commands:
   help (h)      displays this help
   groups (lg)   list all available groups
   codes (pc)    list all available pay codes
   
   chd           set a custom date to be used as the default
   cld           clear the custom date
   lsd           list the default date

   sum [cat]     displays the month summary w/o details (hours)
   psum [cat]    displays the month summary w/o details (percent)
   rep [cat]     displays the month summary w/ details (hours)
   prep [cat]    displays the month summary w/ details (percent)

   print (p) [#] prints info from the log file (default=everything)
   list [label ...] list the labels used in the log. Default labels are
                 activity, group and title.
   
   sc            Start capturing report output to a text file instead of 
                 printing it to stdout.
   ec            End capture report output to a text file.  Quitting will
                 automatically close this file.

    """)
    return True


  # Override the definition function to customize interface defaults
  def definitions(self):
    # Only a subset of commands apply for the year
    self.commands = { 
         "help": self.displayHelp,
            "h": self.displayHelp,  
        "print": self.displayLog,
            "p": self.displayLog,
          "chd": self.changeDate,
          "cld": self.clearDate,
          "lsd": self.showDate,
         "exit": self.quit,
         "quit": self.quit,
            "q": self.quit,
          "sum": self.displaySummary,
         "psum": self.displayPercentSummary,
          "rep": self.displayReport,
         "prep": self.displayPercentReport,
         "list": self.listLabels,
            "l": self.listLabels,
       "groups": self.listGroups,
           "lg": self.listGroups,
        "codes": self.listPayCodes,
           "pc": self.listPayCodes,
           "sc": self.startCapture,
           "ec": self.endCapture,
         }
    
    # You can specify a different default name for the log file
    self.logFilename = "work_log.xml"
    
    # You can change the terminal width that is used to wrap text when displaying summaries
    self.terminalWidth = 132

    # Restore pre-Jira wr/wrep output
    #!self.wrDateSort = False

    # Here is where you can specify only the groups you regularly use
    self.possibleGroups = ['', 
					'BCDA', 'Jira', 'MEDM Replacement', 'motor', 'synApps', 
					#'EPICS base', 'EPICS clients', 'areaDetector',
					#'Python', 'spec', 'VxWorks', 'Beamline Comp Env', 
					'09ID-B', '09ID-C', '15ID', '26ID', '32ID', '33BM', '33ID', 
					'34ID-C', '34ID-E', 'XSD', 'Leave', '33ID-C HFM',
					'ATOMIC/3DMN Support', 'ATOMIC/3DMN Design',
					'ATOMIC 34ID-F', '3DMN 34ID-E']

    self.payCodeDict = {#'None':'None',
                          'VAC':'Vacation',
                          'SIC':'Sick Pay',
                          'SLF':'Sick Leave Family',
                          'FHL':'Floating Holiday',
                         #'BRV':'Bereavement',
                         #'CL1':'Operations Suspended',
                         #'JUR':'Jury Duty',
                         #'PAR':'Parental Leave*',
                           'RG':'Regular',
                          'TEL':'TELECOMMUTING*'
                          }
    self.possiblePayCodes = sorted(list(self.payCodeDict.keys()))

    # Improve correctEntry prompts
    #!self.showCorrectDefaults = True
    #!self.showCorrectDescLen = 60

    ### Improve the wt command for Dayforce
    self.showWBSCodes = True
    # The cost codes are now workday project plans, which are only differentiated by the WBS code. Save screen space and omit them.
    self.showCostCodes = False
    # Pay codes only appear on d, ds and wd output
    self.showPayCodes = True
    # Use the default pay code for everything
    self.promptForPayCode = False
    
    # Temporarily change default pay code
    self.defaultPayCode = "TEL"

  
  def _getLogFilenames(self):
    '''
    Internal routine that determines the user-specified log file names
    '''
    # Allow the user to specify an log file when running the script
    if len(sys.argv) > 1:
      args = sys.argv[1:]
    else:
      args = ["{}/{}".format(os.getcwd(), self.logFilename),]
    
    filepaths = []
    
    for arg in args:
      # Check to see if the file exists
      if os.path.isfile(arg):
        filepaths.append(arg)
      else:
        print("{} DOES NOT EXIST!".format(arg))

    return filepaths[:]
  
  
  # Override the createReportLog function so that PerfAppLog is used instead of ReportLog
  def createReportLog(self, filepaths):
    return PerfAppLog(filepaths)
  
  
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


class PerfAppLog(log.ReportLog):
  def __init__(self, logFiles):
    self.definitions()
    
    # Note: the ReportLog class also defines a logFile member, but that isn't needed here;
    #       all of the commands that use it have been removed.
    
    self.entryArray = []
    
    for logFile in logFiles:
      print("Reading {}".format(logFile))
      # Append the entries from each log file to the entry array
      self.entryArray += (self.createLogFileObj(logFile, self.logEntryDef[:])).convertLogToObjs()
      
  
  # Override the definition function to change the order of items in logEntryDef
  # NOTE: group must always come before title
  def definitions(self):
    self.logEntryDef = [
        "date",
        "duration",
        "group",
        "title",
        "description",
        "activity",
        "payCode"
      ]

    
if __name__ == '__main__':
  perfAppCli = PerfAppCli()
