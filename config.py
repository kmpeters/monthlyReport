#!/usr/bin/env python3

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

payCodeDict  = {'None':'None',
                 'VAC':'Vacation',
                 'VDS':'Vacation Donated Sick',
                 'SIC':'Sick Pay',
                 'SLF':'Sick Leave Family',
                 'SNP':'Sick No Pay',
                 'FHL':'Floating Holiday',
                 'FLS':'Family LV Sick',
                 'FLV':'Family LV Vacation',
                 'ADM':'Administrative Leave',
                 'BRV':'Bereavement',
                 'CL1':'Operations Suspended',
                 'CNP':'No Pay - Holiday Close',
                 'ENP':'Excused No Pay',
                 'FAM':'Family Leave',
                 'FSN':'Family Leave SNP',
                 'HCX':'Cancel Holiday',
                 'HFX':'Holiday Flex Time',
                 'ICA':'Incidental Absence',
                 'JUR':'Jury Duty',
                 'LOA':'Leave of Absence',
                  'MA':'Leave of Absence',
                 'MIL':'Leave of Absence',
                 'OB1':'Leave of Absence',
                 'OCD':'Leave of Absence',
                 'ONC':'Leave of Absence',
                 'PAR':'Parental Leave*',
                  'RG':'Regular',
                 'TEL':'TELECOMMUTING*',
                 'UAD':'Unpd Adm Leave',
                 'UEL':'Unpaid Entrepreneurial Lv',
                 'UML':'Unpaid Military',
                 'UOD':'Unpaid Occup Disability*',
                 'UNX':'Unexcused Absence',
                 'USL':'Unpaid Sabatical Leave',
                 'UV2':'Unsched Vacation S-2',
                 'UV3':'Unsched Vacation S-3',
                 'VNP':'Vacation No Pay',
                 'VO1':'Vac - Override - S1',
                 'VS1':'Vac in lieu of Sick - S1',
                 'WRK':'Work',
                 'HDY':'Holiday'
                 }

possible_payCodes = list(payCodeDict.keys())

