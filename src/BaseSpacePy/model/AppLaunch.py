#!/usr/bin/env python

class AppLaunch:
    '''
    AppLaunch contains the data returned 
    '''

    def __init__(self):
        self.swaggerTypes = {
            'User': 'User',
            'OriginatingUri': 'str',
            'Type': 'str',
            'DateCreated': 'str',
            'Projects': 'list<Project>',
            'Samples': 'list<Sample>',
            'Analyses': 'list<Analysis>',
        }
        
    def __str__(self):
        return "App Launch by " + str(self.User)
    def __repr__(self):
        return str(self)
    
    def getLaunchType(self):
        '''
        Returns a list [<launch type name>, list of objects] where <launch type name> is one of Projects, Samples, Analyses 
        '''
        try: 
            self.Projects
            return ['Projects', self.Projects]
        except: e=1
        try: 
            self.Samples
            return ['Samples', self.Samples]
        except: e=1
        try: 
            self.Analyses
            return ['Analyses', self.Analyses]
        except: e=1
            
        self.User           = None #  The user that triggered your application
        self.OriginatingUri = None #  The URI of BaseSpace
        self.Type           = None #  Should be "trigger"
        self.DateCreated    = None #  The datetime the user acted in BaseSpace
        self.Projects       = None #  (optional) A list of Projects
        self.Samples        = None #  (optional) A list of Samples
        self.Analyses       = None #  (optional) A list of Analyses