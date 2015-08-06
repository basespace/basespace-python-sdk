
from pprint import pprint
import urllib2
import shutil
import urllib
import httplib
import cStringIO
import json
import os
import inspect

from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import *
from BaseSpacePy.model import *


class BaseAPI(object):
    '''
    Parent class for BaseSpaceAPI and BillingAPI classes
    '''

    def __init__(self, AccessToken, apiServerAndVersion, userAgent, timeout=10, verbose=False):
        '''
        :param AccessToken: the current access token
        :param apiServerAndVersion: the api server URL with api version
        :param timeout: (optional) the timeout in seconds for each request made, default 10 
        :param verbose: (optional) prints verbose output, default False
        '''
        self.apiClient = APIClient(AccessToken, apiServerAndVersion, userAgent=userAgent, timeout=timeout)
        self.verbose   = verbose

    def __json_print__(self, label, var):
        try:
            prefix   = " " * len(label)
            var_list = json.dumps(var,indent=4).split('\n')  # ,ensure_ascii=False
            print label + var_list[0]
            if len(var_list)>1:
                print "\n".join( [prefix + s for s in var_list[1:]] )
        except UnicodeDecodeError:
            pass  # we could disable ascii-enforcing, as shown above, but 
                  # this will massively increase the volume of logs

    def __singleRequest__(self, myModel, resourcePath, method, queryParams, headerParams, postData=None, forcePost=False):
        '''
        Call a REST API and deserialize response into an object, handles errors from server.
        
        :param myModel: a Response object that includes a 'Response' swaggerType key with a value for the model type to return
        :param resourcePath: the api url path to call (without server and version)
        :param method: the REST method type, eg. GET
        :param queryParams: a dictionary of query parameters
        :param headerParams: a dictionary of header parameters
        :param postData: (optional) data to POST, default None
        :param version: (optional) print detailed output, default False
        :param forcePost: (optional) use a POST call with pycurl instead of urllib, default False (used only when POSTing with no post data?)

        :raises ServerResponseException: if server returns an error or has no response
        :returns: an instance of the Response model from the provided myModel
        '''
        if self.verbose: 
            print ""
            print "* " + inspect.stack()[1][3] + "  (" + str(method) + ")"  # caller
            print '    # Path:      ' + str(resourcePath)
            print '    # QPars:     ' + str(queryParams)
            print '    # Hdrs:      ' + str(headerParams)
            print '    # forcePost: ' + str(forcePost)
            self.__json_print__('    # postData:  ',postData)
        response = self.apiClient.callAPI(resourcePath, method, queryParams, postData, headerParams, forcePost=forcePost)
        if self.verbose:
            self.__json_print__('    # Response:  ',response)
        if not response: 
            raise ServerResponseException('No response returned')
        if response.has_key('ResponseStatus'):
            if response['ResponseStatus'].has_key('ErrorCode'):
                raise ServerResponseException(str(response['ResponseStatus']['ErrorCode'] + ": " + response['ResponseStatus']['Message']))
            elif response['ResponseStatus'].has_key('Message'):
                raise ServerResponseException(str(response['ResponseStatus']['Message']))
        elif response.has_key('ErrorCode'):
            raise ServerResponseException(response["MessageFormatted"])
                 
        responseObject = self.apiClient.deserialize(response, myModel)
        if hasattr(responseObject, "Response"):
            return responseObject.Response
        else:
            return responseObject

    def __listRequest__(self, myModel, resourcePath, method, queryParams, headerParams):
        '''
        Call a REST API that returns a list and deserialize response into a list of objects of the provided model.
        Handles errors from server.

        :param myModel: a Model type to return a list of
        :param resourcePath: the api url path to call (without server and version)
        :param method: the REST method type, eg. GET
        :param queryParams: a dictionary of query parameters
        :param headerParams: a dictionary of header parameters

        :raises ServerResponseException: if server returns an error or has no response        
        :returns: a list of instances of the provided model
        '''
        if self.verbose: 
            print ""
            print "* " + inspect.stack()[1][3] + "  (" + str(method) + ")"  # caller
            print '    # Path:      ' + str(resourcePath)
            print '    # QPars:     ' + str(queryParams)
            print '    # Hdrs:      ' + str(headerParams)
        response = self.apiClient.callAPI(resourcePath, method, queryParams, None, headerParams)
        if self.verbose:
            self.__json_print__('    # Response:  ',response)
        if not response: 
            raise ServerResponseException('No response returned')
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise ServerResponseException(str(response['ResponseStatus']['ErrorCode'] + ": " + response['ResponseStatus']['Message']))
        elif response['ResponseStatus'].has_key('Message'):
            raise ServerResponseException(str(response['ResponseStatus']['Message']))
        
        respObj = self.apiClient.deserialize(response, ListResponse.ListResponse)
        return [self.apiClient.deserialize(c, myModel) for c in respObj._convertToObjectList()]

    def __makeCurlRequest__(self, data, url):
        '''
        Make a curl POST request
        
        :param data: data to post (eg. list of tuples of form (key, value))
        :param url: url to post data to
        
        :raises ServerResponseException: if server returns an error or has no response
        :returns: dictionary of api server response
        '''
        # pycurl is hard to get working, so best to cauterise it into only the functions where it is needed
        import pycurl
        post = urllib.urlencode(data)
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL,url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, post)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        respVal = response.getvalue()
        if not respVal:
            raise ServerResponseException("No response from server")
        obj = json.loads(respVal)
        if obj.has_key('error'):
            raise ServerResponseException(str(obj['error'] + ": " + obj['error_description']))
        return obj      

    def getTimeout(self):
        '''
        Returns the timeout in seconds for each request made
        '''
        return self.apiClient.timeout

    def setTimeout(self, time):
        '''
        Specify the timeout in seconds for each request made
        
        :param time: timeout in seconds
        '''        
        self.apiClient.timeout = time
        
    def getAccessToken(self):
        '''
        Returns the current access token. 
        '''        
        return self.apiClient.apiKey        

    def setAccessToken(self, token):
        '''
        Sets the current access token.
                
        :param token: an access token
        '''
        self.apiClient.apiKey = token            
