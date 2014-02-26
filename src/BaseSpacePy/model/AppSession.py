
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
            
    def __serializeReferences__(self, api):
        ref = []
        for r in self.References:
            # TODO add try except in case reference isn't a AppSessionLaunchObject
            res = r.__serializeObject__(api)
            ref.append(res)
        self.References = ref
        return self
 