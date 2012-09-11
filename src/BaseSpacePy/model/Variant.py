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

class Variant:

    def __init__(self):
        self.swaggerTypes = {
            'CHROM': 'str',                 
            'ALT': 'str',
            'ID': 'list<Str>',
            'SampleFormat': 'dict',
            'FILTER': 'str',
            'INFO': 'dict',
            'POS':'int',
            'QUAL':'int',
            'REF':'str'
        }
    def __str__(self):
        return "Variant - " + self.CHROM + ": " + str(self.POS) + " id=" + str(self.ID)
    def __repr__(self):
        return str(self)

        self.ID         = None
        self.INFO       = None
        self.CHROM      = None
        self.ALT        = None
        self.FILTER     = None
        self.POS        = None
        self.QUAL       = None
        self.REF        = None
        self.INFO       = None
        self.SampleFormat= None 