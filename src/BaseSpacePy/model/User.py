
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException

class User(object):    
    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Email': 'str',
            'DateLastActive': 'datetime',
            'GravatarUrl': 'str',
            'HrefProjects': 'str',
            'DateCreated': 'datetime',
            'Id': 'str',
            'Href': 'str',
            'HrefRuns': 'str'
        }
    
    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''        
        Tests if the User instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :return True on success
        '''
        err = 'The User object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        
    
    def getProjects(self, api, queryPars=None):
        '''
        Returns a list of the accessible Projects for the user
         
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        self.isInit()        
        return api.getProjectByUser(queryPars=queryPars)
    
    def getRuns(self, api, queryPars=None):
        '''
        Returns a list of the accessible Runs for the user
         
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        self.isInit()
        return api.getAccessibleRunsByUser(queryPars=queryPars)
