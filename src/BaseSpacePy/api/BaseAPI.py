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

from pprint import pprint
import urllib2
import shutil
import urllib
import pycurl
import httplib
import cStringIO
import json
import os

from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import * #@UnusedWildImport
from BaseSpacePy.model import * #@UnusedWildImport


class BaseAPI(object):
    '''
    Parent class for BaseSpaceAPI and BillingAPI objects
    '''
    def __init__(self, AccessToken='', timeout=10):
        self.apiClient = None
        self.setTimeout(timeout)
        self.setAccessToken(AccessToken)        # logic for setting the access-token 

    def __updateAccessToken__(self,AccessToken):
        self.apiClient.apiKey = AccessToken

    def __singleRequest__(self,myModel,resourcePath, method, queryParams, headerParams,postData=None,verbose=0,forcePost=0,noAPI=1):
        # test if access-token has been set
        if not self.apiClient and noAPI:
            raise Exception('Access-token not set, use the "setAccessToken"-method to supply a token value')
        if verbose: print "    # " + str(resourcePath)
        
        # Make the API Call
        response = self.apiClient.callAPI(resourcePath, method, queryParams,postData, headerParams,forcePost=forcePost)
        if verbose: 
            print "    # "
            print "    # forcePost: " + str(forcePost) 
            pprint(response)
        if not response: 
            raise Exception('BaseSpace error: None response returned')
        
        # throw exception here for various error messages
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise Exception('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])
         
        # Create output objects if the response has more than one object
        responseObject = self.apiClient.deserialize(response,myModel)
        return responseObject.Response

    def __listRequest__(self,myModel,resourcePath, method, queryParams, headerParams,verbose=0,noAPI=1):
        # test if access-token has been set
        if not self.apiClient and noAPI:
            raise Exception('Access-token not set, use the "setAccessToken"-method to supply a token value')
        
        # Make the API Call
        if verbose: 
            print '    # Path: ' + str(resourcePath)
            print '    # Pars: ' + str(queryParams)
        response = self.apiClient.callAPI(resourcePath, method, queryParams, None, headerParams)
        if not response: 
            raise Exception('BaseSpace Exception: No data returned')
        
        if verbose: 
            print '    # response: ' 
            pprint(response)
        if not isinstance(response, list): response = [response]
        responseObjects = []
        for responseObject in response:
            responseObjects.append(self.apiClient.deserialize(responseObject, ListResponse.ListResponse))
        
        # convert list response dict to object type
        # TODO check that Response is present -- errors sometime don't include
        convertet = [self.apiClient.deserialize(c,myModel) for c in responseObjects[0].convertToObjectList()]
#        print response 
        return convertet
    # test if 

    def __makeCurlRequest__(self, data, url):
        post = urllib.urlencode(data)
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL,url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, post)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        obj = json.loads(response.getvalue())
        if obj.has_key('error'):
            raise Exception("BaseSpace exception: " + obj['error'] + " - " + obj['error_description'])
        return obj
      

    def __str__(self):
        return "BaseSpaceAPI instance - using token=" + self.getAccessToken()
    
    def __repr__(self):
        return str(self)  

    def setTimeout(self,time):
        '''
        Specify the timeout in seconds for each request made
        
        :param time: timeout in second
        '''
        self.timeout = time
        if self.apiClient:
            self.apiClient.timeout = self.timeout
        
    def setAccessToken(self,token):
        self.apiClient      = None
        if token: 
            apiClient = APIClient(AccessToken=token,apiServer=self.apiServer,timeout=self.timeout)
            self.apiClient = apiClient

    def getAccessToken(self):
        '''
        Returns the access-token that was used to initialize the BaseSpaceAPI object.
        '''
        if self.apiClient:
            return self.apiClient.apiKey
        return ""
    
    def getServerUri(self):
        '''
        Returns the server uri used by this instance
        '''
        return self.apiClient.apiServer

