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

import json
from StringIO import StringIO

class ListResponse:

    def __init__(self):
        self.swaggerTypes = {
            'ResponseStatus': 'ResponseStatus',
            'Response': 'ResourceList',
            'Notifications': 'list<Str>'
        }

    def convertToObjectList(self):
        l = []
        for m in self.Response.Items:
            io = eval(m)
            s = json.dumps(io)
            mj = json.loads(s)
            l.append(mj)
        return l

        # 
        self.ResponseStatus = None # ResponseStatus


        # 
        self.Response = None # ResourceList


        # 
        self.Notifications = None # list<Str>

