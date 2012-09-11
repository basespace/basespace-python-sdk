"""
Copyright 2012 Illumina

    Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
        }
        
    def __str__(self):
        return "App session by " + str(self.UserCreatedBy) + " - Id: " + str(self.Id) + " - status: " + self.Status
    def __repr__(self):
        return str(self)
    
    def __serializeReferences__(self,api):
        ref = []
        for r in self.References:
            res = r.__serializeObject__(api)
            ref.append(res)
        self.References =  ref
        return self
    
    def canWorkOn(self):
        return self.Status.lower() in ['running']
    
    def setStatus(self,api,Status,Summary):
        '''
        Sets the status of the AppSession (note: once set to 'completed' or 'aborted' no more work can be done to the instance)
        
        :param api: An instance of BaseSpaceAPI
        :param Status: The status value, must be completed, aborted, working, or suspended
        :param Summary: The status summary
        '''
        if self.Status.lower()=='complete' or self.Status.lower()=='aborted':
            raise Exception('The status of AppSession=' + str(self) + " is " + self.Status + ",\
             no further status changes are allowed.")
        
        # To prevent the AppResult object from being in an inconsistent state
        # and having two identical objects floating around, we update the current object
        # and discard the returned object
        newSession = api.setAppSessionState(self.Id, Status, Summary)
        self.Status         = newSession.Status
        self.StatusSummary  = newSession.StatusSummary
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