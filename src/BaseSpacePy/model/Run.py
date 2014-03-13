
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class Run(object):
    '''
    A BaseSpace Run object
    '''
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
            'PlatformName': 'str',
            'Workflow': 'str',
            'InstrumentName': 'str',
            'InstrumentType': 'str',
            'NumCyclesRead1': 'int',
            'NumCyclesRead2': 'int',
            'NumCyclesIndex1': 'int',
            'NumCyclesIndex2': 'int',
            'LibraryCount': 'int',                                
        }
    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)

    def isInit(self):
        '''
        Tests if the Run instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :returns: True on success
        
        '''
        err = 'The Run object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        

    def getAccessStr(self,scope='write'):
        '''
        Returns the scope-string to used for requesting BaseSpace access to the Run.
        
        :param scope: The scope type that is request (eg. write, read).
        '''
        self.isInit()
        return scope + ' run ' + str(self.Id)

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
