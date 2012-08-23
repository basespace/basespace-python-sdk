# Abstract class

class BaseSpaceModel:
    
    def __init__(self):
        #to be overriden
        self.Id = ''
        pass

    def __str__(self):
        self.isInit()
        return self.Id
    
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        return 1
    
    def setAPI(self,api):
        self.api = api