#!/usr/bin/env python

############  SVN Repository information  #############
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
#######################################################

version = "0.3.2"

# Set terminalWidth equal or less than your default terminal width
terminalWidth = 132

entryFields = ['date', 'duration', 'category', 'keyword', 'description', 'resolution']
entryRequired=[  0,	   1,	       1,	   0,	       1,	      0      ]
# It might be nicer to have the keyword after the description, since I often think of a better
# keyword after writing the details.  No other changes should be necessary, since dictionaries are used
#entryFields = ['day', 'date', 'duration', 'category', 'description', 'resolution', 'keyword']
dirty = False

# For logging, uncomment the following lines
#!import logging
#!LOG_FILENAME = '/Users/kpetersn/Development/monthlyReport/log.txt'
#!logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

def main():
	run = True

	# Allow the user to specify an xml file when running the script
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		print "No xml file specified; using default"
		filename = "%s/work_log.xml" % getcwd()

	# Assume that the directory of the work_log is where reports should be written
	directory = split(filename)[0]
	logfilename = split(filename)[1]

	# Check to see if the file exists
	if not isfile(filename):
		print filename, "DOES NOT EXIST!"

		# If file doesn't exist, create it
		decision = raw_input("Would you like to create it? (y/n) ")
		if decision == "Yes" or decision == "yes" or decision == "Y" or decision == "y":
			# create the file
			print "Creating %s" % filename
			tree = etree.ElementTree()
			log = etree.Element('log')
			# At the moment this comment gets lost after saving, but 
			# keep it so that empty xml files are saved properly.
			comment = etree.Comment("Version %s" % version)
			log.append(comment)
			indent(log)
			tree._setroot(log)
			tree.write(filename)
		else:
			print "Exiting"
			run = False

	if ( run ):
		# init
		print "Reading %s" % filename
		tree = etree.parse(filename)
		log = tree.getroot()
		userEntries = {}

	while ( run ):
		# Treat a ctrl+c as an attempt to quit
		try:
			#pre_length = readline.get_current_history_length()
			cmnd = raw_input(" > ")
			#post_length = readline.get_current_history_length()
			#print "pre = %d, post = %d" % (pre_length, post_length)

		except KeyboardInterrupt:
			print ""
			print "Exiting..."
			cmnd = "quit"
		except EOFError:
			print ""
			continue
		
		command = strip(cmnd)
		if command == "quit" or command == 'q' or command == 'exit':
			if dirty == True:
				raw_ack = raw_input("You have unsaved changes, are you sure you want to quit without saving? ")
				ack = strip(raw_ack)
				if ack == "Yes" or ack == "yes" or ack == "Y" or ack == "y":
					break
				else:
					continue
			else:
				break
		elif command == "":
			continue
		elif command == "print" or command == "p":
			printTree(log)
			# Add an extra line at the end
			print ""
		elif command == "save" or command == "s":
			save(tree, log, filename)
		elif command == "add" or command == "a":
			addEntry(log, userEntries)
		elif command == "help" or command == "h":
			showHelp()
		elif command == "list":
			showList(log)
		elif len(command) > 0 and ( command.split()[0] == "summary" or command.split()[0] == "sum" ):
			analysis = analyze(log)
			if len(command.split()) > 1:
				displayAnalysis(analysis, 0, 0, command.split()[1])
			else:
				displayAnalysis(analysis, 0, 0)
		elif len(command) > 0 and ( command.split()[0] == "psummary" or command.split()[0] == "psum" ):
			analysis = analyze(log)
			if len(command.split()) > 1:
				displayAnalysis(analysis, 0, 1, command.split()[1])
			else:
				displayAnalysis(analysis, 0, 1)
		elif len(command) > 0 and ( command.split()[0] == "report" or command.split()[0] == "rep" ):
			analysis = analyze(log)
			if len(command.split()) > 1:
				displayAnalysis(analysis, 1, 0, command.split()[1])
			else:
				displayAnalysis(analysis, 1, 0)
		elif len(command) > 0 and ( command.split()[0] == "preport" or command.split()[0] == "prep" ):
			analysis = analyze(log)
			if len(command.split()) > 1:
				displayAnalysis(analysis, 1, 1, command.split()[1])
			else:
				displayAnalysis(analysis, 1, 1)
		elif command == "xml":
			analysis = analyze(log)
			generateSkeleton(analysis, directory)
		elif command == "mkrep":
			# logfilename is passed so it can be excluded from the xml list
			preMakeReport(directory, logfilename)
		elif command == "fix":
			title = raw_input("title > ")
			newTitle = fixTitle(title)
			print "newTitle", newTitle
		elif command == "split":
			path = raw_input("path > ")
			print "cwd", getcwd()
			print "directory", directory
			print "path", path
			print split(path)
		elif command == "name":
			print filename
		elif len(command) > 0 and ( command.split()[0] == "corr" or command.split()[0] == "c" ):
			if len(command.split()) > 1:
				correctEntry(log, userEntries, (int(command.split()[1]) - 1))
			else:
				correctEntry(log, userEntries)
		elif command[:3] == "day":
			d = command[3:]
			day(log, d)
		else:
			print "\"%s\" is not a valid command" % command

