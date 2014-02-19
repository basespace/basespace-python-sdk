
class AppSessionSemiCompact(object):
    '''
    Returned from GET Samples and AppResults
    '''
    def __init__(self):
        self.swaggerTypes = {
            'Id':'str',
            'Href': 'str',
            'UserCreatedBy':'UserCompact',
            'Status': 'str',
            'StatusSummary': 'str',
            'DateCreated': 'datetime',
        }

    def __str__(self):
        return "App session by " + str(self.UserCreatedBy) + " - Id: " + str(self.Id) + " - status: " + self.Status

    def __repr__(self):
        return str(self)

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
