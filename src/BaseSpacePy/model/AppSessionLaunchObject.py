
class AppSessionLaunchObject(object):
    '''
    AppSession References contain a list of AppSessionLaunchObjects.
    They typically include the input project for an AppSession.
    '''
    def __init__(self):
        self.swaggerTypes = {
            'Content': 'dict',
            'Href': 'str',
            'HrefContent': 'str',
            'Rel': 'str',
            'Type': 'str'
        }

    def __str__(self):
        return str(self.Type)
    
    def __repr__(self):
        return str(self)
    
    def __serializeObject__(self, api):
        '''
        Called from AppSession instance when serializing References
        
        :param api: A BaseSpaceAPI instance
        :returns: Self, with Content converted from dict to an object if the type is a major BaseSpace item (eg., a Project)
        '''
        res = api.__serializeObject__(self.Content, self.Type)
        self.Content = res
        return self
