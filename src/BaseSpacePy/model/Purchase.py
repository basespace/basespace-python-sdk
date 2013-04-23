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
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class Purchase:
    '''
    Represents a BaseSpace Purchase object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Id': 'str',
            'Status': 'str',
            'RefundStatus': 'str',
            'DateCreated': 'str',
            'DateUpdated': 'str',
            'InvoiceNumber': 'str',
            'Amount': 'str',
            'AmountOfTax': 'str',
            'AmountTotal': 'str',
            'Products': 'list<Product>',
            'PurchaseType': 'str',
            'AppSession': 'AppSessionCompact',
            'User': 'UserCompact',
            'Application': 'ApplicationCompact',
            'HrefPurchaseDialog': 'str',
            'RefundSecret': 'str',
            'ExceptionMessage': 'str',
            'ExceptionStackTrace': 'str',
        }
    
    def __str__(self):
        return str(self.Id)
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''
        Is called to test if the Purchase instance has been initialized.
        Throws:
            ModelNotInitializedException - Indicates the object has not been populated yet.
        '''
        if not self.Id: raise ModelNotInitializedException('The project model has not been initialized yet')