def showHelp():
	print """
 Commands:
   print (p)	prints info from the xml file
   save (s)	saves changes to the xml file
   add (a)	adds an entry to the xml file
   corr (c) [#]	corrects the specified entry (default=last)
   help (h)	displays this help
   list 	prints categories & keywords
   sum [cat] 	displays the summary w/o details (hours)
   psum [cat]	displays the summary w/o details (percent)
   rep [cat] 	displays the summary w/ details (hours)
   prep [cat]	displays the summary w/ details (percent)
   day [#]	prints list of entries for a given day (default=today)
   
   xml		Generates a skeleton xml report in the same directory
   		as the work log. Categories and keywords in the work log
		correspond to titles and subjects in the xml report.  
		Details must be MANUALLY entered after examining output
		of the 'prep' command.
		
   mkrep	Converts an xml file into a pdf. Subjects are optional 
   		and do not currently appear in the pdf. 
	"""

def printTree(elem):
	for e in elem:
		if len(e) == 0:
			# Space the entries (SPACING IS NOW DONE WHEN PRINTING THE INDEX)
			#if e.tag == entryFields[0]:
			#	print ""

			# Add an extra tab if tag is too short
			if len(e.tag) < 7:
				print "%s:\t\t%s" % (e.tag, e.text)
			else:
				print "%s:\t%s" % (e.tag, e.text)
		else:
			# print index before going further down the tree
			print ""
			print "index:\t\t%s" % e.get("index")

			printTree(e)

def getCategories(log):
	categories = []

	for elem in log:
		category = elem.find("category")
		if category.text not in categories:
			categories.append(category.text)

	categories.sort()
	return categories[:]

def getKeywords(log, category):
	keywords = []

	for elem in log:
		elemCat = elem.find("category")
		# Only collect keywords for given category
		if category == elemCat.text:
			keyword = elem.find("keyword")
			# Only append new keywords
			if keyword.text not in keywords:
				keywords.append(keyword.text)

	keywords.sort()
	return keywords[:]

class TabCompleter:
	def __init__(self,items):
		self.items = items

	def complete(self,text,state):
		#!logging.debug(text)
		results = [x for x in self.items if x.startswith(text)] + [None]
		#!logging.debug(results)
		return results[state]

