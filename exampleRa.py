#!/usr/bin/env python3

'''
Example showing how to use custom config to reduce group list
'''

import cli

class MyCli(cli.ReportCli):
  # Override the definition function to customize interface defaults
  def definitions(self):
    # You can specify a different default name for the log file
    self.logFilename = "work_log.xml"
    
    # You can change the terminal width that is used to wrap text when displaying summaries
    self.terminalWidth = 132

    # Here is where you can specify only the groups you regularly use
    self.possibleGroups = ['', 
					'BCDA', 'Jira', 'MEDM Replacement', 'motor', 'synApps', 
					'15ID', '26ID', '32ID', '33BM', '33ID', '34ID',
					'XSD', 'Leave']
    
if __name__ == '__main__':
  myCli = MyCli()
