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

#from pprint import pprint
#import urllib2
#import shutil
#import urllib
#import pycurl
#import httplib
#import cStringIO
#import json
#import os

from BaseSpacePy.api.BaseAPI import BaseAPI
from BaseSpacePy.api.BaseSpaceException import * #@UnusedWildImport
from BaseSpacePy.model import * #@UnusedWildImport
from BaseSpacePy.model.QueryParametersPurchasedProduct import QueryParametersPurchasedProduct #@UnresolvedImport

class BillingAPI(BaseAPI):
    '''
    The API class used for all communication with the BaseSpace Billng server
    '''
    def __init__(self, apiServer, version, appSessionId='', AccessToken=''):
        if not apiServer[-1]=='/': apiServer = apiServer + '/'
        
        self.appSessionId   = appSessionId
        self.apiServer      = apiServer + version
        self.version        = version
        super(BillingAPI, self).__init__(AccessToken)

    def createPurchase(self, products, appSessionId=''):
        '''
        Creates a purchase with the specified products
        
        :param Name: List of dicts to purchase, each of which has a product 'id'
            and 'quantity' to purchase
        '''        
        if not self.apiClient.apiKey:
            raise Exception('Access-token is not set and is required to create a Purchase')
        resourcePath            = '/purchases/'
        resourcePath            = resourcePath.replace('{format}', 'json')
        method                  = 'POST'
        queryParams             = {}
        headerParams            = {'x-access-token':self.apiClient.apiKey}
        postData                = {}
        # 'Products' is list of dicts with 'id', 'quantity', and optnl 'tags[]'
        postData['Products']    = products
        if appSessionId:
            postData['AppSessionId'] = appSessionId
        
        response = self.__singleRequest__(PurchaseResponse.PurchaseResponse,resourcePath, method, queryParams, headerParams,postData=postData,verbose=0)
        return response
            
    def getPurchaseById(self, Id):
        '''
        Request a purchase object by Id
        
        :param Id: The Id of the purchase
        '''
        resourcePath = '/purchases/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(PurchaseResponse.PurchaseResponse, resourcePath, method, queryParams, headerParams)

    def getUserProducts(self, Id='current', qps={}):
        '''
        Returns the Products for the current user

        :param Id: The id of the user, optional
        :param qps: Query parameters, a dictionary for filtering by 'Tags' and/or 'ProductIds', optional
        '''
        method = 'GET'
        resourcePath = '/users/{Id}/products'
        resourcePath = resourcePath.replace('{Id}', str(Id))
        queryPars = QueryParametersPurchasedProduct(qps)
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        return self.__listRequest__(PurchasedProduct.PurchasedProduct, resourcePath, method, queryParams, headerParams)

