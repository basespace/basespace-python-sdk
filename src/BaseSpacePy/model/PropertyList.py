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

class PropertyList:
    
    # Values for DynamicType, keyed by 'Type' in each property Item
    _dynamicType = {'string': 'PropertyString',
                    'string[]': 'PropertyStrings',
                    'project': 'PropertyProject',
                    'project[]': 'PropertyProjects',
                    'appresult': 'PropertyAppResult',
                    'appresult[]': 'PropertyAppResults',
                    'sample': 'PropertySample',
                    'sample[]': 'PropertySamples',
                    'file': 'PropertyFile',
                    'file[]': 'PropertyFiles',
                    'run': 'PropertyRun',
                    'run[]': 'PropertyRuns',
                    'map': 'PropertyMap',
                    'map[]': 'PropertyMaps',
                   }    

    def __init__(self):
        self.swaggerTypes = {
            'Items': 'list<DynamicType>',
            'Href': 'str', #
            'DisplayedCount': 'int',
            'TotalCount': 'int',            
            'Offset': 'int',
            'Limit': 'int',
            'SortDir': 'str',
            'SortBy': 'str'
        }

#    def __str__(self):
#        return str(self.Href)
#    def __repr__(self):
#        return str(self)
    
