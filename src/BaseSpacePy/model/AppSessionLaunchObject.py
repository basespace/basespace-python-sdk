class AppSessionLaunchObject:

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
    
    def __serializeObject__(self,api):
        res = api.__serializeObject__(self.Content,self.Type)
        self.Content = res
        return self
        
        self.Content        = None
        self.Href           = None
        self.HrefContent    = None
        self.Rel            = None
        self.Type           = None 

