#!/usr/bin/env python

class AppSession:
    '''
    AppLaunch contains the data returned 
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Id':'str',
            'Href': 'str',
            'Type': 'str',
            'UserCreatedBy':'User',
            'DateCreated': 'str',
            'Status':'str',
            'StatusSummary': 'str',
            'Application':'Application',
            'References':'list<AppSessionLaunchObject>'
#            'Projects': 'list<Project>',
#            'Samples': 'list<Sample>',
#            'Analyses': 'list<Analysis>',
        }
        
    def __str__(self):
        return "App Launch by " + str(self.UserCreatedBy) + " on " + str(self.References)
    def __repr__(self):
        return str(self)
    
    def __serializeReferences__(self,api):
        ref = []
        for r in self.References:
            res = r.__serializeObject__(api)
            ref.append(res)
        self.References =  ref
        return self
             


# deprecated
#    def getLaunchType(self):
#        '''
#        Returns a list [<launch type name>, list of objects] where <launch type name> is one of Projects, Samples, Analyses 
#        '''
#        try: 
#            self.Projects
#            return ['Projects', self.Projects]
#        except: e=1
#        try: 
#            self.Samples
#            return ['Samples', self.Samples]
#        except: e=1
#        try: 
#            self.Analyses
#            return ['Analyses', self.Analyses]
#        except: e=1
            
        self.UserUserCreatedBy = None #  The user that triggered your application
        self.Id                = None
        self.Status            = None
        self.StatusSummary     = None
        self.Href              = None #  The URI of BaseSpace
        self.DateCreated       = None #  The datetime the user acted in BaseSpace
        self.References        = None