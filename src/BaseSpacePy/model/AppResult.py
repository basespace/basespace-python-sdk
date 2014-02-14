
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class AppResult(object):

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Status': 'str',
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
        return self.Name
    
    def __repr__(self):
        return str(self)

    def isInit(self):
        '''        
        Tests if the AppResult instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :return True on success
        '''
        err = 'The AppResult object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        
    
    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to be used for requesting BaseSpace access to the object
        
        :param scope: The scope-type that is request (write|read)
        '''
        self.isInit()
        return scope + ' appresult ' + str(self.Id) 
        
    def getReferencedSamplesIds(self):
        '''        
        Return a list of sample ids for the samples referenced.
        '''
        self.isInit()
        res= []
        for s in self.References:
            if s['Type']=='Sample':
                id = s['HrefContent'].split('/')[-1]
                res.append(id)
        return res        
    
    def getReferencedSamples(self, api):
        '''        
        Returns a list of sample objects references by the AppResult. 
        NOTE this method makes one request to REST server per sample
        '''
        self.isInit()
        res = []
        ids = self.getReferencedSamplesIds()
        for id in ids:            
            sample = api.getSampleById(id)
            res.append(sample)                            
        return res
    
    def getFiles(self, api, queryPars=None):
        '''
        Returns a list of file objects
        
        :param api: An instance of BaseSpaceAPI
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering 
        '''
        self.isInit()
        if queryPars is None:
            queryPars = qp()
        return api.getAppResultFiles(self.Id, queryPars=queryPars)
       
    def uploadFile(self, api, localPath, fileName, directory, contentType):
        '''
        Uploads a local file to the BaseSpace AppResult
        
        :param api: An instance of BaseSpaceAPI
        :param localPath: The local path of the file (including file name)
        :param fileName: The file name to use on the server
        :param directory: The remote directory to upload the file to on the server
        :param contentType: The content-type of the file
        '''
        self.isInit()
        return api.appResultFileUpload(self.Id,localPath, fileName, directory, contentType)
