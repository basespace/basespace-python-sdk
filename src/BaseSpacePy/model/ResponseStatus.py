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

class ResponseStatus:

    def __init__(self):
        self.swaggerTypes = {
            'Message': 'str',
            'Errors': 'list<Str>',
            'ErrorCode': 'str',
            'StackTrace': 'str'
        }



        # 
        self.Message = None # str


        # 
        self.Errors = None # list<Str>


        # 
        self.ErrorCode = None # str


        # 
        self.StackTrace = None # str

