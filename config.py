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

:param [str] possible_customers: broad list of choices to categorize Who initiated this work?
:param [str] possible_activities: broad list of choices to categorize What kind of work or activity was done?
:param [str] possible_groups: list of choices where BCDA will deliver support
:param dict tooltips: for use in the GUI


*Customers* initiate, or drive, the work.
The list of a few, short categories is not likely to change.

===============  =====================================================
customer         description
===============  =====================================================
XSD              XSD-maintained beam lines, labs, and staff
non-XSD          Any other beam lines, labs, offsite, whatever
Infrastructure   Includes technical work initiated due to 
                 broad interest (such as support for oscilloscopes)
BCDA             Usually administrative matters or other group, 
                 division, or lab directed work.  Examples would
                 include training, vacation, holidays, or sick days.
                 Also, non-technical work that benefits the group
                 would use this (such as creating/maintaining the 
                 monthly reporting software or the web pages).
===============  =====================================================

*Activities* describe, broadly, the kind of work that was done.
This list helps describe our activities to upper management.

===============  =====================================================
activity         description
===============  =====================================================
Operations       A very broad category.  New work goes here.
Troubleshooting  Work done to diagnose a problem and determine a 
                 solution.
Maintenance      Work done to implement changes to existing things
                 and to apply lessons learned as a result of other
                 activities such as from troubleshooting.
Communications   Meetings, emails, conversations, presentations
Projects         Category to describe new technical efforts that are
                 not yet a part of the activities above.
Administrative   Training, various kinds of leave, ...
===============  =====================================================


We do our work for various *groups*.  The choice of which group will vary,
depending on the type of activity.  If the work involves more than one group,
try to divide the report into multiple entries, one for each separate group.
Work that supports a broad range of groups might be described as "Infrastructure"
or "General".  Only use "Other" to describe work for which none of the choices in 
the list seems to fit.  This will flag the list of groups for revision.


:note: To report vacation time, 
    sick days, lab holidays, weather-related lab closing, or similar,
    select ``customer="BCDA"``, ``activity="Administrative"``, and
    ``group="Leave"``.

'''


possible_customers = ['', 'XSD', 'non-XSD', 'Infrastructure', 'BCDA']
possible_activities = ['', 
                        'Operations',
                        'Troubleshooting', 
                        'Maintenance', 
                        'Communications', 
                        'Projects', 
                        'Administrative']

possible_groups = ['', 
                    '01ID', '01BM', '02ID', '02BM', '03ID', '04ID', 
                    '05ID', '05BM', '06ID', '06BM', '07BM', '07ID', 
                    '08ID', '08BM', '09ID', '10ID', '11BM', '11ID', 
                    '12BM', '12ID', '15ID', '16ID', '18ID', '20ID',
                    '21ID', '26ID', '28ID', '29ID', '30ID', '32ID', 
                    '33BM', '33ID', '34ID', 
                    'AMO Group', 'BCDA', 'Detector Group', 
                    'Detectors', 'General', 'SPEC', 'SSM', 'Other',
                    'Infrastructure',
                    'Training', 'Leave', 'Topo Lab', 'Offsite',
                    'AES-MED', 'HPSynC', 
                    'LTP Lab'
                    'Metrology Lab', 'Optics Group', 
                    'Thermal Fatigue Experiment (TFE)', 
                 ]
possible_groups.sort()

tooltips = {
            'date': "Date of this effort (yyyy-mm-dd)",
            'customer': "Who initiated this work?",
            'activity': "What kind of work or activity was done?",
            'group': "Beam line, group, or category for this work.",
            'effort_hrs': """report the time in hours with
with precision of 0.25, such as '6.75'.""",
            'title': "Summarize this work with a few words.",
            'description': "Describe the work that was done.",
            }

