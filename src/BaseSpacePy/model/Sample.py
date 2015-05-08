
from BaseSpacePy.model.QueryParameters import QueryParameters as qp
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException

class Sample(object):
    '''
    A BaseSpace Sample object.
    '''
    def __init__(self):
        self.swaggerTypes = {
            'HrefGenome': 'str',
            'SampleNumber': 'int',
            'ExperimentName': 'str',
            'HrefFiles': 'str',
            'IsPairedEnd':'int',
            'Read1':'int',
            'Read2':'int',
            'NumReadsRaw':'int',
            'NumReadsPF':'int',
            'Id': 'str',
            'Href': 'str',
            'UserOwnedBy': 'UserCompact',
            'Name': 'str',
            'SampleId': 'str',
            'Status': 'str',
            'StatusSummary': 'str',
            'DateCreated': 'datetime',
            'References':'dict',
            'TotalSize': 'int',
            'AppSession': 'AppSessionSemiCompact',
            'Properties': 'PropertyList',
            'Projects': 'list<Project>',
        }

    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''
        Tests if the Sample instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :returns: True on success
        
        '''
        err = 'The Sample object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        

    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to used for requesting BaseSpace access to the sample.
        
        :param scope: The scope type that is request (eg. write, read).
        '''
        self.isInit()
        return scope + ' sample ' + str(self.Id)
    
    def getReferencedAppResults(self, api):
        '''                
        Return the AppResults referenced by this sample. 
        Note the returned AppResult objects do not have their "References" field set, 
        to get a fully populated AppResult object you must use getAppResultById in BaseSpaceAPI.
        If other reference types than AppResults are present (they shouldn't be), they are ignored.

        :param api: A BaseSpaceAPI instance        
        :returns: A list of AppResult that are referenced by this sample (with their References field not populated)
        '''
        res = []
        for s in self.References:
            if s['Type']=='AppResult':
                ar_dict = s['Content']
                ar = api.__deserializeObject__(ar_dict, "AppResult")
                res.append(ar)
        return res
    
    def getFiles(self, api, queryPars=None):
        '''
        Returns a list of File objects
        
        :param api: A BaseSpaceAPI instance
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        self.isInit()
        if queryPars is None:
            queryPars = qp()
        return api.getSampleFilesById(self.Id, queryPars=queryPars)

    def uploadFile(self, api, localPath, fileName, directory, contentType):
        '''
        WARNING! This method uses an API call that is currently not available (but will be made public in
                 future releases) and, for that reason, it may not work.

        Uploads a local file to the BaseSpace Sample
        
        :param api: An instance of BaseSpaceAPI
        :param localPath: The local path of the file (including file name)
        :param fileName: The file name to use on the server
        :param directory: The remote directory to upload the file to on the server
        :param contentType: The content-type of the file
        '''
        self.isInit()
        return api.sampleFileUpload(self.Id,localPath, fileName, directory, contentType)
