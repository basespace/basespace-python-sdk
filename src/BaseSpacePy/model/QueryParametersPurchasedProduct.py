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

from BaseSpacePy.api.BaseSpaceException import UndefinedParameterException,UnknownParameterException,IllegalParameterException

legal    = { 'Tags':[], 'ProductIds':[] }

class QueryParametersPurchasedProduct:
    '''
    This class can be passed as an optional argument for a filtering getUserProducts list response
    '''
    def __init__(self,pars={}):
        self.passed = {}
        for k in pars.keys():
            self.passed[k] = pars[k]
        self.validate()
        
    def __str__(self):
        return str(self.passed)
    
    def __repr__(self):
        return str(self)
    
    def getParameterDict(self):
        return self.passed
    
    def validate(self):
        for p in self.passed.keys():
            if not legal.has_key(p): raise UnknownParameterException(p)
