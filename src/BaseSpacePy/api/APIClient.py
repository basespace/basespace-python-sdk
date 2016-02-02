
import sys
import os
import re
import urllib
import urllib2
import io
import cStringIO
import json
from subprocess import *
import subprocess
import dateutil.parser
from warnings import warn
from BaseSpacePy.model import *
from BaseSpacePy.api.BaseSpaceException import RestMethodException, ServerResponseException


class APIClient:
    def __init__(self, AccessToken, apiServerAndVersion, userAgent=None, timeout=10):
        '''
        Initialize the API instance
        
        :param AccessToken: an access token
        :param apiServerAndVersion: the URL of the BaseSpace api server with api version
        :param timeout: (optional) the timeout in seconds for each request made, default 10
        '''
        self.apiKey = AccessToken
        self.apiServerAndVersion = apiServerAndVersion
        self.userAgent = userAgent
        self.timeout = timeout

    def __forcePostCall__(self, resourcePath, postData, headers):
        '''
        For forcing a REST POST request (seems to be used when POSTing with no post data)
                
        :param resourcePath: the url to call, including server address and api version
        :param postData: a dictionary of data to post
        :param headers: a dictionary of header key/values to include in call
        :returns: server response (a string containing json)
        '''
        import requests
        # this tries to clean up the output at the expense of letting the user know they're in an insecure context...
        try:
            requests.packages.urllib3.disable_warnings()
        except:
            pass
        import logging
        logging.getLogger("requests").setLevel(logging.WARNING)
        encodedPost =  urllib.urlencode(postData)
        resourcePath = "%s?%s" % (resourcePath, encodedPost)
        response = requests.post(resourcePath, data=json.dumps(postData), headers=headers)
        return response.text

    def __putCall__(self, resourcePath, headers, data):
        '''
        Performs a REST PUT call to the API server.
        
        :param resourcePath: the url to call, including server address and api version        
        :param headers: a dictionary of header key/values to include in call        
        :param transFile: the name of the file containing only data to be PUT
        :returns: server response (a string containing upload status message (from curl?) followed by json response)
        '''
        # headerPrep  = [k + ':' + headers[k] for k in headers.keys()]
        # cmd = 'curl -H "x-access-token:' + self.apiKey + '" -H "Content-MD5:' + headers['Content-MD5'].strip() +'" -T "'+ transFile +'" -X PUT ' + resourcePath
        # p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        # output = p.stdout.read()
        # print output
        # return output
        import requests
        put_headers = {
            'Content-MD5'   :   headers['Content-MD5'].strip(),
            'x-access-token':   self.apiKey
        }
        put_val = requests.put(resourcePath, data, headers=put_headers)
        if put_val.status_code != 200:
            raise ServerResponseException("Multi-part upload: Server return code %s with error %s" % (put_val.status_code, put_val.reason))
        return put_val.text

    def callAPI(self, resourcePath, method, queryParams, postData, headerParams=None, forcePost=False):
        '''
        Call a REST API and return the server response.
        
        An access token header is automatically added.
        If a Content-Type header isn't included, one will be added with 'application/json' (except for PUT and forcePost calls).
        Query parameters with values of None aren't sent to the server.
        Server errors are to be handled by the caller (returned response contains error codes/msgs).
        
        :param resourcePath: the url to call, not including server address and api version
        :param method: REST method, including GET, POST (and forcePost, see below), and PUT (DELETE not yet supported)
        :param queryParams: dictionary of query parameters to be added to url, except for forcePost where they are added as 'postData'; not used for PUT calls
        :param postData: for POST calls, a dictionary to post; not used for forcePost calls; for PUT calls, name of file to put
        :param headerParams: (optional) a dictionary of header data, default None
        :param forcePost: (optional) 'force' a POST call using curl (instead of urllib), default False

        :raises RestMethodException: for unrecognized REST method
        :raises ServerResponseException: for errors in parsing json response from server, and for urlerrors from the opening url
        :returns: Server response deserialized to a python object (dict)
        '''
        url = self.apiServerAndVersion + resourcePath
        headers = {}
        if self.userAgent:
            headers['User-Agent'] = self.userAgent
        if headerParams:
            for param, value in headerParams.iteritems():
                headers[param] = value
        # specify the content type
        if not headers.has_key('Content-Type') and not method=='PUT' and not forcePost: 
            headers['Content-Type'] = 'application/json'
        # include access token in header 
        headers['Authorization'] = 'Bearer ' + self.apiKey
        
        data = None
        if method == 'GET':
            if queryParams:
                # Need to remove None values, these should not be sent
                sentQueryParams = {}
                for param, value in queryParams.iteritems():
                    if value != None:
                        sentQueryParams[param] = value
                url = url + '?' + urllib.urlencode(sentQueryParams)
            request = urllib2.Request(url=url, headers=headers)
        elif method in ['POST', 'PUT', 'DELETE']:
            if queryParams:
                # Need to remove None values, these should not be sent
                sentQueryParams = {}
                for param, value in queryParams.iteritems():
                    if value != None:
                        sentQueryParams[param] = value
                forcePostUrl = url 
                url = url + '?' + urllib.urlencode(sentQueryParams)
            data = postData
            if data:
                if type(postData) not in [str, int, float, bool]:
                    data = json.dumps(postData)
            if not forcePost:
                if data and not len(data): 
                    data='\n' # temp fix, in case is no data in the file, to prevent post request from failing
                request = urllib2.Request(url=url, headers=headers, data=data)#,timeout=self.timeout)
            else:
                response = self.__forcePostCall__(forcePostUrl, sentQueryParams, headers)
            if method in ['PUT', 'DELETE']:
                if method == 'DELETE':
                    raise NotImplementedError("DELETE REST API calls aren't currently supported")
                response = self.__putCall__(url, headers, data)
                response =  response.split()[-1] # discard upload status msg (from curl put?)
        else:
            raise RestMethodException('Method ' + method + ' is not recognized.')

        # Make the request
        if not forcePost and not method in ['PUT', 'DELETE']: # the normal case
            try:
             response = urllib2.urlopen(request, timeout=self.timeout).read()
            except urllib2.HTTPError as e:                
                response = e.read() # treat http error as a response (handle in caller)                
            except urllib2.URLError as e:
                raise ServerResponseException('URLError: ' + str(e))            
        try:
            data = json.loads(response)
        except ValueError as e:
            raise ServerResponseException('Error decoding json in server response')
        return data            

    def deserialize(self, obj, objClass):
        """
        Deserialize a JSON string into a BaseSpacePy object.

        :param obj: A dictionary (or object?) to be deserialized into a class (objClass); or a value to be passed into a new native python type (objClass)
        :param objClass: A class object or native python type for the deserialized object, or a string of a class name or native python type. (eg, Project.Project, int, 'Project', 'int') 
        :returns: A deserialized object
        """        
        # Create an object class from objClass, if a string was passed in
        # Avoid native python types 'file'
        if type(objClass) == str:            
            try:
                if (not str(objClass)=='File'): 
                    objClass = eval(objClass.lower())
                else:
                    objClass = eval(objClass + '.' + objClass)
            except NameError: # not a native type, must be model class
                objClass = eval(objClass + '.' + objClass)
        
        # Create an instance of the object class
        # If the instance is a native python type, return it        
        if objClass in [str, int, float, bool]:
            return objClass(obj)
        instance = objClass()
        
        # For every swaggerType in the instance that is also in the passed-in obj,
        # set the instance value for native python types,
        # or recursively deserialize class instances.
        # For dynamic types, substitute real class after looking up 'Type' value.
        # For lists, deserialize all members of a list, including lists of lists (though not list of list of list...).
        # For datetimes, convert to a readable output string 
        for attr, attrType in instance.swaggerTypes.iteritems():
            if attr in obj:
                value = obj[attr]
                if attrType in ['str', 'int', 'float', 'bool']:
                    attrType = eval(attrType)
                    try:
                        value = attrType(value)
                    except UnicodeEncodeError:
                        value = unicode(value)
                    setattr(instance, attr, value)                            
                elif attrType == 'DynamicType':                                                
                    try:
                        model_name = instance._dynamicType[value['Type']]                
                    except KeyError:
                        pass
                        # suppress this warning, which is caused by a bug in BaseSpace
                        #warn("Warning - unrecognized dynamic type: " + value['Type'])                                                                                    
                    else:
                        setattr(instance, attr, self.deserialize(value, model_name))
                elif 'list<' in attrType:
                    match = re.match('list<(.*)>', attrType)
                    subClass = match.group(1)                    
                    subValues = []                       

                    # lists of dynamic type
                    if subClass == 'DynamicType':                             
                        for subValue in value:                            
                            try:
                                new_type = instance._dynamicType[subValue['Type']]                                
                            except KeyError:
                                pass 
                                # suppress this warning, which is caused by a bug in BaseSpace
                                #warn("Warning - unrecognized (list of) dynamic types: " + subValue['Type'])                                
                            else:
                                subValues.append(self.deserialize(subValue, new_type)) 
                        setattr(instance, attr, subValues)
                    # typical lists
                    else:                                                                             
                        for subValue in value:
                            subValues.append(self.deserialize(subValue, subClass))
                        setattr(instance, attr, subValues)
                # list of lists (e.g. map[] property type)
                elif 'listoflists<' in attrType:
                    match = re.match('listoflists<(.*)>', attrType)
                    subClass = match.group(1)                    
                    outvals = []                
                    for outval in value:
                        invals = []
                        for inval in outval:
                            invals.append(self.deserialize(inval, subClass))
                        outvals.append(invals)
                    setattr(instance, attr, outvals)
                                            
                elif attrType=='dict':                                          
                    setattr(instance, attr, value)
                elif attrType=='datetime':
                    dt = dateutil.parser.parse(value)
                    setattr(instance, attr, dt)
                else:
                    # recursive call with attribute type
                    setattr(instance, attr, self.deserialize(value, attrType))
        return instance
