class UndefinedParameterException(Exception):
    def __init__(self, value):
        self.parameter = 'The following parameter must be defined: ' + str(value)
    def __str__(self):
        return repr(self.parameter)

class UnknownParameterException(Exception):
    def __init__(self, value):
        self.parameter = str(value) + ' is not regcognized as a parameter for this call'
    def __str__(self):
        return repr(self.parameter)

class IllegalParameterException(Exception):
    def __init__(self, value,legal):
        self.parameter = str(value) + ' is not well-defined, legal options are ' + str(legal)
    def __str__(self):
        return repr(self.parameter)
    
class WrongFiletypeException(Exception):
    def __init__(self, filetype):
        self.parameter = 'This data request is not available for file ' + str(filetype)
    def __str__(self):
        return repr(self.parameter)
    
class NoRepsonseException(Exception):
    def __init__(self, value):
        self.parameter = 'No response was returned from the server for this request'
    def __str__(self):
        return repr(self.parameter)
    
class ModelNotInitializedException(Exception):
    def __init__(self,value):
        self.parameter = 'The request cannot be completed as model has not been initialized - ' + value
    def __str__(self):
        return repr(self.parameter)