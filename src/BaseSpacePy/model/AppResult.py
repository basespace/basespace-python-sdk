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

class AppResult(object):

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Status': 'str',        # will be deprecated
            'Description': 'str',
            'StatusSummary': 'str',
            'HrefFiles': 'str',
            'DateCreated': 'datetime',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact',
            'StatusDetail': 'str',
            'HrefGenome': 'str',
            'AppSession':'AppSessionSemiCompact',
            'References':'dict',
            'TotalSize':'int',
            'Properties': 'PropertyList',
        }
    def __str__(self):
        return "AppResult: " + self.Name #+ " - " + str(self.Status)
    def __repr__(self):
        return str(self)
    
    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to be used for requesting BaseSpace access to the object
        
        :param scope: The scope-type that is request (write|read)
        '''
        self.isInit()
        return scope + ' appresult ' + str(self.Id) 
        
    def isInit(self):
        '''
        Is called to test if the Project instance has been initialized
        
        Throws:
            ModelNotInitializedException  - if the instance has not been populated.
        '''
        try: self.Id
        except: raise ModelNotInitializedException('The AppResult model has not been initialized yet')

    def getReferencedSamplesIds(self):
        '''
        Return a list of sample ids for the samples referenced.
        '''
        res= []
        for s in self.References:
            if s['Type']=='Sample':
                id = s['HrefContent'].split('/')[-1]
                res.append(id)
        return res
        
    
    def getReferencedSamples(self,api):
        '''
        Returns a list of sample objects references by the AppResult. NOTE this method makes one request to REST server per sample
        '''
        res = []
        ids = self.getReferencedSamplesIds()
        for id in ids:            
            sample = api.getSampleById(id)
            res.append(sample)                            
        return res
    
    def getFiles(self,api,myQp={}):
        '''
        Returns a list of file objects
        
        :param api: An instance of BaseSpaceAPI
        :param myQp: (Optional) QueryParameters for sorting and filtering the file list 
        '''
        self.isInit()
        return api.getAppResultFiles(self.Id,queryPars=qp(myQp))
       
    def uploadFile(self, api, localPath, fileName, directory, contentType):
        '''
        Uploads a local file to the BaseSpace AppResult
        
        :param api: An instance of BaseSpaceAPI
        :param localPath: The local path of the file
        :param fileName: The filename
        :param directory: The remote directory to upload to
        :param contentType: The content-type of the file
        '''
        self.isInit()
        return api.appResultFileUpload(self.Id,localPath, fileName, directory, contentType)

#    def uploadMultipartFile(self, api, localPath, fileName, directory, contentType,tempDir='',cpuCount=1,partSize=10,verbose=0):
#        '''
#        Upload a file in multi-part mode. Returns an object of type MultipartUpload used for managing the upload.
#        
#        :param api:An instance of BaseSpaceAPI
#        :param localPath: The local path of the file
#        :param fileName: The filename
#        :param directory: The remote directory to upload to
#        :param contentType: The content-type of the file
#        :param cpuCount: The number of CPUs to used for the upload
#        :param partSize:
#        '''
#        self.isInit()
#        return api.multipartFileUpload(self.Id, localPath, fileName, directory, contentType, tempDir,cpuCount,partSize,verbose=verbose)

        self.Name               = None
        self.Description        = None
        self.StatusSummary      = None
        self.HrefFiles          = None
        self.DateCreated        = None
        self.Id                 = None
        self.Href               = None
        self.UserOwnedBy        = None # UserCompact
        self.StatusDetail       = None
        self.HrefGenome         = None
        self.References         = None
