
class UserCompact(object):

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Id': 'str',
            'Href': 'str',
            'GravatarUrl': 'str',
        }

    def __str__(self):
        return self.Name
    
    def __repr__(self):
        return str(self)
