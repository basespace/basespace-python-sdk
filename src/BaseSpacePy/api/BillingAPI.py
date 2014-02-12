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
from BaseSpacePy.api.BaseAPI import BaseAPI
from BaseSpacePy.api.BaseSpaceException import * #@UnusedWildImport
from BaseSpacePy.model import * #@UnusedWildImport
from BaseSpacePy.model.QueryParametersPurchasedProduct import QueryParametersPurchasedProduct as qpp

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
        resourcePath            = '/purchases/'
        resourcePath            = resourcePath.replace('{format}', 'json')
        method                  = 'POST'
        queryParams             = {}
        headerParams            = {}
        postData                = {}
        # 'Products' is list of dicts with 'id', 'quantity', and optnl 'tags[]'
        postData['Products']    = products
        if appSessionId:
            postData['AppSessionId'] = appSessionId
        return self.__singleRequest__(PurchaseResponse.PurchaseResponse,resourcePath, method, queryParams, headerParams,postData=postData,verbose=0)
            
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

    def getUserProducts(self, Id='current', queryPars=None):
        '''
        Returns the Products for the current user

        :param Id: The id of the user, optional
        :param queryPars: An (optional) object of type QueryParametersPurchasedProduct for custom sorting and filtering by 'Tags' and/or 'ProductIds'
        '''
        if queryPars is None:
            queryPars = qpp()
        elif not isinstance(queryPars, qpp):
            raise QueryParameterException("Query parameter argument must be a QueryParameterPurchasedProduct object")
        method = 'GET'
        resourcePath = '/users/{Id}/products'
        resourcePath = resourcePath.replace('{Id}', str(Id))
        queryPars.validate()
        queryParams = queryPars.getParameterDict()    
        headerParams = {}
        return self.__listRequest__(PurchasedProduct.PurchasedProduct, resourcePath, method, queryParams, headerParams)

    def refundPurchase(self, purchaseId, refundSecret, comment=''):
        '''
        Creates a purchase with the specified products
        
        :param purchaseId: The Id of the purchase
        :param refundSecret: The RefundSecret that was provided in the Response from createPurchase()
        :param comment: An optional comment about the refund
        '''        
        resourcePath            = '/purchases/{id}/refund'
        resourcePath            = resourcePath.replace('{id}', purchaseId)
        method                  = 'POST'
        queryParams             = {}
        headerParams            = {}
        postData                = {}
        postData['RefundSecret'] = refundSecret
        if comment:
            postData['Comment'] = comment
        return self.__singleRequest__(RefundPurchaseResponse.RefundPurchaseResponse, resourcePath, method, queryParams, headerParams, postData=postData, verbose=0)
