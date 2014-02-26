
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException, AppSessionException

class AppSessionSemiCompact(object):
    '''
    Returned from GET Samples and AppResults
    '''
    def __init__(self):
        self.swaggerTypes = {
            'Id':'str',
            'Href': 'str',
            'Name': 'str',
            'UserCreatedBy':'UserCompact',
            'Status': 'str',
            'StatusSummary': 'str',
            'Application':'Application',
            'DateCreated': 'datetime',
            'ModifiedOn': 'datetime',
        }

    def __str__(self):
        return "App session by " + str(self.UserCreatedBy) + " - Id: " + str(self.Id) + " - status: " + self.Status

    def __repr__(self):
        return str(self)

    def isInit(self):
        '''        
        Tests if the AppSession instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :return True on success
        '''
        err = 'The AppSession object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        

    def canWorkOn(self):
        '''
        Tests if the AppSession can be modified.
        
        :returns: True if the AppSession can be modified, False otherwise
        '''
        self.isInit()
        return self.Status in ['Running', 'NeedsAttention', 'TimedOut']

    def setStatus(self, api, Status, Summary):
        '''
        Set the Status and StatusSummary of an AppSession in BaseSpace.
        Note - once Status is set to Completed or Aborted, no further changes can made.
        
        :param api: An instance of BaseSpaceAPI
        :param Status: The status value, must be: completed, aborted, working, or suspended
        :param Summary: The status summary
        :returns: The current instance with updated Status and StatusSummary
        '''
        self.isInit()
        if self.Status=='Complete' or self.Status=='Aborted':
            raise AppSessionException("Status changes aren't allowed for AppSessions with status %s" % self.Status)                                                    
        newSession = api.setAppSessionState(self.Id, Status, Summary)
        self.Status = newSession.Status
        self.StatusSummary = newSession.StatusSummary
        return self
