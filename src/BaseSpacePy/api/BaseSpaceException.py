"""
Copyright 2012 Illumina

    Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
    
class ByteRangeException(Exception):
    def __init__(self, value):
        self.parameter = 'Byte-range invalid: ' + value
    def __str__(self):
        return repr(self.parameter)
    
class MultiProcessingTaskFailedException(Exception):
    def __init__(self, value):
        self.parameter = 'Multiprocessing task failed failed: ' + value
    def __str__(self):
        return repr(self.parameter)

class UploadPartSizeException(Exception):
    def __init__(self, value):
        self.parameter = 'Upload part size invalid: ' + value
    def __str__(self):
        return repr(self.parameter)

    