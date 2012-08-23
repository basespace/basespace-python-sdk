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
            'HrefAnalyses': 'str',
            'DateCreated': 'str',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact'
        }
    
    def __str__(self):
        return self.Name
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
    
    def getAnalyses(self,api):
        '''
        Returns a list of Analysis objects.
        
        :param api: An instance of BaseSpaceAPI
        '''
        self.isInit()
        return api.getAnalysisByProject(self.Id)
        
    def getSamples(self,api):
        '''
        Returns a list of Sample objects.
        
        :param api: An instance of BaseSpaceAPI
        '''
        self.isInit()
        return api.getSamplesByProject(self.Id)
    
    def createAnalysis(self,api,name,desc):
        '''
        Return a newly created Analysis object
        
        :param api: An instance of BaseSpaceAPI
        :param name: The name of the analysis
        :param desc: A describtion of the analysis
        '''
        self.isInit()
        return api.createAnalyses(self.Id,name,desc)

        # 
        self.Name = None # str

        # 
        self.HrefSamples = None # str

        # 
        self.HrefAnalyses = None # str

        # 
        self.DateCreated = None # str

        # 
        self.Id = None # str

        # 
        self.Href = None # str

        # 
        self.UserOwnedBy = None # UserCompact