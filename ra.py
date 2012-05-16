#!/usr/bin/env python

'''
Kevin's custom cli customizations:
  1. Reduced the group list to only those groups I actually use.
  2. Rearrange the order of the fields so that customer and activity are prompted after the description is entered.
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

    # Here is where you can specify only the groups you regularly use
    self.possibleGroups = ['', 
                    '15ID', '26ID', '32ID', 
                    '33BM', '33ID', '34ID', 
                    'BCDA', 'General', 'SSM', 'Other',
                    'Infrastructure',
                    'Training', 'Leave', 'Offsite',
                 ]

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
        "customer",
        "activity"
      ]

    
if __name__ == '__main__':
  myCli = MyCli()
