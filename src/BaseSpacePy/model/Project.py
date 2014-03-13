
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class Project(object):
    '''
    Represents a BaseSpace Project object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'HrefSamples': 'str',
            'HrefAppResults': 'str',
            'HrefBaseSpaceUI': 'str',
            'DateCreated': 'datetime',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact',
            'Properties': 'PropertyList',
        }
    
    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)
            
    def isInit(self):
        '''        
        Tests if the Project instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :returns: True on success
        
        '''
        err = 'The Project object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        
    
    def getAccessStr(self, scope='write'):
        '''
        Returns the scope-string to used for requesting BaseSpace access to the object
        
        :param scope: The scope-type that is request (write|read)
        '''
        self.isInit()
        return scope + ' project ' + str(self.Id)
    
    def getAppResults(self, api, queryPars=None, statuses=None):
        '''
        Returns a list of AppResult objects.
        
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :param statuses: An optional list of statuses, eg. 'complete'
        '''
        self.isInit()        
        return api.getAppResultsByProject(self.Id, queryPars=queryPars, statuses=statuses)
        
    def getSamples(self, api, queryPars=None):
        '''
        Returns a list of Sample objects.
        
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        self.isInit()        
        return api.getSamplesByProject(self.Id, queryPars=queryPars)
    
    def createAppResult(self, api, name, desc, samples=None, appSessionId=None):
        '''
        Return a newly created app result object
        
        :param api: An instance of BaseSpaceAPI
        :param name: The name of the app result
        :param desc: A description of the app result
        :param samples: (Optional) A list of one or more Samples Ids that the AppResult is related to
        :param appSessionId: (Optional) If no appSessionId is given, the id used to initialize the BaseSpaceAPI instance will be used. If appSessionId is set equal to an empty string, a new appsession will be created for the appresult object 
        '''
        self.isInit()        
        return api.createAppResult(self.Id, name, desc, samples=samples, appSessionId=appSessionId)
