#!/usr/bin/env python3

############  SVN Repository information  #############
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
#######################################################

'''
Provides functionality to create an XML report and turn the XML report into a PDF.

Running the script allows the XML-to-PDF conversion to be done outside of a user interface. 
'''


import xml.etree.ElementTree as etree
from time import strftime
from os.path import isfile, exists, split
from os import system


def _compileLaTeX(subdir, texPrefix):
  print("")
  system("pdflatex -output-directory {} {}.tex".format(subdir, texPrefix))
  print("")

def _writeLaTeX(results, subdir, texPrefix):
  author = results[0]
  date = strftime("%B %Y")
  srDict = results[2]
  #groupTotals = results[3]
  
  # Eventually get more sophisticated about the filename and file existence checking
  if isfile("dummy.tex"):
    print("dummy.tex already exists")
    return

  # Build the .tex file in an array to write the fill in a single shot
  lines = []
  # LaTeX header
  lines.append("\\documentclass{article}\n")
  lines.append("\\usepackage{fullpage}\n")
  lines.append("\\author{{{0}}}\n".format(author))
  lines.append("\\title{{Monthly Report for {0}}}\n".format(date))
  lines.append("\\begin{document}\n")
  lines.append("\\maketitle\n\n")

  # LaTeX body
  #groups = list(groupTotals.keys())
  groups = list(srDict.keys())
  groups = sorted(groups)
  for group in groups:
    # LaTeX Section = monthly report group
    #!lines.append("\\section*{{{0} - \\emph{{{1}\\%}}}}\n\n".format(group, groupTotals[group]))
    # Pete would prefer we leave out group totals
    lines.append("\\section*{{{0}}}\n\n".format(group))
    # subsections might have more appropriate heading sizes
    #!lines.append("\\subsection*{{{0}}}\n\n".format(group))

    # Itemized list = dummy.xml remarks
    lines.append("\\begin{itemize}\n")
    # will likely need to search for bad characters in remark strings
    # item[0] = effortFloat, item[1] = remarks, item[2] = title
    for item in srDict[group]:
      ### At the momemt simply ignore the subject fields
      # Escape ampersand characters (Note: & isn't allowed in xml.  &amp; = xml ampersand
      correctedDetails = item[1].replace("&", "\\&")
      # Also handle underscores which are special to LaTeX
      correctedDetails = correctedDetails.replace("_", "\\_")
      # Also handle percents
      correctedDetails = correctedDetails.replace("%", "\\%")
      # And pound signs
      correctedDetails = correctedDetails.replace("#", "\\#")
      #lines.append("  \\item {0} - \\emph{{{1}\\%}}\n".format(correctedDetails, item[0]))
      lines.append("  \\item {0} - \\emph{{{1}}}\n".format(correctedDetails, item[0]))
  
      # Eventually figure out a pretty way of including an optional title
      #!if item[2] == None:
      #!      lines.append("  \\item {0} - \\emph{{{1}\\%}}\n".format(item[1], item[0]))
      #!else:
      #!      # Need to handle "optional" title somehow.  Not sure how to do it so it isn't ugly.		      
      
    lines.append("\\end{itemize}\n\n")

  # LaTeX end
  lines.append("\\end{document}\n")
  
  # 
  if subdir == '':
      subdir = "."

  # Write the .tex file
  filename = "{}/{}.tex".format(subdir, texPrefix)
  f = open(filename, 'w')
  f.writelines(lines)
  f.close()


def _analyzeXml(sr):
  fullname = None
  xmldate = None
  srDict = {}
  #groupTotals = {}

  # Get relevant info from xml file
  for elem in sr:
    if elem.tag == "author_fullname":
      fullname = elem.text

    if elem.tag == "date":
      xmldate = elem.text

    if elem.tag == "remark":
      # rename this element so the code is easier to read
      remark = elem
      group = remark.find("group")
      # the "title" element is optional
      title = remark.find("title")
      if title == None:
        titleText = None
      else:
        titleText = title.text
      effort = remark.find("effort")
      entry = remark.find("entry")

      # Add entries if group hasn't been encountered yet
      if group.text not in srDict:
        srDict[group.text] = []
        #groupTotals[group.text] = 0.0

      # Add a tuple for this bullet point to the srDict
      #effortFloat = float(effort.text[:-1])
      #srDict[group.text].append( (effortFloat, entry.text, titleText) )
      srDict[group.text].append( (effort.text, entry.text, titleText) )
      # Add it to the total effort calculation
      #groupTotals[group.text] += effortFloat

  # Compute total (sanity check)
  #totalEffort = 0.0
  #for group in groupTotals:
  #	  totalEffort += groupTotals[group]
  #print("")
  #print("Total effort: {:0.2f}%".format(totalEffort))
  #print("")

  #return (fullname, xmldate, srDict, groupTotals)
  return (fullname, xmldate, srDict)


def _readXml(fullFilePath):
  tree = etree.parse(fullFilePath)
  sr = tree.getroot()
  return sr


