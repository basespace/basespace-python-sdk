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

class Property:
    """
    A generic Property to catch unrecognized Property types -- shouldn't be
    used unless new properties are added to the REST API
    """

    def __init__(self):
        self.swaggerTypes = {
            'Type': 'str',
            'Href': 'str',
            'Name': 'str',
            'Description': 'str',
            'Content': 'str',
            'Items': 'list<Str>',
            'HrefItems': 'list<Str>',
            'ItemsDisplayedCount': 'str',
            'ItemsTotalCount': 'str'
        }

    def __str__(self):
        return str(self.Name)
    def __repr__(self):
        return str(self)
    
#    def __serializeObject__(self,api):
#        res = api.__serializeObject__(self.Content,self.Type)
#        self.Content = res
#        return self
        
#        self.Content        = None
#        self.Href           = None
#        self.HrefContent    = None
#        self.Rel            = None
#        self.Type           = None 

