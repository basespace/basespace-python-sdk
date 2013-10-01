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

class Run:

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'Number': 'str',
            'HrefFiles': 'str',
            'HrefSamples': 'str',
            'UserUploadedBy': 'UserCompact',
            'UserOwnedBy': 'UserCompact',
            'DateUploadCompleted': 'datetime',
            'DateUploadStarted': 'datetime',
            'HrefBaseSpaceUI': 'str',
            'Id': 'str',
            'Href': 'str',
            'ExperimentName': 'str',
            'Status': 'str',
            'DateCreated': 'datetime',
            'DateModified': 'datetime',
            'Properties': 'PropertyList',
            'ReagentBarcode': 'str',
            'FlowcellBarcode': 'str',
            'TotalSize': 'int',                                        
        }
    def __str__(self):
        return self.Name
    def __repr__(self):
        return str(self)
    
