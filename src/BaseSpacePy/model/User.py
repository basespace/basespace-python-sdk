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

from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException

class User(object):
    
    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Email': 'str',
            'DateLastActive': 'datetime',
            'GravatarUrl': 'str',
            'HrefProjects': 'str',
            'DateCreated': 'datetime',
            'Id': 'str',
            'Href': 'str',
            'HrefRuns': 'str'
        }
    
    def __str__(self):
        return str(self.Id) + ": " + self.Name
    def __repr__(self):
        return str(self)
    def isInit(self):
        '''
        Is called to test if the Project instance has been initialized
        :raise Throws ModelNotInitializedException if the Id variable is not set
        '''
        try: self.Id 
        except: raise ModelNotInitializedException('The user model has not been initialized yet')
        
    
    def getProjects(self,api):
        self.isInit()
        return api.getProjectByUser(self.Id)
    
    def getRuns(self,api):
        '''
        Returns a list of the accessible run for the user 
        :param api: An instance of BaseSpaceAPI
        '''
        self.isInit()
        return api.getAccessibleRunsByUser('current')
        
        self.Name = None # str

        self.Email = None # str

        self.DateLastActive = None # datetime

        self.GravatarUrl = None # str

        self.HrefProjects = None # str

        self.DateCreated = None # datetime

        self.Id = None # str

        self.Href = None # str

        self.HrefRuns = None # str
