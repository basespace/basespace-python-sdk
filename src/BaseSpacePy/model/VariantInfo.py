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

class VariantInfo:
    def __init__(self):
        self.swaggerTypes = {
            'CIGAR': 'list<Str>',
            'IDREP': 'list<Str>',                 
            'REFREP': 'list<Str>',
            'RU':'list<Str>',
            'VARTYPE_DEL':'list<Str>',
            'VARTYPE_INS':'list<Str>',
            'VARTYPE_SNV':'list<Str>',
        }
        
        self.CIGAR          = None
        self.IDREP          = None
        self.REFREP         = None
        self.RU             = None
        self.VARTYPE_DEL    = None
        self.VARTYPE_INS    = None
        self.VARTYPE_SNV    = None
 