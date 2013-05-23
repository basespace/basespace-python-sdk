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

from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class Project:
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
    
    def getAppResults(self,api,myQp={},statuses=[]):
        '''
        Returns a list of AppResult objects.
        
        :param api: An instance of BaseSpaceAPI
        :param statuses: An optional list of statuses
        '''
        self.isInit()
        return api.getAppResultsByProject(self.Id, queryPars=qp(myQp),statuses=statuses)
        
    def getSamples(self,api):
        '''
        Returns a list of Sample objects.
        
        :param api: An instance of BaseSpaceAPI
        '''
        self.isInit()
        return api.getSamplesByProject(self.Id)
    
    def createAppResult(self,api,name,desc,appSessionId=None,samples=[]):
        '''
        Return a newly created app result object
        
        :param api: An instance of BaseSpaceAPI
        :param name: The name of the app result
        :param desc: A describtion of the app result
        '''
        self.isInit()
        return api.createAppResult(self.Id,name,desc,appSessionId=appSessionId,samples=samples)

        self.Name           = None # str
        self.HrefSamples    = None # str
        self.HrefAppResults = None # str
        self.HrefBaseSpaceUI = None # str
        self.DateCreated    = None # str
        self.Id             = None # str
        self.Href           = None # str
        self.UserOwnedBy    = None # UserCompact
