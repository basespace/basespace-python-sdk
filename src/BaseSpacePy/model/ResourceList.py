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

class ResourceList:

    def __init__(self):
        self.swaggerTypes = {
            'Items': 'list<Str>',
            'DisplayedCount': 'int',
            'SortDir': 'str',
            'TotalCount': 'int',
            'Offset': 'int',
            'SortBy': 'str',
            'Limit': 'int'
        }

        # 
        self.Items = None # list<Str>
        # 
        self.DisplayedCount = None # int
        # 
        self.SortDir = None # str
        # 
        self.TotalCount = None # int
        # 
        self.Offset = None # int
        # 
        self.SortBy = None # str
        # 
        self.Limit = None # int