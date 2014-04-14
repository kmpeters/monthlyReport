#!/usr/bin/env python

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
Basic configuration of choices for reporting.

:param [str] possible_activities: broad list of choices to categorize What kind of work or activity was done?
:param [str] possible_groups: list of choices where BCDA will deliver support
:param dict tooltips: for use in the GUI


*Activities* describe, broadly, the kind of work that was done.
This list helps describe our activities to upper management.

===============   =====================================================
activity          description
===============   =====================================================
administrative    purchasing, management, time reporting (Jira, 
                  Dayforce), Help Desk, licensing
ask group leader  no obvious choice, use **sparingly**, continually 
                  reviewed for re-classification
construction      building equipment or parts (separate from deployment)
deployment        installing new hardware or software (usually for the 
                  first time), this involves installing items that are 
                  already built but need configuring or adjustments to 
                  become useful
development       creating new software (or designing hardware) or new 
                  features
discussion        meetings, emails, phone calls, conferences, impromptu
documentation     writing: in manuals, wiki, email, elog, knowledge 
                  base, Jira issues, Trac, Confluence
maintenance       routine work, usually the result of troubleshooting, 
                  review, testing, discussion
review            critique of work or preparation
safety            activities related to safety such as inspections, 
                  reviews, training
testing           performance evaluation of software or hardware
training          any training or education, workshop
troubleshooting   investigation, problem identification
===============   =====================================================


We do our work for various *groups*.  The choice of which group will vary,
depending on the type of activity.  If the work involves more than one group,
try to divide the report into multiple entries, one for each separate group.
Work that supports a broad range of groups might be described as "XSD"
or "synApps".  


:note: To report vacation time, 
    sick days, lab holidays, weather-related lab closing, or similar,
    select ``activity="Administrative"``, and ``group="Leave"``.

'''

possible_activities = ['',
					    'Administrative',
					    'Ask group leader',
					    'Construction',
					    'Deployment',
					    'Development',
					    'Discussion',
					    'Documentation',
					    'Maintenance',
					    'Review',
					    'Safety',
					    'Testing',
					    'Training',
					    'Troubleshooting']

possible_groups = ['', 
					'BCDA', 'motor', 'synApps', 'Jira', 'Python', 'spec', 'Stockroom',
					'VxWorks', 'Beamline Env Config', 'MEDM Replacement',
					'Custom Hardware', 'areaDetector', 'EPICS base', 'EPICS clients',
					'01BM', '01ID', '02BM', '02ID', '03ID', '04ID',
					'05BM', '05ID', '06BM', '06ID', '07BM', '07ID',
					'08BM', '08ID', '09BM', '09ID', '11BM', '11ID',
					'12BM', '12ID', '13ID', '14ID', '15ID', '16ID',
					'18ID', '20ID', '23ID', '26ID', '27ID', '29ID',
					'30ID', '32ID', '33BM', '33ID', '34ID', '35ID',
					'XSD', 'Detector Group', 'Optics Group', 'HPSynC',
					'MED Labs', 'Depo Lab', 'LTP Lab', 'Topo Lab', 'XRR Lab',
					'Leave']

possible_groups.sort()

tooltips = {
            'date': "Date of this effort (yyyy-mm-dd)",
            'activity': "What kind of work or activity was done?",
            'group': "Beam line, group, or category for this work.",
            'effort_hrs': """report the time in hours with
with precision of 0.25, such as '6.75'.""",
            'title': "Summarize this work with a few words.",
            'description': "Describe the work that was done.",
            }

