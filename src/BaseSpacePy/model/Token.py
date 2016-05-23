class Token(object):
    def __init__(self):
        self.swaggerTypes = {
            'Scopes': 'list<str>',
            'DateCreated': 'datetime',
            'UserResourceOwner': 'User',
            'Application': 'Application',
            'AccessToken': 'str'
        }
    
