#!/usr/bin/env python

############  SVN Repository information  #############
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
#######################################################

import sys
import os
import xml.etree.ElementTree as etree
import xml.parsers.expat
import time
import shutil
import string
import textwrap
import readline

version = "0.1"

# Set terminalWidth equal or less than your default terminal width
terminalWidth = 132

class paCli:

	def __init__(self, mrXmlDir):
		self._userDefinitions()
		self.run = True

		self.xmlDir = mrXmlDir
		#!print self.xmlDir
		# TODO: allow specifying this somehow in the future.
		self.paXmlFile = "%s.xml" % time.strftime("%Y")
	
		# Read xml files or perfApp log
		self.root = self._readPerfAppData()

		# Check totals
		self.checkTotals()

		# Replace spaces with underscores in subjects so that renaming can be implemented.
		self._replaceSpaces("subject")
		self._replaceSpaces("title")

	def _userDefinitions(self):
		self.commands = {
			"p":self.printLog,
			"sum":self.summary,
			"psum":self.percentSummary,
			"rep":self.report,
			"prep":self.percentReport,
			"q":self.quit,
			"s":self.save,
			"rr":self.rereadPerfAppLog,
			"h":self.showHelp,
			"ct":self.checkTotals,
			"rs":self.renameSubject
			}
	
			
	def showHelp(self):
		print """
  Commands:
    h			prints this help message
    p			prints the perf app log
    sum	[title]		prints the perf app summary
    psum [title]	prints the perf app summary (percents)
    rep	[title]		prints the perf app summary with details
    prep [title]	prints the perf app summary with details (percents)
    s			saves the perf app log
    rr			rereads the perf app log
    q			quits the program
    ct			checks the totals for each month
    rs title old_subject new_subject	renames the subject
		"""
		return True

	def _readPerfAppLog(self):
		xmlRoot = None

		# Check to see if perf app log exists
		path = "%s/%s" % (self.xmlDir, self.paXmlFile)
		if os.path.exists(path):
			print "Reading \"%s\"" % path
			try:
				temproot = etree.parse(path).getroot()
				if temproot.tag == "Performance_Appraisal":
					xmlRoot = temproot
				else:
					print "\"%s\" is not a perf app xml file."
			except:
				print "\"%s\" is not an xml file." % path
				pass
		else:
			print "\"%s\" doesn't exist." % path
		
		return xmlRoot

	def _readPerfAppData(self):
		xmlRoot = self._readPerfAppLog()
				
		if xmlRoot == None:
			print "Reading monthly-report xml files"

			logArray = []

			# Could find all xml files in subdirectories in the future, but how to handle duplicates and backup files?
			root, dirs, files = os.walk(self.xmlDir).next()
			if self.xmlDir == None:
				self.xmlDir = root
			
			#!print files
			if len(files) == 0:
				print "There are no xml files."
				# Temporarily quit
				self.run = False
			
			for f in files:
				if f[-4:].upper() == ".XML":
					path = "%s/%s" % (root, f)
					#!print path
					#
					try:
						temproot = etree.parse(path).getroot()
						if temproot.tag == "BCDA_Staff_Monthly_Report":
							logArray.append(temproot)
						else:
							print "\"%s\" is not a BCDA staff monthly report xml file." % path
					except xml.parsers.expat.ExpatError, e:
						print "There was a problem reading \"%s\":" % path
						print "\t%s" % e
						# Temporarily quit
						self.run = False
				else:
					#!print "%s doesn't have an xml extension" % f
					pass
	
			if len(logArray) > 0:
				# Creating a new tree might not be necessary at this point
				#!masterLog = etree.ElementTree()
				# Create a new element to be the xml root
				xmlRoot = etree.Element("Performance_Appraisal")
	
				### Stuff to do before saving
				#!indent(xmlRoot)
				#!masterLog._setroot(log)
				#!masterLog.write(filename)

				#!print logArray
				for l in logArray:
					#!printTree(l)
		
					# Placeholder for date
					date = l.find("date").text
					#!print date
					fullName = l.find("author_fullname").text
		
					for elem in l:
						#!print elem, elem.tag
						if elem.tag == "remark":
							#!print "Remark!"
							dateElem = etree.SubElement(elem, "date")
							dateElem.text = date
				
							#!printTree(elem)
							#!for i in elem:
							#!	print i
							xmlRoot.append(elem)
			else:
				print "No perf app data found."
				
		#!print xmlRoot
		#!printTree(xmlRoot)

		return xmlRoot

	def _printTree(self, elem):
		for e in elem:
			if len(e) == 0:
				# Add an extra tab if tag is too short
				if len(e.tag) < 7:
					print "%s:\t\t%s" % (e.tag, e.text)
				else:
					print "%s:\t%s" % (e.tag, e.text)
			else:
				print ""
				self._printTree(e)

	def renameSubject(self, *args):
		print "changeSubject(", args, ")"
		if len(args) != 3:
			print "Usage: rs title old_subject new_subject"
		else:
			specifiedTitle = args[0]
			oldSubject = args[1]
			newSubject = args[2]
			for remark in self.root:
				title = remark.find("title")
				if title.text.upper() == specifiedTitle.upper():
					subject = remark.find("subject")
					if subject.text == oldSubject:
						# TODO: set a dirty flag
						subject.text = newSubject
		return True

	# Replacing spaces is necessary to allow subjects to be renamed
	def _replaceSpaces(self, tag):
		for remark in self.root:
			elem = remark.find(tag)
			if " " in elem.text:
				#!print "\"%s\" contains spaces. Replacing spaces with underscores." % elem.text
				elem.text = elem.text.replace(" ", "_")

	def checkTotals(self):
		monthTotals = {}

		for remark in self.root:
			date = remark.find("date")
			effort = remark.find("effort")
			# Assume the effort has a percent sign
			effortNum = float(effort.text[:-1])

			if date.text not in monthTotals:
				monthTotals[date.text] = 0.0

			monthTotals[date.text] += effortNum

		#!print monthTotals

		num = 0
		for k, v in monthTotals.iteritems():
			if v != 100.0:
				print "Report with date %s has %s%% total effort." % (k, v)
				num += 1

		if num == 0:
			print "All reports have 100% total effort."

		return True

	def _analyze(self):
		if len(self.root) == 0:
			print "There is nothing to analyze"
			return None

		subjectTotals = {}
		details = {}
		
		# do the totaling
		for remark in self.root:
			title = remark.find("title")
			if title.text not in subjectTotals:
				subjectTotals[title.text] = {}
				details[title.text] = {}
				
			subject = remark.find("subject")
			if subject.text not in subjectTotals[title.text]:
				subjectTotals[title.text][subject.text] = 0.0
				details[title.text][subject.text] = []
			
			effort = remark.find("effort")
			# Remove the percent sign from the effort
			effortNum = float(effort.text[:-1])

			entry = remark.find("entry")
			date = remark.find("date")
			
			details[title.text][subject.text].append((date.text, effortNum, entry.text))
			
			subjectTotals[title.text][subject.text] += effortNum

		
		t = subjectTotals.keys()
		t.sort()
		
		#!print t
		#!print ""
		#!print subjectTotals
		#!print ""
		#!print details
		
		titleTotals = {}
		recordedTotal = 0.0
		for i in t:
			s = subjectTotals[i].keys()
			s.sort()
			
			# loop over subject to get a title total
			titleTotal = 0.0
			for j in s:
				titleTotal += subjectTotals[i][j]
			
			titleTotals[i] = titleTotal
			recordedTotal += titleTotal
		
		#!print ""
		#!print titleTotals
		#!print ""
		#!print recordedTotal
		
		return (details, titleTotals, subjectTotals, recordedTotal)
		
	def _displayAnalysis(self, args, percentFlag, detailFlag):
		print "displayAnalysis(", args, ")"
		details, titleTotals, subjectTotals, recordedTotal = self._analyze()
		
		#!print details
		#!print titleTotals
		#!print subjectTotals
		#!print recordedTotal
		
		s = subjectTotals.keys()
		s.sort()
		#!print s
		
		# Determining the subset of titles to display could be its own function
		titlesToDisplay = []
		if args == ():
			print "No title specified.  Display all"
			titlesToDisplay = s[:]
		else:
			sCapital = [x.upper() for x in s]
			for i in args:
				# Do a case-insensitive comparison
				if i.upper() in sCapital:
					#!print "%s is valid" % i
					# Append the original form of the title, not the form typed by the user
					titlesToDisplay.append(s[sCapital.index(i.upper())])
				else:
					print "%s isn't a valid title" % i
		
		print titlesToDisplay 
		
		print ""
		for t in titlesToDisplay:
			sKeys = subjectTotals[t].keys()
			sKeys.sort()
			
			# print title total
			if percentFlag == False:
				print "%5.1f %s" % (titleTotals[t], t)
			else:
				print "%4.1f%% %s" % (titleTotals[t] / recordedTotal * 100.0, t)
			
			# loop over subjects printing totals
			for s in sKeys:
				if percentFlag == False:
					print "\t%5.1f %s" % (subjectTotals[t][s], s)
				else:
					print "\t%4.1f%% %s" % (subjectTotals[t][s] / recordedTotal * 100.0, s)
			
				if detailFlag == True:
					for detail in details[t][s]:
						# detail[0] = date.text
						# detail[1] = effortNum
						# detail[2] = entry.text
						# At some point it may be useful to display the details with yearly percents
						line = "\t\t%s ; %.1f ; %s" % (detail[0], detail[1], detail[2])
						print textwrap.fill(line, width=(terminalWidth-16), subsequent_indent="\t\t")
						print ""
		
		print ""
		print "Recorded Total: %.1f" % recordedTotal
		print ""
		
	def summary(self, *args):
		print "summary(", args, ")"
		self._displayAnalysis(args, False, False)
		return True
	
	def percentSummary(self, *args):
		print "percentSummary(", args,")"
		self._displayAnalysis(args, True, False)
		return True

	def report(self, *args):
		print "report(", args, ")"
		self._displayAnalysis(args, False, True)
		return True
	
	def percentReport(self, *args):
		print "percentReport(", args,")"
		self._displayAnalysis(args, True, True)
		return True

	def _indent(self, elem, level=0):
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

	def printLog(self):
		self._printTree(self.root)
		return True

	def quit(self):
		# TODO: check dirty flag before exiting
		print "Exiting..."
		return False

	def save(self):
		# TODO: check dirty flag before saving
		okToSave = True
		saveName = "%s/%s" % (self.xmlDir, self.paXmlFile)
		if os.path.exists(saveName):
			print "\"%s\" already exists" % saveName
			bupSaveName = "%s.bup" % saveName
			print "Moving \"%s\" to \"%s\"" % (saveName, bupSaveName)
			shutil.move(saveName, bupSaveName)

		print "Saving perf app log to \"%s\"" % saveName
		tree = etree.ElementTree()
		self._indent(self.root)
		tree._setroot(self.root)
		tree.write(saveName)

		return True

	def rereadXmlfiles(self):
		print "Rereading xml files"
	
	def rereadPerfAppLog(self):
		# There may be inconsistencies in the naming of subjects between months
		# (since the subjects don't appear on the monthly report). Rather than
		# try to decide which variation is correct, let the user correct the
		# perf app xml file and reload it.
		print "Rereading PerfApp Log"
		# TODO: warn user about unsaved changes?
		xmlRoot = self._readPerfAppLog()
		
		if xmlRoot != None:
			print "reread successful"
			self.root = xmlRoot
		else:
			print "reread failed."
		
		return True

	def main(self):
		# Enter command interpreter mode
		while (self.run ):
			command = raw_input(">> ")
			cmnd = string.strip(command)
			
			if len(cmnd) > 0:
				cmndKey = cmnd.split(" ")[0]
				args = cmnd.split(" ")[1:]
				#!print cmnd, cmndKey, self.commands.keys()
				if cmndKey in self.commands.keys():
					#!print self.commands[cmndKey]
					self.run = self.commands[cmndKey](*args)
				else:
					print "\"%s\" is not a valid command" % cmndKey
			
			
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: pa.py <path to directory containing monthly report xml files>"
	else:	
		if os.path.isdir(sys.argv[1]):
			cli = paCli(sys.argv[1])
			cli.main()
		else:
			print "\"%s\" doesn't exist." % sys.argv[1]

