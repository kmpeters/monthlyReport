#!/usr/bin/env python

############  SVN Repository information  #############
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
#######################################################

import xml.etree.ElementTree as etree
from time import strftime
from os.path import isfile, exists, split
from os import system

def compileLaTeX(subdir, texPrefix):
	system("pdflatex -output-directory %s %s.tex" % (subdir, texPrefix) )

def writeLaTeX(results, subdir, texPrefix):
	author = results[0]
	date = strftime("%B %Y")
	srDict = results[2]
	catTotals = results[3]
	
	# Eventually get more sophisticated about the filename and file existence checking
	if isfile("dummy.tex"):
		print "dummy.tex already exists"
		return

	# Build the .tex file in an array to write the fill in a single shot
	c = []
	# LaTeX header
	c.append("\\documentclass{article}\n")
	c.append("\\usepackage{fullpage}\n")
	c.append("\\author{%s}\n" % author)
	c.append("\\title{Monthly Report for %s}\n" % date)
	c.append("\\begin{document}\n")
	c.append("\\maketitle\n\n")

	# LaTeX body
	cats = catTotals.keys()
	cats.sort()
	for cat in cats:
		# LaTeX Section = monthly report category
		#!c.append("\\section*{%s - \\emph{%d\\%%}}\n\n" % (cat, catTotals[cat]))
		# Pete would prefer we leave out category totals
		c.append("\\section*{%s}\n\n" % cat)
		# subsections might have more appropriate heading sizes
		#!c.append("\\subsection*{%s}\n\n" % cat)

		# Itemized list = dummy.xml remarks
		c.append("\\begin{itemize}\n")
		# will likely need to search for bad characters in remark strings
		# item[0] = effortFloat, item[1] = remarks, item[2] = subject
		for item in srDict[cat]:
			### At the momemt simply ignore the subject fields
			# Escape ampersand characters (Note: & isn't allowed in xml.  &amp; = xml ampersand
			correctedDetails = item[1].replace("&", "\\&")
			# Also handle underscores which are special to LaTeX
			correctedDetails = correctedDetails.replace("_", "\\_")
			# Also handle percents
			correctedDetails = correctedDetails.replace("%", "\\%")
			c.append("  \\item %s - \\emph{%d\\%%}\n" % (correctedDetails, item[0]) )
			
			# Eventually figure out a pretty way of including an optional subject
			#!if item[2] == None:
			#!	c.append("  \\item %s - \\emph{%d\\%%}\n" % (item[1], item[0]) )
			#!else:
			#!	# Need to handle "optional" subject somehow.  Not sure how to do it so it isn't ugly.			
			
		c.append("\\end{itemize}\n\n")

	# LaTeX end
	c.append("\\end{document}\n")
		
	#!for line in c:
	#!	print line

	# 
	if subdir == '':
		subdir = "."
	
	# Write the .tex file
	filename = "%s/%s.tex" % (subdir, texPrefix)
	f = open(filename, 'w')
	f.writelines(c)
	f.close()

def analyzeXml(sr):
	fullname = None
	xmldate = None
	srDict = {}
	catTotals = {}

	# Get relevant info from xml file
	for elem in sr:
		if elem.tag == "author_fullname":
			fullname = elem.text

		if elem.tag == "date":
			xmldate = elem.text

		if elem.tag == "remark":
			# rename this element so the code is easier to read
			remark = elem
			title = remark.find("title")
			# the "subject" element is optional
			subject = remark.find("subject")
			if subject == None:
				subjectText = None
			else:
				subjectText = subject.text
			effort = remark.find("effort")
			entry = remark.find("entry")
		
			# Add entries if category (title) hasn't been encountered yet
			if title.text not in srDict:
				srDict[title.text] = []
				catTotals[title.text] = 0.0
		
			# Add a tuple for this bullet point to the srDict
			effortFloat = float(effort.text[:-1])
			srDict[title.text].append( (effortFloat, entry.text, subjectText) )
			# Add it to the total effort calculation
			catTotals[title.text] += effortFloat

	# Compute total (sanity check)
	totalEffort = 0.0
	for cat in catTotals:
		totalEffort += catTotals[cat]
	print "Total effort: %0.2f%%" % totalEffort
	
	### Don't sort the lists. Assume the xml file has the desired order.
	# Sort lists inside srDict
	#!for cat in srDict:
	#!	# Sort by increasing time
	#!	srDict[cat].sort()
	#!	# Reverse it so more significant issues are first.
	#!	srDict[cat].reverse()
	
	return (fullname, xmldate, srDict, catTotals)

def readXml(fullFilePath):
	tree = etree.parse(fullFilePath)
	sr = tree.getroot()
	return sr

def makeReport(fullFilePath):
	# Check to see if the subdirectory exists (assumes fullFilePath ends in .xml)
	subdir = fullFilePath[:-4]
	if exists( subdir ):
		print "The desired subdirectory (%s) already exists." % subdir
		return
	else:
		print "Creating subdirectory: %s" % subdir
		system("mkdir %s" % subdir)

	# Read the xml report
	print "Reading %s" % fullFilePath
	sr = readXml(fullFilePath)

	# Scan the tree for important info
	print "Analyzing %s" % fullFilePath
	results = analyzeXml(sr)
	#!print results

	# Write the LaTeX file (may need to catch errors writing file)
	print "Writing LaTeX report"
	texPrefix = split(subdir)[1]
	writeLaTeX(results, subdir, texPrefix)
	
	# Compile the LaTeX file (eventually will need to skip if there was a write error)
	print "Compiling LaTeX report and converting to pdf"
	compileLaTeX(subdir, texPrefix)

def main():
	# Require the user to specify an xml file when running the script
	if len(sys.argv) > 1:
		fullFilePath = sys.argv[1]
	else:
		print "Usage: mkrep.py <bcda_staff_monthly_report_xml>"
		return
	
	# Check to see if the file exists
	if not isfile(fullFilePath):
		print "The specified xml file (%s) doesn't exist." % fullFilePath
		return

	makeReport(fullFilePath)

if __name__ == "__main__":
	import sys
	main()