def promptEntry(log, userEntries, star=True, blankCat=''):
	"""  <entry index="2">
	       <day>1</day>
	       <date>2011-01-01</date>
	       <duration>0.5</duration>
	       <category>Email</category>
	       <keyword>n/a</keyword>
	       <description>Email/tech-talk</description>
	       <resolution>n/a</resolution>
	     </entry> """

	categories = getCategories(log)
	skipRemainingInput = False

	# prompt user to input each of the fields
	for i in range(len(entryFields)):
		# If field is a category or a keyword, display list of existing categories or keywords
		if entryFields[i] == 'category' and skipRemainingInput == False:
			print "  Existing categories:   %s" % ", ".join(categories)
		if entryFields[i] == 'keyword':
			if star == False and userEntries['category'] == "":
				# I'm in correct mode so AND user didn't a new category
				category = blankCat
			else:
				# Lookup current category (keyword must always be input *after* category for this to work)
				category = userEntries['category']
				
				# If the user didn't specify a category, it defaults to "other"
				if category == '':
					category = "other"
			# Get keywords for current category
			keywords = getKeywords(log, category)
			
			# Display the relevant keywords
			if skipRemainingInput == False:
				print "  Existing keywords for %s:   %s" % (category, ", ".join(keywords))

		# Add star to required fields.  Might be able to do this with string addition instead.
		if entryRequired[i] and star==True:
			promptStr = "%s*: " % entryFields[i]
		else:
			promptStr = "%s: " % entryFields[i]
		
		# Catch KeyboardInterrupt to allow the user to exit the entry process
		try:
			# Turn on tab complete
			if entryFields[i] == 'category':
				readline.parse_and_bind("tab: complete")
				completer = TabCompleter(categories[:])
				readline.set_completer(completer.complete)
			if entryFields[i] == 'keyword':
				readline.parse_and_bind("tab: complete")
				completer = TabCompleter(keywords[:])
				readline.set_completer(completer.complete)

			if skipRemainingInput == False:
				# Get user input
				userEntries[entryFields[i]] = raw_input(promptStr)

				# Remove entry items from command history
				if userEntries[entryFields[i]] != '':
					pos = readline.get_current_history_length() - 1
					#print "Removing %s from history" % readline.get_history_item(pos)
					readline.remove_history_item(pos)
			else:
				# Append blanks for fields after the ctrl+d
				userEntries[entryFields[i]] = ''
				
		except KeyboardInterrupt:
			print ""
			print "Aborting..."
			return False
			
		except EOFError:
			print ""
			print "Finishing..."
			skipRemainingInput = True
			# Append the field that was being input when the ctrl+d was encountered
			userEntries[entryFields[i]] = ''
		
		finally:
			# Turn off tab complete
			if entryFields[i] == 'category' or entryFields[i] == 'keyword':
				readline.parse_and_bind("tab: \t")

	return True

def correctEntry(log, userEntries, entryIndex=-1):
	# Assume last entry if none specified
	if entryIndex == -1:
		entryIndex = len(log) - 1

	#
	#print userEntries

	#
	elem = log[entryIndex]
	#print elem, elem.get("index")

	# 
	print ""
	print "Editing Entry #%s" % elem.get("index")
	print ""
	printTree(elem)
	print ""

	# Find the current category to pass to promptEntry to display keywords in case user leaves it blank.
	category = elem.find('category')

	# prompt for new entries
	success = promptEntry(log, userEntries, False, category.text)

	# Don't continue if data entry was aborted
	if not success:
		return

	#print userEntries

	#
	keys = userEntries.keys()
	for key in keys:
		if userEntries[key] != '':
			if key == 'date':
				# Also correct the 'day' element
				d = elem.find('day')
				d.text = userEntries[key][-2:]
			
			e = elem.find(key)
			#print e
			e.text = userEntries[key]
			#print e.text
			
			# Set the dirty flag (this could happen multiple times, but that shouldn't hurt anything)
			global dirty
			dirty = True

def addEntry(log, userEntries):
	# prompt for new entries
	success = promptEntry(log, userEntries)

	# Don't continue if data entry was aborted
	if not success:
		return

	# Set the dirty flag
	global dirty
	dirty = True

	#print userEntries
	
	# Add an entry with the appropriate index
	length = len(log) + 1
	entry = etree.SubElement(log, "entry", index="%i" % length)

	# Append the day to the entry even though the user is no longer propmpted for it
	elem = etree.SubElement(entry, "day")
	if userEntries['date'] == '':
		# if date is blank, use current day of month
		elem.text = strftime("%d")
	else:
		# Assume that the day is the last two digits of the date field.
		elem.text = userEntries['date'][-2:]

	# Loop over array, appending to entry
	for f in entryFields:
		elem = etree.SubElement(entry, f)
		# Be smarter about what is input
		#   NOTE: Eventually this might be moved to the input section 
		#   to allow corrections and immediate feedback
		if f == 'date' and userEntries[f] == '':
			# if date is left blank, use current date
			text = strftime("%Y-%m-%d")
		elif f == 'resolution' and userEntries[f] == '':
			# if resolution is left blank, assume it doesn't apply
			text = 'n/a'
		elif f == 'keyword' and userEntries[f] == '':
			# if keyword is left blank, assume it doesn't apply
			text = 'n/a'
		elif f == 'category' and userEntries[f] == '':
			# use "other" as default category
			text = 'other'
		elif f == 'description' and userEntries[f] == '':
			# use 'n/a' as default description
			text = 'n/a'
		elif f == 'duration' and userEntries[f] == '':
			# use '0' as default duration
			text = '0'
		else:
			text = userEntries[f]

		elem.text = text