jiraDict = {
  'BCDA':{'jira_key':'BCDA_GROUP', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'motor':{'jira_key':'BCDA_MOTOR', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'synApps':{'jira_key':'BCDA_SYNAPPS', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'Jira':{'jira_key':'BCDA_JIRA', 'cost_code':'PRJ1000854-PH01-APS03010501', 'wbs_code':'APS03010501'},
  'admin':{'jira_key':'BCDA_ADMIN', 'cost_code':'PRJ1000854-PH01-APS03010501', 'wbs_code':'APS03010501'},
  'Python':{'jira_key':'BCDA_PYTHON', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'spec':{'jira_key':'BCDA_SPEC', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'Stockroom':{'jira_key':'BCDA_STOCKROOM', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  # VxWorks is closed. Keep it around for a while in case old files are loaded or future VxWorks upgrade require effort
  #!'VxWorks':{'jira_key':'BCDA_VXWORKS', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'Beamline Comp Env':{'jira_key':'BCDA_BL_ENV_CONFIG', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'MEDM Replacement':{'jira_key':'BCDA_MEDM_REPLACE_IT', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'Custom Hardware':{'jira_key':'BCDA_CUSTOM_HARDWARE', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'areaDetector':{'jira_key':'BCDA_AREA_DETECTOR', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'EPICS base':{'jira_key':'BCDA_EPICS_BASE', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'EPICS clients':{'jira_key':'BCDA_EPICS_CLIENTS', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  '01BM':{'jira_key':'BCDA_01BM', 'cost_code':'PRJ1000854-PH01-APS03070202', 'wbs_code':'APS03070202'},
  '01ID':{'jira_key':'BCDA_01ID', 'cost_code':'PRJ1000854-PH01-APS03070302', 'wbs_code':'APS03070302'},
  '02BM':{'jira_key':'BCDA_02BM', 'cost_code':'PRJ1000854-PH01-APS03070402', 'wbs_code':'APS03070402'},
  '02ID-D':{'jira_key':'BCDA_02ID_A_D', 'cost_code':'PRJ1000854-PH01-APS03070602', 'wbs_code':'APS03070602'},
  '02ID-E':{'jira_key':'BCDA_02ID_A_E', 'cost_code':'PRJ1000854-PH01-APS03070702', 'wbs_code':'APS03070702'},
  '03ID':{'jira_key':'BCDA_03ID', 'cost_code':'PRJ1000854-PH01-APS03070802', 'wbs_code':'APS03070802'},
  '04ID-C':{'jira_key':'BCDA_04ID_A_C', 'cost_code':'PRJ1000854-PH01-APS03070902', 'wbs_code':'APS03070902'},
  '04ID-D':{'jira_key':'BCDA_04ID_A_D', 'cost_code':'PRJ1000854-PH01-APS03071002', 'wbs_code':'APS03071002'},
  '05BM':{'jira_key':'BCDA_05BM', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '05ID':{'jira_key':'BCDA_05ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '06BM':{'jira_key':'BCDA_06BM', 'cost_code':'PRJ1000854-PH01-APS03071302', 'wbs_code':'APS03071302'},
  '06ID-D':{'jira_key':'BCDA_06ID_A_D', 'cost_code':'PRJ1000854-PH01-APS03071202', 'wbs_code':'APS03071202'},
  '06ID-BC':{'jira_key':'BCDA_06ID_A_B_C', 'cost_code':'PRJ1000854-PH01-APS03071102', 'wbs_code':'APS03071102'},
  '07BM':{'jira_key':'BCDA_07BM', 'cost_code':'PRJ1000854-PH01-APS03071402', 'wbs_code':'APS03071402'},
  '07ID':{'jira_key':'BCDA_07ID', 'cost_code':'PRJ1000854-PH01-APS03071502', 'wbs_code':'APS03071502'},
  '08BM':{'jira_key':'BCDA_08BM', 'cost_code':'PRJ1000854-PH01-APS03071602', 'wbs_code':'APS03071602'},
  '08ID-E':{'jira_key':'BCDA_08ID_A_E', 'cost_code':'PRJ1000854-PH01-APS03071702', 'wbs_code':'APS03071702'},
  '08ID-I':{'jira_key':'BCDA_08ID_A_I', 'cost_code':'PRJ1000854-PH01-APS03071802', 'wbs_code':'APS03071802'},
  '09BM':{'jira_key':'BCDA_09BM', 'cost_code':'PRJ1000854-PH01-APS03071902', 'wbs_code':'APS03071902'},
  '09ID-B':{'jira_key':'BCDA_09ID_B', 'cost_code':'PRJ1000854-PH01-APS03073302', 'wbs_code':'APS03073302'},
  '09ID-C':{'jira_key':'BCDA_09ID', 'cost_code':'PRJ1000854-PH01-APS03072002', 'wbs_code':'APS03072002'},
  '11BM':{'jira_key':'BCDA_11BM', 'cost_code':'PRJ1000854-PH01-APS03072102', 'wbs_code':'APS03072102'},
  '11ID-B':{'jira_key':'BCDA_11ID_A_B', 'cost_code':'PRJ1000854-PH01-APS03072202', 'wbs_code':'APS03072202'},
  '11ID-C':{'jira_key':'BCDA_11ID_A_C', 'cost_code':'PRJ1000854-PH01-APS03072302', 'wbs_code':'APS03072302'},
  '11ID-D':{'jira_key':'BCDA_11ID_A_D', 'cost_code':'PRJ1000854-PH01-APS03072402', 'wbs_code':'APS03072402'},
  '12BM':{'jira_key':'BCDA_12BM', 'cost_code':'PRJ1000854-PH01-APS03072502', 'wbs_code':'APS03072502'},
  '12ID-B':{'jira_key':'BCDA_12ID_A_B', 'cost_code':'PRJ1000854-PH01-APS03072602', 'wbs_code':'APS03072602'},
  '12ID-CD':{'jira_key':'BCDA_12ID_A_C_D', 'cost_code':'PRJ1000854-PH01-APS03072702', 'wbs_code':'APS03072702'},
  '13ID':{'jira_key':'BCDA_13ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '14ID':{'jira_key':'BCDA_14ID', 'cost_code':'PRJ1000854-PH01-APS03072802', 'wbs_code':'APS03072802'},
  '15ID':{'jira_key':'BCDA_15ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '16ID':{'jira_key':'BCDA_16ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '18ID':{'jira_key':'BCDA_18ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '20ID':{'jira_key':'BCDA_20ID', 'cost_code':'PRJ1000854-PH01-APS03073202', 'wbs_code':'APS03073202'},
  '22BM':{'jira_key':'BCDA_22BM', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '22ID':{'jira_key':'BCDA_22ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '23ID':{'jira_key':'BCDA_23ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  '26ID':{'jira_key':'BCDA_26ID', 'cost_code':'PRJ1000854-PH01-APS03073402', 'wbs_code':'APS03073402'},
  '27ID':{'jira_key':'BCDA_27ID', 'cost_code':'PRJ1000854-PH01-APS03073502', 'wbs_code':'APS03073502'},
  '29ID':{'jira_key':'BCDA_29ID', 'cost_code':'PRJ1000854-PH01-APS03073602', 'wbs_code':'APS03073602'},
  '30ID':{'jira_key':'BCDA_30ID', 'cost_code':'PRJ1000854-PH01-APS03073702', 'wbs_code':'APS03073702'},
  '32ID':{'jira_key':'BCDA_32ID', 'cost_code':'PRJ1000854-PH01-APS03073802', 'wbs_code':'APS03073802'},
  '33BM':{'jira_key':'BCDA_33BM', 'cost_code':'PRJ1000854-PH01-APS03073902', 'wbs_code':'APS03073902'},
  '33ID':{'jira_key':'BCDA_33ID', 'cost_code':'PRJ1000854-PH01-APS03074002', 'wbs_code':'APS03074002'},
  '34ID-C':{'jira_key':'BCDA_34ID_A_C', 'cost_code':'PRJ1000854-PH01-APS03074102', 'wbs_code':'APS03074102'},
  '34ID-E':{'jira_key':'BCDA_34ID_A_E', 'cost_code':'PRJ1000854-PH01-APS03074202', 'wbs_code':'APS03074202'},
  '35ID':{'jira_key':'BCDA_35ID', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  'XSD':{'jira_key':'BCDA_XSD', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'Detector Group':{'jira_key':'BCDA_XSD_DETECTORS', 'cost_code':'PRJ1000854-PH01-APS030402', 'wbs_code':'APS030402'},
  'Optics Group':{'jira_key':'BCDA_XSD_OPTICS', 'cost_code':'PRJ1000854-PH01-APS03030202', 'wbs_code':'APS03030202'},
  'HPSynC':{'jira_key':'BCDA_HPSYNC', 'cost_code':'PRJ1000854-PH01-APS030107', 'wbs_code':'APS030107'},
  'MED Labs':{'jira_key':'BCDA_MED_LABS', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'APS03010502'},
  'Depo Lab':{'jira_key':'BCDA_DEPO_LAB', 'cost_code':'PRJ1000854-PH01-APS030501', 'wbs_code':'APS030501'},
  'LTP Lab':{'jira_key':'BCDA_LTP_LAB', 'cost_code':'PRJ1000854-PH01-APS030501', 'wbs_code':'APS030501'},
  'Topo Lab':{'jira_key':'BCDA_TOPO_LAB', 'cost_code':'PRJ1000854-PH01-APS030501', 'wbs_code':'APS030501'},
  'XRR Lab':{'jira_key':'BCDA_XRR_LAB', 'cost_code':'PRJ1000854-PH01-APS030501', 'wbs_code':'APS030501'},
  # Old leave cost code: 1321000-132; Formerly PAID_ABSENCE
  'Leave':{'jira_key':'LEAVE', 'cost_code':'PRJ1000854-PH01-APS03010502', 'wbs_code':'PT4037'},
  '33ID-C HFM':{'jira_key':'33IDC_HFM', 'cost_code':'PRJ1000854-PH01-APS03020220P', 'wbs_code':'APS03020220P'},
  # Upgrade projects
  'ATOMIC/3DMN Support':{'jira_key':'UPGRADE_34ID_SUPPORT', 'cost_code':'RJ1006459 U2-CON-133_MGT_0403340101.D', 'wbs_code':'0403340101'},
  'ATOMIC/3DMN Design':{'jira_key':'UPGRADE_34ID_DESIGN', 'cost_code':'PRJ1006459 U2-CON-133_DES_0403340102.D', 'wbs_code':'0403340102'},
  'ATOMIC 34ID-F':{'jira_key':'UPGRADE_34ID_F', 'cost_code':'PRJ1006459 U2-CON-133_FIN_04033401030301.D', 'wbs_code':'04033401030301'},
  '3DMN 34ID-E':{'jira_key':'UPGRADE_34ID_E', 'cost_code':'PRJ1006459 U2-CON-133_DES_0403340102.D', 'wbs_code':'0403340102'}
  }

possible_groups = list(jiraDict.keys()) + ["",]

possible_groups = sorted(possible_groups)

tooltips = {
            'date': "Date of this effort (yyyy-mm-dd)",
            'activity': "What kind of work or activity was done?",
            'group': "Beam line, group, or category for this work.",
            'effort_hrs': """report the time in hours with
with precision of 0.25, such as '6.75'.""",
            'title': "Summarize this work with a few words.",
            'description': "Describe the work that was done.",
            }

