
class AppLaunchResponse(object):
    '''
    Represents a BaseSpace AppLaunch object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'DateCreated': 'datetime',
            'ModifiedOn': 'datetime',
            'Application': 'str',
            'Id': 'str',
            'Href': 'str',
            'OriginatingUri': 'str',
            'UserCreatedBy': 'UserCompact',
            'Properties': 'PropertyList',
            'Status': 'str',
            'StatusSummary': 'str'
        }
    
    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)
            
