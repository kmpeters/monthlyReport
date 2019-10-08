# Getting Started

Use the command-line interface; the gui hasn't been maintained

* ``cli.py`` provides a generic command-line interface that shows all of the available options when entering data
* ``exampleRa.py`` is an example of how the default cli.py settings can be overridden to make the program more usable
* ``ra.py`` is Kevin's highly-customized cli (ra is short for report append)

## Starting the program

cli.py accepts an optional filename argument

```
$ python cli.py [filename]
```
If no filename is specified, cli.py offers to create a file named ``work_log.xml`` in the current working directory.

## Available commands

The help command ('help' or 'h') prints a somewhat helpful message:
```
 > h

 Commands:
   help (h)      displays this help
   groups (lg)   list all available groups
   codes (pc)    list all available pay codes
   tpc           Toggle prompt for pay code when adding entries

   add (a)       adds an entry to the log file
   save (s)      saves changes to the log file
   corr (c) [#]  corrects the specified entry (default=last)

   chd           set a custom date to be used as the default
   cld           clear the custom date
   lsd           list the default date

   day (d) [#]   prints list of entries for a given day (default=today)
   dsum (ds) [#] prints summary of entries for a given day (default=today)
   
   wtab (wt) [#] prints a table of hours in green-sheet format
   wsum (ws) [#] displays the week summary w/o details (hours)
   wrep (wr) [#] displays the week summary w/ details (hours)
   
   wd [#]        prints a table in dayforce format
   
   sum [cat]     displays the month summary w/o details (hours)
   psum [cat]    displays the month summary w/o details (percent)
   rep [cat]     displays the month summary w/ details (hours)
   prep [cat]    displays the month summary w/ details (percent)

   print (p) [#] prints info from the log file (default=everything)
   list [label ...] list the labels used in the log. Default labels are
                 activity, group and title.

   xml           Generates a skeleton xml report in the same directory
                 as the work log. Categories and keywords in the work log
                 correspond to titles and subjects in the xml report.  
                 Details must be MANUALLY entered after examining output
                 of the 'prep' command.
                
   mkrep         Converts an xml file into a pdf. Titles are optional 
                 and do not currently appear in the pdf.
                
   ch            Bulk title change. Make a BACKUP of your log before using
                 this feature, since it hasn't been extensively tested yet.
    
 > 
```

## Commonly-used commands

### a (add)

`` > a ``

This initiates the data entry process for a new entry in the work log.  The user is prompted for the following info:
```
date - The date in YYYY-MM-DD format.  Leaving the date blank will result in today's date being used.
duration - Duration of effort (floating point number of hours).  Leaving the duration blank will result in 0.0 being used.
activity - A high-level categorization of the type of work that was completed.  A valid option is required and tab-completion is available.
group - The group for which the work was done. A valid option is required.  Tab completion is available but much less useful.
title - A user-specified title for the work being done.  This can't be empty.  Tab-completion is available for previously-entered titles of the current group.
description - Details of the work.  This can't be empty.
payCode - Dayforce payCode associated with the work.  The 'tpc' command can be used to turn this prompt off, which results in RG being used for every entry (the payCode can still be modified when correcting entries).
```

### s (save)

`` > s ``

Saves the log file after copying the previous log file to <filename>.bup.

### c (corr)

`` > c [#]``

This initiates the correction of an entry.  If an entry index is given (indices are the first column in the output of the 'd' command), that entry is correct.  If no entry is given, the last entry is corrected.  The user is prompted for the same info that was entered with the 'a' command.  No input is required at any of the prompts.  Non-empty reponses to the prompts will overwrite the previously-entered data.  The correction of an entry can be ended prematurely by typing 'Ctrl+d', which abandons any corrections for the current prompt.

### d (day)

`` > d [#]``

This command displays the entries for the specified day (or today if no day is specified).  The argument is an integer.

### wt (wtab)

`` > wt [#] [#] [#]...``

The 'wt' command displays a week table with groups and effort totals.  The optional arguments are integers.  If no arguments are specified, the current week is displayed.  Negative integers can be used to display previous weeks (-1 = last week).  Positive integers can be used to display specific days.

### wd

`` > wd [#] [#] [#]...``

The 'wd' command displays much of the same info as the 'wt' command in the format that is currently used by dayforce.

### rep

`` > rep [group]``

The 'rep' command prints a summary of the effort for the month with the details of each event.  By default the entries are sorted by the following: group, title, date, index


