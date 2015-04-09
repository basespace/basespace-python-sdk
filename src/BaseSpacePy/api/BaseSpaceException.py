
class UndefinedParameterException(Exception):
    def __init__(self, value):
        self.parameter = 'The following required parameter must be defined: ' + str(value)
    def __str__(self):
        return repr(self.parameter)

class UnknownParameterException(Exception):
    def __init__(self, value):
        self.parameter = str(value) + ' is not recognized as a parameter for this call'
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
    
class ServerResponseException(Exception):
    def __init__(self, value):
        self.parameter = 'Error with API server response: ' + value
    def __str__(self):
        return repr(self.parameter)
    
class ModelNotInitializedException(Exception):
    def __init__(self,value):
        self.parameter = 'The request cannot be completed as model has not been initialized - ' + value
    def __str__(self):
        return repr(self.parameter)
    
class ByteRangeException(Exception):
    def __init__(self, value):
        self.parameter = 'Byte-range invalid: ' + value
    def __str__(self):
        return repr(self.parameter)
    
class MultiProcessingTaskFailedException(Exception):
    def __init__(self, value):
        self.parameter = 'Multiprocessing task failed: ' + value
    def __str__(self):
        return repr(self.parameter)

class UploadPartSizeException(Exception):
    def __init__(self, value):
        self.parameter = 'Upload part size invalid: ' + value
    def __str__(self):
        return repr(self.parameter)

class CredentialsException(Exception):
    def __init__(self, value):
        self.parameter = 'Error with BaseSpace credentials: ' + value
    def __str__(self):
        return repr(self.parameter)

class QueryParameterException(Exception):
    def __init__(self, value):
        self.parameter = 'Error with query parameter: ' + value
    def __str__(self):
        return repr(self.parameter)

class AppSessionException(Exception):
    def __init__(self, value):
        self.parameter = 'Error with AppSession: ' + value
    def __str__(self):
        return repr(self.parameter)

class ModelNotSupportedException(Exception):
    def __init__(self, value):
        self.parameter = 'Model not supported: ' + value
    def __str__(self):
        return repr(self.parameter)

class OAuthException(Exception):
    def __init__(self, value):
        self.parameter = 'Error with OAuth: ' + value
    def __str__(self):
        return repr(self.parameter)

class RestMethodException(Exception):
    def __init__(self, value):
        self.parameter = 'Error with REST API method: ' + value
    def __str__(self):
        return repr(self.parameter)
    
