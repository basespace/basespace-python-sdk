#!/usr/bin/env python
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException

class Project:
    '''
    Represents a BaseSpace Project object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'HrefSamples': 'str',
            'HrefAppResults': 'str',
            'DateCreated': 'str',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact'
        }
    
    def __str__(self):
        return self.Name + ' - id=' + str(self.Id)
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''
        Is called to test if the Project instance has been initialized.
        
        Throws:
            ModelNotInitializedException - Indicates the object has not been populated yet.
        '''
        if not self.Id: raise ModelNotInitializedException('The project model has not been initialized yet')
    
    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to used for requesting BaseSpace access to the object
        
        :param scope: The scope-type that is request (write|read)
        '''
        self.isInit()
        return scope + ' project ' + str(self.Id)
    
    def getAppResults(self,api,statuses=[]):
        '''
        Returns a list of Analysis objects.
        
        :param api: An instance of BaseSpaceAPI
        :param statuses: An optional list of statuses
        '''
        self.isInit()
        return api.getAppResultsByProject(self.Id,statuses=statuses)
        
    def getSamples(self,api):
        '''
        Returns a list of Sample objects.
        
        :param api: An instance of BaseSpaceAPI
        '''
        self.isInit()
        return api.getSamplesByProject(self.Id)
    
    def createAppResult(self,api,name,desc,appSessionId=None):
        '''
        Return a newly created app result object
        
        :param api: An instance of BaseSpaceAPI
        :param name: The name of the app result
        :param desc: A describtion of the app result
        '''
        self.isInit()
        return api.createAppResult(self.Id,name,desc,appSessionId=appSessionId)

        self.Name           = None # str
        self.HrefSamples    = None # str
        self.HrefAppResults = None # str
        self.DateCreated    = None # str
        self.Id             = None # str
        self.Href           = None # str
        self.UserOwnedBy    = None # UserCompact