def analyze(log):
	# Make sure there is something to analyze
	if len(log) == 0:
		print "There is nothing to analyze"
		return ()

	keyTotals = {}
	details = {}
	catTotals = {}
	days = []

	# do the totaling
	for elem in log:
		# Count the days for total work-day calculation
		date = elem.find("date")
		if date.text not in days:
			days.append(date.text)

		category = elem.find("category")
		if category.text not in keyTotals:
			keyTotals[category.text] = {}
			details[category.text] = {}

		keyword = elem.find("keyword")
		if keyword.text not in keyTotals[category.text]:
			keyTotals[category.text][keyword.text] = 0.0
			details[category.text][keyword.text] = []

		duration = elem.find("duration")
		# For now, assume that duration can be easily converted into floating point hours
		num_duration = float(duration.text)

		# Collect the activity descriptions
		date = elem.find("date")
		duration = elem.find("duration")
		description = elem.find("description")
		resolution = elem.find("resolution")

		details[category.text][keyword.text].append((date.text, float(duration.text), description.text, resolution.text))

		keyTotals[category.text][keyword.text] += num_duration

	#print "keyTotals", keyTotals
	#print "details", details

	c = keyTotals.keys()
	c.sort()

	#print "sorted keyTotals.keys()", c

	# Compute category totals after all categories and keywords have been collected
	recordedTotal = 0.0
	for i in c:
		k = keyTotals[i].keys()
		k.sort()

		# loop over keywords to get a category total
		catTotal = 0.0
		for j in k:
			catTotal += keyTotals[i][j]
		catTotals[i] = catTotal
		recordedTotal += catTotal
	
	#print "catTotals", catTotals
	
	# Compute theoretical work hours
	workDays = len(days)
	theoreticalHours = workDays * 8.0

	# Compute percent
	percent = recordedTotal / theoreticalHours * 100

	return (details, keyTotals, catTotals, recordedTotal, theoreticalHours, percent)

def displayAnalysis(analysis, verbose=0, percents=0, desiredCat=None):
	# Make sure the log isn't empty
	if len(analysis) == 0:
		print "Error: the log might be empty"
		return

	details = analysis[0]
	keyTotals = analysis[1]
	catTotals = analysis[2]
	recordedTotal = analysis[3]
	theoreticalHours = analysis[4]
	percent = analysis[5]

	c = keyTotals.keys()
	c.sort()

	# Make sure desiredCat exists
	if desiredCat != None:
		if desiredCat not in c:
			print "You specified a category that doesn't exist."
			return

	# Display totals
	print ""
	for i in c:
		if desiredCat == None or desiredCat == i:
			k = keyTotals[i].keys()
			k.sort()

			# print category total
			if percents == 0:
				print "%5.2f %s" % (catTotals[i], i)
			else:
				print "%4.1f%% %s" % (catTotals[i] / recordedTotal * 100.0, i)
			# loop over keywords printing totals
			for j in k:
				if percents == 0:
					print "\t%5.2f %s" % (keyTotals[i][j], j)
				else:
					print "\t%4.1f%% %s" % (keyTotals[i][j] / recordedTotal * 100.0, j)
				if verbose == 1:
					# Old way: simply print the detail lines
					#print "\n".join(details[i][j])
				
					# New way: wrap the lines so long descriptions stay readable
					for detail in details[i][j]:
						# detail[0]: date.text
						# detail[1]: float(duration.text)
						# detail[2]: description.text
						# detail[3]: resolution.text
						line = "\t\t%s ; %.2f ; %s ; %s" % (detail[0], detail[1], detail[2], detail[3])
						print textwrap.fill(line, width=(terminalWidth-16), subsequent_indent="\t\t")
						print ""
	
	print ""

	# Print total hours, theoretical hours, and percent
	print "Recorded:", recordedTotal, "hrs" 
	print "Possible:", theoreticalHours, "hrs"
	print "Complete: %0.1f%%" % percent
	print ""

