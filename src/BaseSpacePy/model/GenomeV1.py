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

class GenomeV1:


    def __init__(self):
        self.swaggerTypes = {
            'Source': 'str',
            'SpeciesName': 'str',
            'Build': 'str',
            'Id': 'str',
            'Href': 'str',
            'DisplayName': 'str'
        }
        
    def __str__(self):
        if self.SpeciesName:    return self.SpeciesName
        elif self.DisplayName:  return self.DisplayName
        else:                   return "Genome @ " + str(self.Href)
    def __repr__(self):
        return str(self)

        # 
        self.Source = None # str


        # 
        self.SpeciesName = None # str


        # 
        self.Build = None # str


        # 
        self.Id = None # str


        # 
        self.Href = None # str


        # 
        self.DisplayName = None # str

