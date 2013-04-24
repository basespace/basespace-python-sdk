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

class PurchasedProduct:

    def __init__(self):
        self.swaggerTypes = {
            'PurchaseId': 'str',
            'DatePurchased': 'str',
            'Id': 'str',
            'Name': 'str',
            'Price': 'str',
            'Quantity': 'str',
            'PersistenceStatus': 'str',
            'Tags': 'list<str>',         # only if provided as a query parameter
            'ProductIds': 'list<str>',   # only if provided as a query parameter
        }

    def __str__(self):
        return str(self.Name)
    def __repr__(self):
        return str(self)
