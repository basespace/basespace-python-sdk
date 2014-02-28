
from BaseSpacePy.model.AppSessionSemiCompact import AppSessionSemiCompact

class AppSession(AppSessionSemiCompact):
    '''
    Returned from getAppSessionById() and getAppSesssion()
    '''
    def __init__(self):
        self.swaggerTypes = {
            'Id':'str',
            'Href': 'str',
            'Type': 'str',
            'Name': 'str',
            'UserCreatedBy':'UserCompact',
            'DateCreated': 'datetime',
            'ModifiedOn': 'datetime',
            'Status':'str',
            'StatusSummary': 'str',
            'Application':'Application',
            'References':'list<AppSessionLaunchObject>',
            'Properties':'PropertyList',
            'AuthorizationCode': 'str',
            'OriginatingUri': 'str',
        }
            
    def __deserializeReferences__(self, api):
        '''
        Convert References (actually, the Content of each AppSessionLaunchObject) from dicts to objects,
        if the type is a primary BaseSpace item (eg., Project)
        
        :param api: A BaseSpaceAPI instance
        :returns: Self, with each Reference's Content converted from dict to an object if the type is a major BaseSpace item (eg., a Project)
        '''        
        ref = []
        for r in self.References:
            res = r.__deserializeObject__(api)
            ref.append(res)
        self.References = ref
        return self
 