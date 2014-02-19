
class AppSessionCompact(object):
    '''
    Returned from GET purchases
    '''
    def __init__(self):
        self.swaggerTypes = {
            'Id':'str',
            'Name':'str',
        }
        
    def __str__(self):
        return str(self.Name)
    
    def __repr__(self):
        return str(self)
    
