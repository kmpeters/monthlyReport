#!/usr/bin/env python3

'''
Kevin's custom cli customizations:
  1. Reduced the group list to only those groups I actually use.
  2. Rearrange the order of the fields so that activity is prompted after the description is entered.
'''

import cli
import log

class MyCli(cli.ReportCli):
  # Override the definition function to customize interface defaults
  def definitions(self):
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

  # Override the createReportLog function so that MyReportLog is used instead of ReportLog
  def createReportLog(self, filepath):
    return MyReportLog(filepath)

class MyReportLog(log.ReportLog):
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
  myCli = MyCli()
