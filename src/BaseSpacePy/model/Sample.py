#!/usr/bin/env python
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class Sample:
    '''
    Representation of a BaseSpace Sample object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'HrefFiles': 'str',
            'DateCreated': 'str',
            'SampleNumber': 'int',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact',
            'ExperimentName': 'str',
            'Run': 'RunCompact',
            'HrefGenome': 'str'
        }
    def __str__(self):
        return self.Name
    def __repr__(self):
        return str(self)
    def isInit(self):
        '''
        Is called to test if the sample instance has been initialized.
        
        Throws:
            ModelNotInitializedException - Indicated the Id variable is not set.
        '''
        if not self.Id: raise ModelNotInitializedException('The sample model has not been initialized yet') #@UndefinedVariable
        
#    def getGenome(self):
#        pass

    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to used for requesting BaseSpace access to the sample.
        
        :param scope: The scope type that is request (write|read).
        '''
        self.isInit()
        return scope + ' sample ' + str(self.Id)
    
    def getFiles(self,api, myQp={}):
        '''
        Returns a list of File objects
        
        :param api: A BaseSpaceAPI instance
        :param myQp: Query parameters to sort and filter the file list by.
        '''
        self.isInit()
        return api.getFilesBySample(self.Id,queryPars=qp(myQp))

        self.Name = None # str
        self.HrefFiles = None # str
        self.DateCreated = None # str
        self.SampleNumber = None # int
        self.Id = None # str
        self.Href = None # str
        self.UserOwnedBy = None # UserCompact
        self.ExperimentName = None # str
        self.Run = None # RunCompact
        self.HrefGenome = None # str