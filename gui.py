#!/usr/bin/env python

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
A GUI for Kevin Peterson's monthly reporting package

Built using the Traits library from the
Enthought Python Distribution. 
'''


from traits.api import *    #@UnusedWildImport
from traitsui.api import *  #@UnusedWildImport

import config


class Report( HasTraits ):
    '''
    describes a single report of work
    '''
    customer = Enum(config.possible_customers, value="")
    activity = Enum(config.possible_activities, value="")
    group = Enum(config.possible_groups, value="")
    description = Str
    title = Str
    effort_hrs = Float
    # date: provide some record of when this entry was created or modified
    _dirty = Bool(False)    # True once the field is edited

    addBtn = Button('Add')
    resetBtn = Button('Reset')
    cancelBtn = Button('Cancel')
    
    def _addBtn_fired(self):
        if len(self.customer) == 0:
            raise Exception, "You must choose a customer."
        if len(self.activity) == 0:
            raise Exception, "You must choose an activity."
        if len(self.group) == 0:
            raise Exception, "You must choose a group."
        if len(self.title) == 0:
            raise Exception, "You need a title."
        if self.effort_hrs < 0:
            raise Exception, "You need to estimate the effort for this entry."
        if len(self.description) == 0:
            raise Exception, "Provide some description of the activity."
        doReportAdd(self.customer, self.activity, self.group, self.title,
                    self.effort_hrs, self.description)
    
    def _resetBtn_fired(self):
        # TODO: finish this work
        print "reset button pressed"
    
    def _cancelBtn_fired(self):
        # TODO: finish this work
        print "click [x] in the window's title bar to quit"

    traits_view = View(
        Item('customer', tooltip=config.tooltips['customer']),
        Item('activity', tooltip=config.tooltips['activity']),
        Item('group', tooltip=config.tooltips['group']),
        HGroup(
               Item('title', springy=True, tooltip=config.tooltips['title']),
               Item('effort_hrs', tooltip=config.tooltips['effort_hrs']),
               ),
        Item('description', 
             tooltip=config.tooltips['description'], 
             resizable=True, springy=True, 
             editor=TextEditor(), style='custom'),
        HGroup(
            UItem('addBtn', tooltip="submit this report"),
            Spring(),
            UItem('resetBtn', tooltip="revert all changes to this form data"),
            Spring(),
            UItem('cancelBtn', tooltip="discard this form data"),
        ),
        resizable = True,
        width = 600,
        height = 400,
    )


def doReportAdd(*args, **kw):
    '''
    Example routine to handle the request to enter a new report
    of work into the current database.  This routine has a trivial
    response, since no database is yet connected and the calling
    signature is not yet confirmed.
    '''
    import pprint
    print "args: ",
    pprint.pprint(args)
    print "kw: ",
    pprint.pprint(kw)


if __name__ == '__main__':
    rep = Report()
    rep.configure_traits()
