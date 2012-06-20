#!/usr/bin/env python

########### SVN repository information ###########
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###########

'''
The Entry class used by Kevin's monthly-report software.  

Allows the interface to be agnostic with respect to the log file type.
'''

from time import strftime, strptime

import config

class ReportEntry:
  '''
  Class representing a monthly-report entry.
  
  All arguments to the init function are strings.
  '''
  def __init__(self, date=None, duration="0.0", customer="", activity="", group="", title="", description=""):
    if date == None:
      self.date = strftime("%Y-%m-%d")
    self.duration = duration
    self.customer = customer
    self.activity = activity
    self.group = group
    self.title = title
    self.description = description
    self.functionDict = {"date":(self.getDate, self.setDate, self.verifyDate), 
      "duration":(self.getDuration, self.setDuration, self.verifyDuration),
      "customer":(self.getCustomer, self.setCustomer, self.verifyCustomer),
      "activity":(self.getActivity, self.setActivity, self.verifyActivity),
      "group":(self.getGroup, self.setGroup, self.verifyGroup),
      "title":(self.getTitle, self.setTitle, self.verifyTitle),
      "description":(self.getDescription, self.setDescription, self.verifyDescription),
      "index":(self.getIndex, self.setIndex, self.verifyIndex)}
    self.index = -1

  def getAll(self):
    '''
    Method to get all the fields that can be modified by the user.
    
    Returns [self.date, self.duration, self.customer, self.activity, self.group, self.title, self.description]
    '''
    return [self.date, self.duration, self.customer, self.activity, self.group, self.title, self.description]
  
  def setAll(self, fieldList):
    '''
    Method to set all the fields that can be modified by the user.
    
    fieldList: [self.date, self.duration, self.customer, self.activity, self.group, self.title, self.description]
    '''  
    self.date, self.duration, self.customer, self.activity, self.group, self.title, self.description = fieldList
    return
  
  
  def getDate(self):
    '''
    Method to get the entry date.
    '''  
    return self.date
  
  def getDuration(self):
    '''
    Method to get the entry duration.
    '''  
    return self.duration
    
  def getCustomer(self):
    '''
    Method to get the entry customer.
    '''  
    return self.customer
  
  def getActivity(self):
    '''
    Method to get the entry activity.
    '''  
    return self.activity
  
  def getGroup(self):
    '''
    Method to get the entry group.
    '''  
    return self.group
    
  def getTitle(self):
    '''
    Method to get the entry title.
    '''  
    return self.title
    
  def getDescription(self):
    '''
    Method to get the entry description.
    '''  
    return self.description

  def getIndex(self):
    '''
    Method to get the entry index.
    '''  
    return self.index
    
  def setDate(self, date):
    '''
    Method to set the entry date (String).
    '''  
    self.date = date
    
  def setDuration(self, duration):
    '''
    Method to set the entry duration (String).
    '''  
    self.duration = duration
    
  def setCustomer(self, customer):
    '''
    Method to set the entry customer (String, choices defined in the config module).
    '''  
    self.customer = customer
    
  def setActivity(self, activity):
    '''
    Method to set the entry activity (String, choices defined in the config module).
    '''  
    self.activity = activity
    
  def setGroup(self, group):
    '''
    Method to set the entry group (String, choices defined in the config module).
    '''  
    self.group = group
    
  def setTitle(self, title):
    '''
    Method to set the entry title (String).
    '''  
    self.title = title
    
  def setDescription(self, description):
    '''
    Method to set the entry description (String).
    '''  
    self.description = description

  def setIndex(self, index):
    '''
    Method to set the entry index (String, numbering starts with 1)
    '''  
    # Maybe should make this simply pass instead
    self.index = index

  def verifyDate(self, userInput):
    '''
    Method to verify the date to be written to the entry. (String)
    '''  
    if userInput == "":
      valid = True
    else:
      try:
        strptime(userInput, '%Y-%m-%d')
        valid = True
      except ValueError:
        valid = False
    return valid
  
  def verifyDuration(self, userInput):
    '''
    Method to verify the duration to be written to the entry. (String)
    '''  
    if userInput == "":
      valid = True
    else:
      try:
        float(userInput)
	valid = True
      except ValueError:
        valid = False
    return valid
    
  def verifyCustomer(self, userInput):
    '''
    Method to verify the customer to be written to the entry. (String)
    '''  
    if userInput in config.possible_customers:
      valid = True
    else:
      valid = False
    return valid
  
  def verifyActivity(self, userInput):
    '''
    Method to verify the activity to be written to the entry. (String)
    '''  
    if userInput in config.possible_activities:
      valid = True
    else:
      valid = False
    return valid
  
  def verifyGroup(self, userInput):
    '''
    Method to verify the group to be written to the entry. (String)
    '''  
    if userInput in config.possible_groups:
      valid = True
    else:
      valid = False
    return valid

  def verifyTitle(self, userInput):
    '''
    Method to verify the title to be written to the entry. (String)
    '''  
    return True
    
  def verifyDescription(self, userInput):
    '''
    Method to verify the description to be written to the entry. (String)
    '''  
    return True

  def verifyIndex(self, userInput):
    '''
    Method to verify the index to be written to the entry. (String)
    '''  
    # Maybe should make this simply pass instead
    if userInput == "":
      valid = True
    else:
      try:
        index = int(userInput)
	if index >= -1:
	  valid = True
	else:
	  valid = False
      except ValueError:
        valid = False
    return valid
  
  def getFunctions(self, item):
    '''
    Method that returns the get, set and verify functions for a given string from log.logEntryDef.
    '''
    return self.functionDict[item]
  
  def printEntry(self):
    '''
    Prints the entry to the console.
    '''
    # Should this instead return a string representation of the entry?
    print "index: %s" % self.index
    print "date: %s" % self.date
    print "duration: %s" % self.duration
    print "customer: %s" % self.customer
    print "activity: %s" % self.activity
    print "group: %s" % self.group
    print "title: %s" % self.title
    print "description: %s" % self.description