def fixTitle(rawTitle):
	# Make titles more presentable since I like to use all lower case for entering log entries
	firstWord = rawTitle.split(" ")[0]
	i = 1
	lastNumIndex = 0
	while i < len(firstWord):
		if firstWord[:i].isdigit() == False:
			lastNumIndex = i - 1
			break
		i += 1
	
	if rawTitle.isupper():
		return rawTitle
	elif rawTitle.upper() == "BCDA":
		return rawTitle.upper()
	elif lastNumIndex == 0:
		# If the rawTitle doesn't start with a number, simply capitalize the words
		return rawTitle.title()
	else:
		# if rawTitle starts with a number, shorten it to a capitalized sector name
		return "%d%s" % (int(rawTitle[:lastNumIndex]), rawTitle[lastNumIndex:lastNumIndex+2].upper())

def generateSkeleton(analysis, directory):
	# Make sure the log isn't empty
	if len(analysis) == 0:
		print "Error: the log might be empty"
		return

	details = analysis[0]
	keyTotals = analysis[1]
	catTotals = analysis[2]
	recordedTotal = analysis[3]
	theoreticalHours = analysis[4]
	percent = analysis[5]
	
	# Prompt user for desired filename (Assume just a filename, not a path)
	desiredFilename = raw_input("XML report filename: ")
	# Use a default filename if it was left blank
	if desiredFilename == "":
		desiredFilename = "dummy.xml"
	# Make sure file has xml extension
	fparts = desiredFilename.split(".") 
	if len(fparts) >= 2 and fparts[len(fparts)-1] == "xml":
		pass
	else:
		desiredFilename = desiredFilename + ".xml"
	# Abort rather than overwrite an existing file
	if exists("%s/%s" % (directory, desiredFilename) ):
		print "Can't write xml report.  %s/%s already exists." % (directory, desiredFilename)
		return
	
	# Prompt user for their name
	full_name = raw_input("Your name*: ")
	
	# Author is the last word in the full name
	last_name = full_name.split()[len(full_name.split())-1]
	#!print "author", last_name

	# Get current time
	currentTime = strftime("%Y-%m-%dT%H:%M:%S")
	currentDate = strftime("%Y-%m-%d")
	#!print "time", currentTime
	
	# Create <BCDA_Staff_Monthly_Report>
	#!print "Creating %s" % filename
	tree = etree.ElementTree()
	sr = etree.Element('BCDA_Staff_Monthly_Report', version="1.0")

	date = etree.SubElement(sr, "date")
	date.text = currentDate

	author_fullname = etree.SubElement(sr, "author_fullname")
	author_fullname.text = full_name

	author = etree.SubElement(sr, "author")
	author.text = last_name

	# Get categories
	c = keyTotals.keys()
	c.sort()
	
	for i in c:
		# Get keywords
		k = keyTotals[i].keys()
		k.sort()
		
		iPercent = catTotals[i] / recordedTotal * 100.0
		iPercentStr = "%.1f%%" % iPercent
		#!print i, catTotals[i], iPercentStr
		
		for j in k:
			jPercent = keyTotals[i][j] / recordedTotal * 100.0
			jPercentStr = "%.1f%%" % jPercent
			#!print i, j, keyTotals[i][j], jPercentStr

			# Populate report with <remark>'s
			remark = etree.SubElement(sr, "remark")

			# The title as written by the staff
			#!rawtitle = etree.SubElement(remark, "rawtitle")
			#!rawtitle.text = i

			# A more presentable title (Title = category)
			title = etree.SubElement(remark, "title")
			title.text = fixTitle(i)
			
			# The subject of the entry (Subject = keyword)
			subject = etree.SubElement(remark, "subject")
			subject.text = j
			
			# The user will replace this text with actual content
			entry = etree.SubElement(remark, "entry")
			entry.text = "Details of %s" % j

			effort = etree.SubElement(remark, "effort")
			effort.text = jPercentStr

	# handle empty directory
	if directory == '':
		directory = "."

	# Write the populated staff report to disk
	indent(sr)
	tree._setroot(sr)
	tree.write("%s/%s" % (directory, desiredFilename) )

