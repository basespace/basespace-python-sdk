#!/usr/bin/env python
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class AppResult:

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Status': 'str',
            'Description': 'str',
            'StatusSummary': 'str',
            'HrefFiles': 'str',
            'DateCreated': 'str',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact',
            'StatusDetail': 'str',
            'HrefGenome': 'str'
        }
    def __str__(self):
        return self.Name + " - " + str(self.Status)
    def __repr__(self):
        return str(self)
    
    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to be used for requesting BaseSpace access to the object
        
        :param scope: The scope-type that is request (write|read)
        '''
        self.isInit()
        return scope + ' analysis ' + str(self.Id) 
        
    def isInit(self):
        '''
        Is called to test if the Project instance has been initialized
        
        Throws:
            ModelNotInitializedException  - if the instance has not been populated.
        '''
        try: self.Id
        except: raise ModelNotInitializedException('The Analysis model has not been initialized yet')
    
    def getFiles(self,api,myQp={}):
        '''
        Returns a list of file objects
        
        :param api: An instance of BaseSpaceAPI
        :param myQp: (Optional) QueryParameters for sorting and filtering the file list 
        '''
        self.isInit()
        return api.getAnalysisFiles(self.Id,queryPars=qp(myQp))
       
    def uploadFile(self, api, localPath, fileName, directory, contentType):
        '''
        Uploads a local file to the BaseSpace analysis
        
        :param api: An instance of BaseSpaceAPI
        :param localPath: The local path of the file
        :param fileName: The filename
        :param directory: The remote directory to upload to
        :param contentType: The content-type of the file
        '''
        self.isInit()
        return api.analysisFileUpload(self.Id,localPath, fileName, directory, contentType)
         
    def uploadMultipartFile(self, api, localPath, fileName, directory, contentType,tempDir='',cpuCount=1,partSize=10,verbose=0):
        '''
        Upload a file in multi-part mode. Returns an object of type MultipartUpload used for managing the upload.
        
        :param api:An instance of BaseSpaceAPI
        :param localPath: The local path of the file
        :param fileName: The filename
        :param directory: The remote directory to upload to
        :param contentType: The content-type of the file
        :param cpuCount: The number of CPUs to used for the upload
        :param partSize:
        '''
        self.isInit()
        return api.multipartFileUpload(self.Id, localPath, fileName, directory, contentType, tempDir,cpuCount,partSize,verbose=verbose)

        # 
        self.Name = None # str
        # 
        self.Status = None # str
        # 
        self.Description = None # str
        # 
        self.StatusSummary = None # str
        # 
        self.HrefFiles = None # str
        # 
        self.DateCreated = None # str
        # 
        self.Id = None # str
        # 
        self.Href = None # str
        # 
        self.UserOwnedBy = None # UserCompact
        # 
        self.StatusDetail = None # str
        # 
        self.HrefGenome = None # str