def makeReport(fullFilePath):
  '''
  Converts a report XML file to LaTeX and then compiles it into a PDF
  
  Called by user interfaces and main routine.
  
  ============  ==============================================
  argument      description
  ============  ==============================================
  fullFilePath  (String) The full path to the xml report file.
  ============  ==============================================
  '''
  # TODO: Turn off print statments if being called from user interface?
  #       This may require exposing each of the internal functions so the user
  #       interface can choose what info to display.
  # Check to see if the subdirectory exists (assumes fullFilePath ends in .xml)
  subdir = fullFilePath[:-4]
  if exists( subdir ):
    print("The desired subdirectory ({}) already exists.".format(subdir))
  else:
    print("Creating subdirectory: {}".format(subdir))
    system("mkdir {}".format(subdir))

  # Read the xml report
  print("Reading {}".format(fullFilePath))
  sr = _readXml(fullFilePath)

  # Scan the tree for important info
  print("Analyzing {}".format(fullFilePath))
  results = _analyzeXml(sr)
  #!print(results)

  # Write the LaTeX file (may need to catch errors writing file)
  print("Writing LaTeX report")
  texPrefix = split(subdir)[1]
  _writeLaTeX(results, subdir, texPrefix)
  
  # Compile the LaTeX file (eventually will need to skip if there was a write error)
  print("Compiling LaTeX report and converting to pdf")
  _compileLaTeX(subdir, texPrefix)


def _indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      _indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i


def makeXml(analysis, directory, filename, fullName):
  '''
  Function that writes a skeleton xml report file based on the log summary.
  
  Called by user interfaces.
  
  =========  =====================================================================
  argument   description
  =========  =====================================================================
  analysis   (Tuple) The analyis tuple that is returned by log.getAnalysis()
  directory  (String) The path to the directory where the xml report file resides.
  filename   (String) The xml report filename.
  fullName   (String) The full name of the author.
  =========  =====================================================================
  '''
  #!print(analysis)
  details = analysis[0]
  groupTotals = analysis[1]
  titleTotals = analysis[2]
  recordedTotal = analysis[3]
  theoreticalHours = analysis[4]
  percent = analysis[5]

  # Author is the last word in the full name
  lastName = fullName.split()[len(fullName.split())-1]
  #!print("author", last_name)

  # Get current time
  currentTime = strftime("%Y-%m-%dT%H:%M:%S")
  currentDate = strftime("%Y-%m-%d")
  #!print("time", currentTime)

  # Create <BCDA_Staff_Monthly_Report>
  #!print("Creating {}".format(filename))
  tree = etree.ElementTree()
  root = etree.Element('BCDA_Staff_Monthly_Report', version="1.0")

  date = etree.SubElement(root, "date")
  date.text = currentDate

  authorFullname = etree.SubElement(root, "author_fullname")
  authorFullname.text = fullName

  author = etree.SubElement(root, "author")
  author.text = lastName

  # Get groups
  groups = list(titleTotals.keys())
  groups = sorted(groups)
  
  for group in groups:
    # Get titles
    titles = list(titleTotals[group].keys())
    titles = sorted(titles)

    # Eventually this should change to report hours instead of percents. 
    
    #groupPercent = groupTotals[group] / recordedTotal * 100.00
    #groupPercentStr = "{:.1f}%".format(groupPercent)
    
    groupHourStr = "{:.2f} hrs".format(groupTotals[group])
    
    for title in titles:
      #titlePercent = titleTotals[group][title] / recordedTotal * 100.0
      #titlePercentStr = "{:.1f}%".format(titlePercent)
      
      titleHourStr = "{:.2f} hrs".format(titleTotals[group][title])
      
      # Populate report with <remark>'s
      remark = etree.SubElement(root, "remark")

      # The group of the entry
      groupElem = etree.SubElement(remark, "group")
      groupElem.text = group

      # The title of the entry
      titleElem = etree.SubElement(remark, "title")
      titleElem.text = title

      # The user will replace this text with actual content
      entryElem = etree.SubElement(remark, "entry")
      #entryElem.text = "Details of {}".format(title)
      # Combine all the entry descriptions into a paragraph
      entryText = ""
      effortBreakdown = {}
      for entryObj in details[group][title]:
        # Combine all the entry descriptions into a paragraph
        entryText += entryObj.description
        entryText += " "
        
      entryElem.text = entryText

      effortElem = etree.SubElement(remark, "effort")
      #effortElem.text = titlePercentStr
      effortElem.text = titleHourStr
      
  # handle empty directory
  if directory == '':
    directory = "."

  # Write the populated staff report to disk
  _indent(root)
  tree._setroot(root)
  tree.write("{}/{}".format(directory, filename))

  return True


def main():
  '''
  Main loop that allows mkrep to be run from outside a user interface.
  '''
  # Require the user to specify an xml file when running the script
  if len(sys.argv) > 1:
    fullFilePath = sys.argv[1]
  else:
    print("Usage: mkrep.py <bcda_staff_monthly_report_xml>")
    return

  # Check to see if the file exists
  if not isfile(fullFilePath):
    print("The specified xml file ({}) doesn't exist.".format(fullFilePath))
    return

  makeReport(fullFilePath)


if __name__ == "__main__":
  import sys
  main()