def preMakeReport(directory, logfilename):
	# Interpret empty directory as pwd
	if directory == '':
		directory = "."
	# Create a list of xml files in the same directory as the work_log
	files = listdir(directory)
	xmlFiles = []
	#!print files
	for f in files:
		if f[-4:] == ".xml" and f != logfilename:
			xmlFiles.append(f)
	#!print xmlFiles
	
	# Print xml files in the directory that aren't the work_log
	print "Found XML files:", ", ".join(xmlFiles)
	# Prompt user for desired xml file with autocomplete
	try:
		# Turn on tab complete
		readline.parse_and_bind("tab: complete")
		completer = TabCompleter(xmlFiles[:])
		readline.set_completer(completer.complete)
		
		# Get xml file
		desiredXml = raw_input("XML file to convert: ")
		
		if desiredXml != '':
			pos = readline.get_current_history_length() - 1
			#print "Removing %s from history" % readline.get_history_item(pos)
			readline.remove_history_item(pos)
		else:
			#!print "You didn't specify a file, assuming you want dummy.xml"
			desiredXml = "dummy.xml"
			
	# Catch KeyboardInterrupt to allow the user to exit the entry process
	except KeyboardInterrupt:
		print ""
		print "Aborting..."
		return False
	finally:
		# Turn off tab complete
		readline.parse_and_bind("tab: \t")

	#!print "desiredXml", desiredXml

	# Verify that the file exists
	#!print "%s/%s" % (directory, desiredXml)
	fullFilePath = "%s/%s" % (directory, desiredXml)
	if exists(fullFilePath) == False:
		print "The desired xml file (%s) doesn't exist." % fullFilePath
		return False

	# Call mkrep.makeReport()
	mkrep.makeReport(fullFilePath)

def day(log, d):
	# Day array
	dayEntries = []

	# Assume current day
	if d == '':
		currentDay = int(strftime("%d"))
	else:
		try:
			currentDay = int(d)
		except ValueError:
			print "You must specify an integer."
			currentDay = int(strftime("%d"))

	print "selected day:", currentDay
	print ""

	#
	for elem in log:
		elemDay = elem.find("day")

		if int(elemDay.text) == currentDay:
			dayEntries.append(elem)

	#print dayEntries

	hours = 0.0

	# Loop over days entries to compute & print
	for e in dayEntries:
		index = int(e.get('index'))
		duration = float(e.find('duration').text)
		category = e.find('category').text
		keyword = e.find('keyword').text
		description = e.find('description').text

		hours += duration
		print "%3d ; %2.2f ; %s - %s ; %s" % (index, duration, category, keyword, description)

	print ""
	print "Hours: %4.2f" % hours
	print "Percent: %3.1f%%" % (hours / 8.0 * 100.0)

def showList(log):
	# dictionary will contain categories as keys and keywords as value array elements
	categories = {}

	for elem in log:
		category = elem.find("category")
		if category.text not in categories:
			categories[category.text] = []
		
		keyword = elem.find("keyword")
		# if you get to a keyword, the category must already be in the dictonary
		if keyword.text not in categories[category.text]:
			categories[category.text].append(keyword.text)

	# print unsorted keywords
	#print categories
	k = categories.keys()
	k.sort()

	print "\nCategory\tKeywords\n---------\t---------"

	for i in k:
		categories[i].sort()
		# Display method 1
		#!print i
		#!print "\t\t", categories[i]
		# Display method 2
		#!print "%s\n\t\t%s" % (i, ", ".join(categories[i]))
		# Display method 3
		if len(i) < 8:
			print "%s\t\t%s" % (i, ", ".join(categories[i]))
		else:
			print "%s\t%s" % (i, ", ".join(categories[i]))

	print ""

	# print sorted keywords
	#print categories

def indent(elem, level=0):
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def save(tree, root, filename):
	# Move current file to backup
	newfilename = "%s.bup" % filename
	move(filename, newfilename)
	# Make tree presentable
	indent(root)
	# Write file
	tree.write(filename)
	global dirty
	dirty = False

if __name__ == "__main__":
	import sys
	import xml.etree.ElementTree as etree
	import textwrap
	import readline

	# Remove '-' from delim list so categories & keywords auto-complete properly
	delims = readline.get_completer_delims()
	#!print "delims = %s" % delims
	new_delims = delims.replace("-",'')
	readline.set_completer_delims(new_delims)
	#!delims2 = readline.get_completer_delims()
	#!print "delims = %s" % delims2

	from time import strftime
	from string import strip
	from os.path import isfile, split, exists
	from os import getcwd, listdir
	from shutil import move
	
	import mkrep
	
	main()
