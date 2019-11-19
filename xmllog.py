#!/usr/bin/env python3

########### SVN repository information ###########
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###########

'''
The xml backend for Kevin's monthly-report software
'''

import xml.etree.ElementTree as etree
import shutil
import os.path

import entry

class XmlLog:
  '''
  Class representing a monthly-report xml file.
  
  filepath is the full path to the xml log (string).
  xmlEntryDef is a list of strings, defined as logEntryDef in the log module.
  '''
  def __init__(self, filepath, xmlEntryDef):
    self.filepath = filepath
    self.xmlEntryDef = xmlEntryDef
    self.definitions()

    # Split filename into dir and name
    self.directory = os.path.split(filepath)[0]
    self.filename = os.path.split(filepath)[1]
    # Handle empty directories when file is in cwd
    if self.directory == '':
      self.directory = "."

    # Check to see if file exists
    if not os.path.isfile(filepath):
      # Assume user wants file created (ui is responsible for aborting)
      self._createEmptyXML()

    # Read the file
    self.tree, self.root = self._readXML()

  def definitions(self):
    '''
    Method called by __init__ to define the root and entry element names in the xml file.  Designed to be overridden without having to reimplement __init__.
    '''
    self.xmlRoot = "log"
    self.xmlEntry = "entry"

  def convertEntryToObj(self, entryElem):
    '''
    Converts a single xml entry element into an ReportEntry object.
    '''
    # Create an empty ReportEntry object -- may need to make this a function so it can be more easily overridden
    newObj = entry.ReportEntry()
    # handle the index, which isn't in the xmlEntryDef
    getFun, setFun, verifyFun = newObj.getFunctions("index")
    setFun(entryElem.get("index"))
    
    # loop over elements of an entry
    for x in self.xmlEntryDef:
      getFun, setFun, verifyFun = newObj.getFunctions(x)
      # Set the ReportEntry object to the value from the xml file
      try:
        setFun(entryElem.find(x).text)
      except AttributeError:
        # The x element of the entry couldn't be found; None types don't have .text fields
        setFun("None")

    return newObj

  def convertLogToObjs(self):
    '''
    Converts the xml log into an array of ReportEntry objects.
    '''
    objArray = []
    for x in self.root:
      objArray.append( self.convertEntryToObj(x) )
      
    return objArray[:]

  def addEntry(self, entryObj):
    '''
    Add a SubElement to the xml root and populate it with the contects of the specified ReportEntry object.
    '''
    # Add an entry with the appropriate index
    length = len(self.root) + 1
    #!print(length)
    entryElem = etree.SubElement(self.root, "entry", index="{:d}".format(length))

    # Loop over array, appending to entry
    for x in self.xmlEntryDef:
      getFun, setFun, verifyFun = entryObj.getFunctions(x)
      elem = etree.SubElement(entryElem, x)
      # may need to test for blanks and things that break xml here
      elem.text = getFun()

  def replaceEntry(self, index, entryObj):
    '''
    Replace the contents of an xml entry with the values from the specified ReportEntry object.
    
    index is an integer (numbered from zero).
    entryObj is a ReportEntry object.
    '''
    #
    for x in self.xmlEntryDef:
      getFun, setFun, verifyFun = entryObj.getFunctions(x)
      self.root[index].find(x).text = getFun()

  def _indent(self, elem, level=0):
    '''
    Internal method to make the xml file easier to read by humans.
    '''
    i = "\n" + level*"  "
    if len(elem):
      if not elem.text or not elem.text.strip():
        elem.text = i + "  "
      if not elem.tail or not elem.tail.strip():
        elem.tail = i
      for elem in elem:
        self._indent(elem, level+1)
      if not elem.tail or not elem.tail.strip():
        elem.tail = i
    else:
      if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

  def _createEmptyXML(self):
    '''
    Creates an empty xml file.  File name is set in __init__ by the user interface.
    '''
    tree = etree.ElementTree()
    root = etree.Element(self.xmlRoot)
    # Add a comment so an empty xml file can be properly read
    comment = etree.Comment("This is an empty file")
    root.append(comment)
    self._indent(root)
    tree._setroot(root)
    tree.write(self.filepath)

  def _readXML(self):
    '''
    Reads the xml log file.  File name is set in __init__ by the user interface.
    '''
    # May need to expose this function with a general name to allow a GUI to reread an xml file
    # Protection is done at a higher level
    tree = etree.parse(self.filepath)
    root = tree.getroot()
    return tree, root

  def save(self):
    '''
    Write the xml file to disk.
    '''
    # Move current file to backup
    newfilepath = "{}.bup".format(self.filepath)
    shutil.move(self.filepath, newfilepath)
    # Make tree presentable
    self._indent(self.root)
    # Write file
    self.tree.write(self.filepath)
    # Clear the dirty flag
    self.dirty = False
