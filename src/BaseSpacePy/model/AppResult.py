
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
        :returns: True on success
        
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
        Return the sample ids for the referenced sample(s). 
        If other reference types than Samples are present (they shouldn't be), they are ignored.
        
        :returns: a list of sample ids for the referenced samples.
        '''
        self.isInit()
        res = []
        for s in self.References:
            if s['Type']=='Sample':
                sid = s['HrefContent'].split('/')[-1]
                res.append(sid)
        return res        
    
    def getReferencedSamples(self, api):
        '''        
        Returns the sample objects for the referenced sample(s). 
        NOTE this method makes one request to REST server per sample.
        If other reference types than Samples are present (they shouldn't be), they are ignored.
        
        :param api: A BaseSpaceAPI instance
        :returns: A list of sample objects that are referenced by the AppResult.
        '''
        self.isInit()
        res = []
        ids = self.getReferencedSamplesIds()
        for sid in ids:            
            sample = api.getSampleById(sid)
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
