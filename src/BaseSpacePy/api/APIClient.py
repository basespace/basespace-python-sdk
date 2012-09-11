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

import sys
import os
import re
import urllib
import urllib2
import pycurl
import io
import cStringIO
import json
from subprocess import *
import subprocess
#from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from model import *


class APIClient:
    def __init__(self, AccessToken=None, apiServer=None):
        if AccessToken == None:
            raise Exception('You must pass an access token when instantiating the '
                            'APIClient')
        self.apiKey = AccessToken
        self.apiServer = apiServer

    def __forcePostCall__(self,resourcePath,postData,headers,data=None):
        '''
        For forcing a post request using pycurl
        :param qParams:Query oaramter string
        :param resourcePath: The url 
        '''
#        print "Forcing post"
#        print resourcePath
        postData = [(p,postData[p]) for p in postData]
        headerPrep  = [k + ':' + headers[k] for k in headers.keys()]
        post =  urllib.urlencode(postData)
#        print headerPrep
#        print post
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL,resourcePath + '?' + post)
        c.setopt(pycurl.HTTPHEADER, headerPrep)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, post)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        return response.getvalue()

    def __putCall__(self,resourcePath,postData,headers,transFile):
        headerPrep  = [k + ':' + headers[k] for k in headers.keys()]
#        name = '/home/mkallberg/Desktop/multi/tempfiles/temp.bam' + resourcePath.split('/')[-1]  
#        f = open(name,'w')
#        f.write(data)
#        f.close()
#        f = open(name)
#        print len(f.read())
#        c = pycurl.Curl()
#        c.setopt(pycurl.URL,resourcePath)
#        c.setopt(pycurl.HTTPHEADER, headerPrep)
#        c.setopt(pycurl.PUT, 1)
#        c.setopt(pycurl.UPLOAD,dataInput)
#        c.setopt(pycurl.INFILESIZE,10239174)
#        c.setopt(c.WRITEFUNCTION, response.write)
#        c.perform()
#        c.close()
#        print resourcePath
#        
        cmd = 'curl -H "x-access-token:' + self.apiKey + '" -H "Content-MD5:' + headers['Content-MD5'].strip() +'" -T "'+ transFile +'" -X PUT ' + resourcePath
        ##cmd = data +'|curl -H "x-access-token:' + self.apiKey + '" -H "Content-MD5:' + headers['Content-MD5'].strip() +'" -d @- -X PUT ' + resourcePath
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        return output
        

    def callAPI(self, resourcePath, method, queryParams, postData,
                headerParams=None,forcePost=0):

        url = self.apiServer + resourcePath
        headers = {}
        if headerParams:
            for param, value in headerParams.iteritems():
                headers[param] = value

        if not headers.has_key('Content-Type') and not method=='PUT': headers['Content-Type'] = 'application/json'
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
#            print "!!! " + str(url)
#            print "!!! " + str(data)
            if not forcePost:
                if data and not len(data): data='\n' # temp fix, in case is no data in the file, to prevent post request from failing
                request = urllib2.Request(url=url, headers=headers, data=data)
            else:                                    # use pycurl to force a post call, even w/o data
                response = self.__forcePostCall__(forcePostUrl,sentQueryParams,headers)
            if method in ['PUT', 'DELETE']: #urllib doesnt do put and delete, default to pycurl here
                response = self.__putCall__(url, queryParams, headers, data)
                response =  response.split()[-1]
                
        else:
            raise Exception('Method ' + method + ' is not recognized.')

        # Make the request, request may raise 403 forbidden, or 404 non-response
        if not forcePost and not method in ['PUT', 'DELETE']:                                      # the normal case
#            print url
            #print request
            response = urllib2.urlopen(request).read()
            
        try:
            data = json.loads(response)
        except Exception, err:
            err
            data= None
        return data

    def toPathValue(self, obj):
        """Serialize a list to a CSV string, if necessary.
        Args:
            obj -- data object to be serialized
        Returns:
            string -- json serialization of object
        """
        if type(obj) == list:
            return ','.join(obj)
        else:
            return obj

    def deserialize(self, obj, objClass):
        """Derialize a JSON string into an object.

        Args:
            obj -- string or object to be deserialized
            objClass -- class literal for deserialzied object, or string
                of class name
        Returns:
            object -- deserialized object"""

        # Have to accept objClass as string or actual type. Type could be a
        # native Python type, or one of the model classes.
        if type(objClass) == str:
            try:
                if not str(objClass)=='File':                # Hack to avoid native python-type 'file' (non-capital 'f')
                    objClass = eval(objClass.lower())
                else:
                    objClass = eval(objClass + '.' + objClass)
            except NameError: # not a native type, must be model class
                objClass = eval(objClass + '.' + objClass)

        if objClass in [str, int, float, bool]:
            return objClass(obj)
        instance = objClass()
        
        for attr, attrType in instance.swaggerTypes.iteritems():
            if attr in obj:
#                print '@@@@ ' + str(obj)
#                print '@@@@ ' + str(attr)
#                print '@@@@ ' + str(attrType)
                value = obj[attr]
#                print value
                if attrType in ['str', 'int', 'float', 'bool']:
                    attrType = eval(attrType)
                    try:
                        value = attrType(value)
                    except UnicodeEncodeError:
                        value = unicode(value)
                    setattr(instance, attr, value)
                elif 'list<' in attrType:
                    match = re.match('list<(.*)>', attrType)
                    subClass = match.group(1)
                    subValues = []

                    for subValue in value:
                        subValues.append(self.deserialize(subValue, subClass))
                    setattr(instance, attr, subValues)
                elif attrType=='dict':                                          # support for parsing dictionary
#                    pprint(value)                   
                    setattr(instance, attr,value)
                else:
#                    print "recursive call w/ " + attrType
                    setattr(instance, attr, self.deserialize(value,attrType))

        return instance
