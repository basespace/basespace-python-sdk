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

class Run(object):

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Number': 'int',
            'HrefFiles': 'str',
            'HrefSamples': 'str',
            'UserUploadedBy': 'UserCompact',
            'UserOwnedBy': 'UserCompact',
            'DateUploadCompleted': 'datetime',
            'DateUploadStarted': 'datetime',
            'HrefBaseSpaceUI': 'str',
            'Id': 'str',
            'Href': 'str',
            'ExperimentName': 'str',
            'Status': 'str',
            'DateCreated': 'datetime',
            'DateModified': 'datetime',
            'Properties': 'PropertyList',
            'ReagentBarcode': 'str',
            'FlowcellBarcode': 'str',
            'TotalSize': 'int',                                        
        }
    def __str__(self):
        return self.Name
    def __repr__(self):
        return str(self)

    def isInit(self):
        '''
        Tests if the Project instance has been initialized
        
        Throws: ModelNotInitializedException  - if the instance has not been populated.
        '''
        try:
            self.Id
        except:
            raise ModelNotInitializedException('The Run model has not been initialized yet')
    
    def getFiles(self, api, queryPars=None):
        '''
        Returns a list of File objects associated with the Run
        
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering 
        '''
        self.isInit()
        if queryPars is None:
            queryPars = qp()
        return api.getRunFilesById(self.Id, queryPars=queryPars)
       
    def getSamples(self, api, queryPars=None):
        '''
        Returns a list of Sample objects associated with the Run
        
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering 
        '''
        self.isInit()
        if queryPars is None:
            queryPars = qp()
        return api.getRunSamplesById(self.Id, queryPars=queryPars)
