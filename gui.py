#!/usr/bin/env python

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
A GUI for Kevin Peterson's monthly effort reporting package

Built using the Traits library from the
Enthought Python Distribution. 
'''


from traits.api import *    #@UnusedWildImport
from traitsui.api import *  #@UnusedWildImport

import datetime
import config


class Entry( HasTraits ):
    '''
    describes a single entry of a work report
    '''
    customer = Enum(config.possible_customers, value="")
    activity = Enum(config.possible_activities, value="")
    group = Enum(config.possible_groups, value="")
    description = Str
    title = Str
    effort_hrs = Float
    date = Str
    _dirty = Bool(False)    # True once the field is edited
    _created = Str          # ISO8601 timestamp when this entry was created

    addBtn = Button('Add')
    resetBtn = Button('Reset')
    cancelBtn = Button('Cancel')
    
    def _date_default(self):
        return str(datetime.date.today())
    
    def __created_default(self):
        '''creation time, formatted per ISO8601'''
        return self.iso8601()
    
    def iso8601(self):
        '''current time, formatted per ISO8601'''
        return "T".join(str(datetime.datetime.now()).split())

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
        doEntryAdd(self.customer, self.activity, self.group, self.title,
                    self.effort_hrs, self.description)
        self._dirty = False
    
    def _resetBtn_fired(self):
        # TODO: finish this work
        print "reset button pressed"
        self._dirty = False
    
    def _cancelBtn_fired(self):
        # TODO: finish this work
        print "click [x] in the window's title bar to quit"
        self._dirty = False
    
    def _customer_changed(self):
        self._dirty = True
    
    def _activity_changed(self):
        self._dirty = True
    
    def _group_changed(self):
        self._dirty = True
    
    def _title_changed(self):
        self._dirty = True
    
    def _effort_hrs_changed(self):
        self._dirty = True
    
    def _description_changed(self):
        self._dirty = True

    traits_view = View(
        Item('date', tooltip=config.tooltips['date']),
        Item('customer', tooltip=config.tooltips['customer']),
        Item('activity', tooltip=config.tooltips['activity']),
        Item('group', tooltip=config.tooltips['group'], 
              #style  = 'custom', 
              #editor = EnumEditor(values=group.values, mode='list', cols=3),
              ),
        HGroup(
               Item('title', springy=True, tooltip=config.tooltips['title']),
               Item('effort_hrs', tooltip=config.tooltips['effort_hrs']),
               ),
        Item('description', 
             tooltip=config.tooltips['description'], 
             resizable=True, springy=True, 
             editor=TextEditor(), style='custom'),
        HGroup(
            UItem('addBtn', tooltip="submit this entry"),
            Spring(),
            UItem('resetBtn', tooltip="revert all changes to this form data"),
            Spring(),
            UItem('cancelBtn', tooltip="discard this form data"),
        ),
        resizable = True,
        width = 600,
        height = 400,
    )
    
    def __str__(self):
        '''default string representation'''
        return "%s, %s, %s, %s" % (self.date, self.customer, self.activity, self.group)
    
    def __repr__(self):
        '''alternate string representation'''
        return self._created


class EntryLog( HasTraits ):
    name = Str
    entry_list = List(Entry)


def doEntryAdd(*args, **kw):
    '''
    Example routine to handle the request to enter a new entry
    describing work into the current database.  This routine has a trivial
    response, since no database is yet connected and the calling
    signature is not yet confirmed.
    '''
    import pprint
    print "args: ",
    pprint.pprint(args)
    print "kw: ",
    pprint.pprint(kw)


if __name__ == '__main__':
    rep = Entry()
    log = EntryLog(name = "my_log", entry_list = [rep])
    log.configure_traits()
    print rep
    print repr(rep)
