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

from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class Sample:
    '''
    Representation of a BaseSpace Sample object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'HrefFiles': 'str',
            'DateCreated': 'datetime',
            'SampleNumber': 'int',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact',
            'ExperimentName': 'str',
            'Run': 'RunCompact',
            'HrefGenome': 'str',
            'IsPairedEnd':'int',
            'Read1':'int',
            'Read2':'int',
            'NumReadsRaw':'int',
            'NumReadsPF':'int',
            'References':'dict'
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
    
    def getReferencedAppResults(self,api):
        '''
        Return the AppResults referenced by this sample. Note the returned AppResult objects
        do not have their "References" field set, to get a fully populate AppResult object
        you must use getAppResultById in BaseSpaceAPI.
        '''
        res = []
        for s in self.References:
            if s['Type']=='AppResult':
                jsonAppResult = s['Content']
                myAR = api.__serializeObject__(jsonAppResult,"AppResult")
                res.append(myAR)
        return res
    
    def getFiles(self,api, myQp={}):
        '''
        Returns a list of File objects
        
        :param api: A BaseSpaceAPI instance
        :param myQp: Query parameters to sort and filter the file list by.
        '''
        self.isInit()
        return api.getFilesBySample(self.Id,queryPars=qp(myQp))

        self.Name           = None # str
        self.HrefFiles      = None # str
        self.DateCreated    = None # datetime
        self.SampleNumber   = None # int
        self.Id             = None # str
        self.Href           = None # str
        self.UserOwnedBy    = None # UserCompact
        self.ExperimentName = None # str
        self.Run            = None # RunCompact
        self.HrefGenome     = None # str
        self.IsPairedEnd    = None # int
        self.Read1          = None # int
        self.Read2          = None # int
        self.NumReadsRaw    = None # int
        self.NumReadsPF     = None # int
        self.References     = None # dict
