
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
            'Run': 'RunCompact', # deprecated?
            'TotalSize': 'int',
            'AppSession': 'AppSessionSemiCompact',
            'Properties': 'PropertyList',
        }

    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''
        Tests if the Sample instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :return True on success
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
