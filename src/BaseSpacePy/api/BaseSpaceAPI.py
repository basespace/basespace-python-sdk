
from pprint import pprint
import urllib2
import shutil
import urllib
import httplib
import cStringIO
import json
import os
import re
from tempfile import mkdtemp
import socket
import ConfigParser
import urlparse
import logging

from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseAPI import BaseAPI
from BaseSpacePy.api.BaseSpaceException import *
from BaseSpacePy.model.MultipartFileTransfer import MultipartUpload as mpu
from BaseSpacePy.model.MultipartFileTransfer import MultipartDownload as mpd
from BaseSpacePy.model.QueryParameters import QueryParameters as qp
from BaseSpacePy.model import *

# Uris for obtaining a access token, user verification code, and app trigger information
tokenURL                   = '/oauthv2/token'
deviceURL                  = "/oauthv2/deviceauthorization"
webAuthorize               = '/oauth/authorize'

# other constants
# resource types permitted by the generic properties API:
# https://developer.basespace.illumina.com/docs/content/documentation/rest-api/api-reference#Properties
PROPERTY_RESOURCE_TYPES = set([ "samples", "appresults", "runs", "appsessions", "projects" ])


class BaseSpaceAPI(BaseAPI):
    '''
    The main API class used for all communication with the REST server
    '''
    def __init__(self, clientKey=None, clientSecret=None, apiServer=None, version=None, appSessionId='', AccessToken='', userAgent=None, timeout=10, verbose=0, profile='DEFAULT'):
        '''
        The following arguments are required in either the constructor or a config file (~/.basespacepy.cfg):        
        
        :param clientKey: the client key of the user's app; required in constructor or config file
        :param clientSecret: the client secret of the user's app; required in constructor or config file
        :param apiServer: the URL of the BaseSpace api server; required in constructor or config file
        :param version: the version of the BaseSpace API; required in constructor or config file
        :param appSessionId: optional, though may be needed for AppSession-related methods
        :param AccessToken: optional, though will be needed for most methods (except to obtain a new access token)
        :param timeout: optional, timeout period in seconds for api calls, default 10 
        :param profile: optional, name of profile in config file, default 'DEFAULT'
        '''
        
        cred = self._setCredentials(clientKey, clientSecret, apiServer, version, appSessionId, AccessToken, profile)
            
        self.appSessionId   = cred['appSessionId']
        self.key            = cred['clientKey']
        self.secret         = cred['clientSecret']
        self.apiServer      = cred['apiServer']
        self.version        = cred['apiVersion']
        if 'profile' in cred:
            self.profile    = cred['profile']
        # TODO this replacement won't work for all environments
        self.weburl         = cred['apiServer'].replace('api.','')
        
        apiServerAndVersion = urlparse.urljoin(cred['apiServer'], cred['apiVersion'])
        super(BaseSpaceAPI, self).__init__(cred['accessToken'], apiServerAndVersion, userAgent, timeout, verbose)

    def _setCredentials(self, clientKey, clientSecret, apiServer, apiVersion, appSessionId, accessToken, profile):
        '''
        Returns credentials from constructor, config file, or default (for optional args), in this priority order
        for each credential.
        If clientKey was provided only in config file, include 'name' (in return dict) with profile name.
        Raises exception if required creds aren't provided (clientKey, clientSecret, apiServer, apiVersion).

        :param clientKey: the client key of the user's app
        :param clientSecret: the client secret of the user's app
        :param apiServer: the URL of the BaseSpace api server
        :param version: the version of the BaseSpace API
        :param appSessionId: the AppSession Id
        :param AccessToken: an access token        
        :param profile: name of profile in config file        
        :returns: dictionary with credentials from constructor, config file, or default (for optional args), in this priority order.
        '''
        lcl_cred = self._getLocalCredentials(profile)
        cred = {}
        # required credentials
        if clientKey is not None:
            cred['clientKey'] = clientKey
        else:
            try:
                cred['clientKey'] = lcl_cred['clientKey']
            except KeyError:        
                raise CredentialsException('Client Key not available - please provide in BaseSpaceAPI constructor or config file')
            else:
                # set profile name
                if 'name' in lcl_cred:
                    cred['profile'] = lcl_cred['name']
                else:
                    cred['profile'] = profile
        if clientSecret is not None:
            cred['clientSecret'] = clientSecret
        else:
            try:
                cred['clientSecret'] = lcl_cred['clientSecret']
            except KeyError:        
                raise CredentialsException('Client Secret not available - please provide in BaseSpaceAPI constructor or config file')
        if apiServer is not None:
            cred['apiServer'] = apiServer
        else:
            try:
                cred['apiServer'] = lcl_cred['apiServer']
            except KeyError:        
                raise CredentialsException('API Server URL not available - please provide in BaseSpaceAPI constructor or config file')
        if apiVersion is not None:
            cred['apiVersion'] = apiVersion
        else:
            try:
                cred['apiVersion'] = lcl_cred['apiVersion']
            except KeyError:        
                raise CredentialsException('API version available - please provide in BaseSpaceAPI constructor or config file')        
        # Optional credentials 
        if appSessionId:
            cred['appSessionId'] = appSessionId
        elif 'apiVersion' in lcl_cred:
            try:
                cred['appSessionId'] = lcl_cred['appSessionId']
            except KeyError:
                cred['appSessionId'] = appSessionId
        else:
            cred['appSessionId'] = appSessionId
        
        if accessToken:
            cred['accessToken'] = accessToken
        elif 'accessToken' in lcl_cred:            
            try:
                cred['accessToken'] = lcl_cred['accessToken']
            except KeyError:
                cred['accessToken'] = accessToken
        else:
            cred['accessToken'] = accessToken
        
        return cred            

    def _getLocalCredentials(self, profile):
        '''
        Returns credentials from local config file (~/.basespacepy.cfg)
        If some or all credentials are missing, they aren't included the in the returned dict
        
        :param profile: Profile name from local config file 
        :returns: A dictionary with credentials from local config file 
        '''
        config_file = os.path.expanduser('~/.basespacepy.cfg')
        cred = {}        
        config = ConfigParser.SafeConfigParser()
        if config.read(config_file):
            if not config.has_section(profile) and profile.lower() != 'default':                
                raise CredentialsException("Profile name '%s' not present in config file %s" % (profile, config_file))
            try:
                cred['name'] = config.get(profile, "name")
            except ConfigParser.NoOptionError:
                pass
            try:
                cred['clientKey'] = config.get(profile, "clientKey")
            except ConfigParser.NoOptionError:
                pass
            try:
                cred['clientSecret'] = config.get(profile, "clientSecret")
            except ConfigParser.NoOptionError:
                pass
            try:
                cred['apiServer'] = config.get(profile, "apiServer")
            except ConfigParser.NoOptionError:
                pass
            try:
                cred['apiVersion'] = config.get(profile, "apiVersion")
            except ConfigParser.NoOptionError:
                pass
            try: 
                cred['appSessionId'] = config.get(profile, "appSessionId")
            except ConfigParser.NoOptionError:
                pass
            try:
                cred['accessToken'] = config.get(profile, "accessToken")
            except ConfigParser.NoOptionError:
                pass            
        return cred

    def getAppSessionById(self, Id):
        '''
        Get metadata about an AppSession.
        Note that the client key and secret must match those of the AppSession's Application.
        
        :param Id: The Id of the AppSession
        :returns: An AppSession instance
        '''            
        return self.getAppSession(Id=Id)

    def getAppSessionOld(self, Id=None):
        '''
        Get metadata about an AppSession.         
        Note that the client key and secret must match those of the AppSession's Application.    
        
        :param Id: an AppSession Id; if not provided, the AppSession Id of the BaseSpaceAPI instance will be used 
        :returns: An AppSession instance                
        '''
        # pycurl is hard to get working, so best to cauterise it into only the functions where it is needed
        if Id is None:
            Id = self.appSessionId
        if not Id:
            raise AppSessionException("An AppSession Id is required")
        resourcePath = self.apiClient.apiServerAndVersion + '/appsessions/{AppSessionId}'        
        resourcePath = resourcePath.replace('{AppSessionId}', Id)        
        response = cStringIO.StringIO()
        # import pycurl
        # c = pycurl.Curl()
        # c.setopt(pycurl.URL, resourcePath)
        # c.setopt(pycurl.USERPWD, self.key + ":" + self.secret)
        # c.setopt(c.WRITEFUNCTION, response.write)
        # c.perform()
        # c.close()
        # resp_dict = json.loads(response.getvalue())        
        import requests
        response = requests.get(resourcePath, auth=(self.key, self.secret))
        resp_dict = json.loads(response.text)
        return self.__deserializeAppSessionResponse__(resp_dict) 

    def getAppSession(self, Id=None, queryPars=None):
        if Id is None:
            Id = self.appSessionId
        if not Id:
            raise AppSessionException("An AppSession Id is required")
        resourcePath = '/appsessions/{AppSessionId}'        
        resourcePath = resourcePath.replace('{AppSessionId}', Id)        
        method = 'GET'
        headerParams = {}
        queryParams = {}
        return self.__singleRequest__(AppSessionResponse.AppSessionResponse, resourcePath, method, queryParams, headerParams)

    def __deserializeAppSessionResponse__(self, response):
        '''
        Converts a AppSession response from the API server to an AppSession object.        
        
        :param response: a dictionary (decoded from json) from getting an AppSession from the api server
        :returns: An AppSession instance                
        '''        
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise AppSessionException('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])                    
        tempApi = APIClient(AccessToken='', apiServerAndVersion=self.apiClient.apiServerAndVersion, userAgent=self.apiClient.userAgent)
        res = tempApi.deserialize(response, AppSessionResponse.AppSessionResponse)            
        return res.Response.__deserializeReferences__(self)

    def getAppSessionPropertiesById(self, Id, queryPars=None):
        '''
        Returns the Properties of an AppSession
        
        :param Id: An AppSession Id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: A PropertyList instance            
        '''                
        queryParams = self._validateQueryParameters(queryPars)            
        resourcePath = '/appsessions/{Id}/properties'
        resourcePath = resourcePath.replace('{Id}',Id)
        method = 'GET'        
        headerParams = {}                
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse, resourcePath, method, queryParams, headerParams)

    def getAppSessionPropertyByName(self, Id, name, queryPars=None):
        '''
        Returns the multi-value Property of the provided AppSession that has the provided Property name.
        Note - this method (and REST API) is supported for ONLY multi-value Properties.
        
        :param Id: The AppSessionId
        :param name: Name of the multi-value property to retrieve
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: A multi-value propertylist instance such as MultiValuePropertyAppResultsList (depending on the Property Type)        
        '''
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/appsessions/{Id}/properties/{Name}/items'
        resourcePath = resourcePath.replace('{Id}', Id)
        resourcePath = resourcePath.replace('{Name}', name)        
        method = 'GET'        
        headerParams = {}
        return self.__singleRequest__(MultiValuePropertyResponse.MultiValuePropertyResponse, resourcePath, method, queryParams, headerParams)
                    
    def getAppSessionInputsById(self, Id, queryPars=None):
        '''
        Returns the input properties of an AppSession
        
        :param Id: An AppSessionId
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a dictionary of input properties, keyed by input Name      
        '''            
        props = self.getAppSessionPropertiesById(Id, queryPars)
        inputs = {}
        for prop in props.Items:
            match = re.search("^Input\.(.+)", prop.Name)
            if match != None:
                inputs[match.group(1)] = prop
        return inputs

    def setAppSessionState(self, Id, Status, Summary):
        '''
        Set the Status and StatusSummary of an AppSession in BaseSpace.
        Note - once Status is set to Completed or Aborted, no further changes can made.
        
        :param Id: The id of the AppSession
        :param Status: The AppSession status string, must be one of: Running, Complete, NeedsAttention, TimedOut, Aborted
        :param Summary: The status summary string
        :returns: An updated AppSession instance
        '''
        resourcePath = '/appsessions/{Id}'        
        method = 'POST'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        postData = {}
        statusAllowed = ['running', 'complete', 'needsattention', 'timedout', 'aborted']
        if not Status.lower() in statusAllowed:
            raise AppSessionException("AppSession state must be one of: " + str(statusAllowed))
        postData['status'] = Status.lower()
        postData['statussummary'] = Summary
        return self.__singleRequest__(AppSessionResponse.AppSessionResponse, resourcePath, method, queryParams, headerParams, postData=postData)

    def __deserializeObject__(self, dct, type):
        '''
        Converts API response into object instances for Projects, Samples, and AppResults.
        For other types, the input value is simply returned.
        
        (Currently called by Sample's getReferencedAppResults() and 
        AppSessionLaunchObject's __deserializeObject__() to serialize References)

        :param dct: dictionary from an API response (converted from JSON) for a BaseSpace item (eg., a Project)
        :param type: BaseSpace item name
        :returns: for types Project, Sample, and AppResult, an object is returned; for other types, the input dict is returned.
        '''
        tempApi = APIClient(AccessToken='', apiServerAndVersion=self.apiClient.apiServerAndVersion, userAgent=self.apiClient.userAgent)
        if type.lower()=='project':
            return tempApi.deserialize(dct, Project.Project)
        if type.lower()=='sample':
            return tempApi.deserialize(dct, Sample.Sample)
        if type.lower()=='appresult':
            return tempApi.deserialize(dct, AppResult.AppResult)        
        return dct            
                
    def getAccess(self, obj, accessType='write', web=False, redirectURL='', state=''):
        '''
        Requests access to the provided BaseSpace object.
        
        :param obj: The data object we wish to get access to -- must be a Project, Sample, AppResult, or Run.
        :param accessType: (Optional) the type of access (browse|read|write|create), default is write. Create is only supported for Projects.
        :param web: (Optional) true if the App is web-based, default is false meaning a device based app
        :param redirectURL: (Optional) Redirect URL for the web-based case
        :param state: (Optional) A parameter that will passed through to the redirect response.
        :raises ModelNotSupportedException: for classes of objects not supported by this method
        :returns: for device requests, a dictionary of server response; for web requests, a url to to send the user to
        '''
        try:
            scopeStr = obj.getAccessStr(scope=accessType)
        except AttributeError:
            raise ModelNotSupportedException("Error - the class of the provided object is not supported for this method")
        if web:
            return self.getWebVerificationCode(scopeStr, redirectURL, state)
        else:
            return self.getVerificationCode(scopeStr)
        
    def getVerificationCode(self, scope):
        '''
        For non-web applications (eg. devices), returns the device code 
        and verification url for the user to approve access to a specific data scope.  
            
        :param scope: The scope that access is requested for (e.g. 'browse project 123')
        :returns: dictionary of server response
        '''
        data = [('client_id', self.key), ('scope', scope),('response_type', 'device_code')]
        return self.__makeCurlRequest__(data, self.apiClient.apiServerAndVersion + deviceURL)

    def getWebVerificationCode(self, scope, redirectURL, state=''):
        '''
        Generates the URL the user should be redirected to for web-based authentication
         
        :param scope: The scope that access is requested for (e.g. 'browse project 123')
        :param redirectURL: The redirect URL
        :param state: (Optional) A state parameter that will passed through to the redirect response
        :returns: a url 
        '''        
        data = {'client_id': self.key, 'redirect_uri': redirectURL, 'scope': scope, 'response_type': 'code', "state": state}
        return self.weburl + webAuthorize + '?' + urllib.urlencode(data)

    def obtainAccessToken(self, code, grantType='device', redirect_uri=None):
        '''
        Returns a user specific access token, for either device (non-web) or web apps.   
        
        :param code: The device code returned by the getVerificationCode method
        :param grantType: Grant-type may be either 'device' for non-web apps (default), or 'authorization_code' for web apps 
        :param redirect_uri: The uri to redirect to; required for web apps only.
        :raises OAuthException: when redirect_uri isn't provided by web apps
        :returns: an access token
        '''
        if grantType=='authorization_code' and redirect_uri is None:
            raise OAuthException('A Redirect URI is requred for web apps to obtain access tokens')
        data = [('client_id', self.key), ('client_secret', self.secret), ('code', code), ('grant_type', grantType), ('redirect_uri', redirect_uri)]
        resp_dict = self.__makeCurlRequest__(data, self.apiClient.apiServerAndVersion + tokenURL)
        return str(resp_dict['access_token'])

    def updatePrivileges(self, code, grantType='device', redirect_uri=None):
        '''
        Retrieves a user-specific access token, and sets the token on the current object.

        :param code: The device code returned by the getVerificationCode method
        :param grantType: Grant-type may be either 'device' for non-web apps (default), or 'authorization_code' for web apps 
        :param redirect_uri: The uri to redirect to; required for web apps only.
        :returns: None        
        '''
        token = self.obtainAccessToken(code, grantType=grantType, redirect_uri=redirect_uri)
        self.setAccessToken(token)
            
    def createProject(self, Name):
        '''
        Creates a project with the specified name and returns a project object. 
        If a project with this name already exists, the existing project is returned.
        
        :param Name: Name of the project
        :returns: a Project instance of the newly created project        
        '''        
        resourcePath            = '/projects/'        
        method                  = 'POST'
        queryParams             = {}
        headerParams            = {}
        postData                = {}
        postData['Name']        = Name        
        return self.__singleRequest__(ProjectResponse.ProjectResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData)

    def launchApp(self, appId, configJson):
        resourcePath            = '/applications/%s/appsessions' % appId
        method                  = 'POST'
        queryParams             = {}
        headerParams            = { 'Content-Type' : "application/json" }
        postData                = configJson
        return self.__singleRequest__(AppLaunchResponse.AppLaunchResponse, 
                                      resourcePath, method, queryParams, headerParams, postData=postData)

    def getUserById(self, Id):
        '''
        Returns the User object corresponding to User Id
        
        :param Id: The Id of the user
        :returns: a User instance
        '''        
        resourcePath = '/users/{Id}'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(UserResponse.UserResponse, resourcePath, method, queryParams, headerParams)
           
    def getAppResultFromAppSessionId(self, Id, appResultName=""):
        '''
        Returns an AppResult object from an AppSession Id. 
        if appResultName is supplied, look for an appresult with this name
        otherwise, expect there to be exactly one appresult

        :param Id: The Id of the AppSession
        :param appResultName: The name of the appresult to return
        :returns: An AppResult instance
        '''
        ars = self.getAppSessionPropertyByName(Id, 'Output.AppResults')
        if len(ars.Items) != 1:
            if appResultName:
                for ar in ars.Items:
                    if ar.Content.Name == appResultName:
                        return ar
                raise AppSessionException("App session: %s had more than on appresult without the specified %s" % (Id, appResultName))
            else:
                raise AppSessionException("App session: %s did not have exactly one AppResult" % Id)
        appresult = ars.Items[0]
        return appresult

    def getAppResultById(self, Id, queryPars=None):
        '''
        Returns an AppResult object corresponding to Id
        
        :param Id: The Id of the AppResult
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: an AppResult instance
        '''        
        queryParams = self._validateQueryParameters(queryPars)
        resourcePath = '/appresults/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)        
        headerParams = {}
        return self.__singleRequest__(AppResultResponse.AppResultResponse,resourcePath, method, queryParams, headerParams)

    def getAppResultPropertiesById(self, Id, queryPars=None):
        '''
        Returns the Properties of an AppResult object corresponding to AppResult Id
        
        :param Id: The Id of the AppResult
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a PropertyList instance
        '''                    
        queryParams = self._validateQueryParameters(queryPars)        
        resourcePath = '/appresults/{Id}/properties'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)                
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse, resourcePath, method, queryParams, headerParams)

    def getAppResultFilesById(self, Id, queryPars=None):
        '''
        Returns a list of File object for an AppResult
        
        :param Id: The id of the AppResult
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of File instances 
        '''
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/appresults/{Id}/files'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'        
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(File.File,resourcePath, method, queryParams, headerParams)

    def getAppResultFiles(self, Id, queryPars=None):
        '''
        * Deprecated in favor of getAppResultFileById() *
        
        Returns a list of File object for an AppResult
        
        :param Id: The id of the AppResult
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of File instances 
        '''
        return self.getAppResultFilesById(Id, queryPars)

    def downloadAppResultFilesByExtension(self, Id, extension, localDir, appResultName="", queryPars=None):
        '''
        Convenience method to dowload all the files in an AppSession's AppResult that match a file extension
        Uses fileDownload without in its simplest form - may need to be refined later.

        :param Id: The AppSession Id
        :param pattern: The regexp pattern to look for in the generated files
        :param localDir: The local directory where files will be downloaded to
        :param queryPars: the additional query parameters to pass into the appresult call (primarily to remove limits)
        :returns a list of File instances
        '''
        appResult = self.getAppResultFromAppSessionId(Id, appResultName)
        appResultId = appResult.Content.Id
        appResultFiles = self.getAppResultFiles(appResultId, queryPars)
        allDownloads = []
        for appResultFile in appResultFiles:
            fileName = appResultFile.Name
            if fileName.endswith(extension):
                fileId = appResultFile.Id
                download = self.fileDownload(fileId, localDir)
                allDownloads.append(download)
        return allDownloads

    def getProjectById(self, Id, queryPars=None):
        '''
        Request a project object by Id
        
        :param Id: The Id of the project
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a Project instance
        '''
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/projects/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)        
        headerParams = {}
        return self.__singleRequest__(ProjectResponse.ProjectResponse, resourcePath, method, queryParams, headerParams)

    def getProjectPropertiesById(self, Id, queryPars=None):
        '''
        Request the Properties of a project object by Id
        
        :param Id: The Id of the project
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a ProjectList instance
        '''
        queryParams = self._validateQueryParameters(queryPars)       
        resourcePath = '/projects/{Id}/properties'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)        
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse,resourcePath, method, queryParams, headerParams)
           
    def getProjectByUser(self, queryPars=None):
        '''
        Returns a list available projects for the current User.
                
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Project instances
        '''
        queryParams = self._validateQueryParameters(queryPars)               
        resourcePath = '/users/current/projects'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'        
        headerParams = {}
        return self.__listRequest__(Project.Project,resourcePath, method, queryParams, headerParams)
       
    def getAccessibleRunsByUser(self, queryPars=None):
        '''
        Returns a list of accessible runs for the current User
                
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Run instances
        '''        
        queryParams = self._validateQueryParameters(queryPars)               
        resourcePath = '/users/current/runs'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'        
        headerParams = {}
        return self.__listRequest__(Run.Run, resourcePath, method, queryParams, headerParams)
    
    def getRunById(self, Id, queryPars=None):
        '''        
        Request a run object by Id
        
        :param Id: The Id of the run
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a Run instance
        '''        
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/runs/{Id}'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)            
        headerParams = {}
        return self.__singleRequest__(RunResponse.RunResponse,resourcePath, method, queryParams, headerParams)
    
    def getRunPropertiesById(self, Id, queryPars=None):
        '''        
        Request the Properties of a run object by Id
        
        :param Id: The Id of the run
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a PropertyList instance
        '''        
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/runs/{Id}/properties'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)        
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse,resourcePath, method, queryParams, headerParams)

    def getRunFilesById(self, Id, queryPars=None):
        '''        
        Request the files associated with a Run, using the Run's Id
        
        :param Id: The Id of the run
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Run instances
        '''        
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/runs/{Id}/files'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)            
        headerParams = {}         
        return self.__listRequest__(File.File,resourcePath, method, queryParams, headerParams)

    def getRunSamplesById(self, Id, queryPars=None):
        '''        
        Request the Samples associated with a Run, using the Run's Id
        
        :param Id: The Id of the run
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Sample instances
        '''        
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/runs/{Id}/samples'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)            
        headerParams = {}         
        return self.__listRequest__(Sample.Sample,resourcePath, method, queryParams, headerParams)
  
    def getAppResultsByProject(self, Id, queryPars=None, statuses=None):
        '''
        Returns a list of AppResult object associated with the project with Id
        
        :param Id: The project id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :param statuses: An (optional) list of AppResult statuses to filter by, eg., 'complete'
        :returns: a list of AppResult instances
        '''
        queryParams = self._validateQueryParameters(queryPars) 
        if statuses is None:
            statuses = []               
        resourcePath = '/projects/{Id}/appresults'        
        method = 'GET'        
        if len(statuses): 
            queryParams['Statuses'] = ",".join(statuses)
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(AppResult.AppResult,resourcePath, method, queryParams, headerParams)

    def getSamplesByProject(self, Id, queryPars=None):
        '''
        Returns a list of samples associated with a project with Id
        
        :param Id: The id of the project
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Sample instances
        '''
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/projects/{Id}/samples'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'        
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(Sample.Sample,resourcePath, method, queryParams, headerParams)

    def getSampleById(self, Id, queryPars=None):
        '''
        Returns a Sample object
        
        :param Id: The id of the sample
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a Sample instance
        '''
        queryParams = self._validateQueryParameters(queryPars)        
        resourcePath = '/samples/{Id}'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)        
        headerParams = {}
        return self.__singleRequest__(SampleResponse.SampleResponse, resourcePath, method, queryParams, headerParams)
    
    def getSamplePropertiesById(self, Id, queryPars=None):
        '''
        Returns the Properties of a Sample object
        
        :param Id: The id of the sample
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a PropertyList instance
        '''
        queryParams = self._validateQueryParameters(queryPars)
        resourcePath = '/samples/{Id}/properties'
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse,
                                      resourcePath, method, queryParams, headerParams)

    def getSampleFilesById(self, Id, queryPars=None):
        '''
        Returns a list of File objects associated with a Sample
        
        :param Id: A Sample id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of File instances
        '''
        queryParams = self._validateQueryParameters(queryPars)
        resourcePath = '/samples/{Id}/files'        
        method = 'GET'        
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(File.File,
                                    resourcePath, method, queryParams, headerParams)

    def getFilesBySample(self, Id, queryPars=None):
        '''
        * Deprecated in favor of getSampleFilesById() *
        
        Returns a list of File objects associated with a Sample
        
        :param Id: A Sample id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of File instances
        '''
        return self.getSampleFilesById(Id, queryPars)        
    
    def getFileById(self, Id, queryPars=None):
        '''
        Returns a file object by Id
        
        :param Id: The id of the file
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a File instance
        '''
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/files/{Id}'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)            
        headerParams = {}
        return self.__singleRequest__(FileResponse.FileResponse,
                                      resourcePath, method, queryParams, headerParams)
        
    def getFilePropertiesById(self, Id, queryPars=None):
        '''
        Returns the Properties of a file object by Id
        
        :param Id: The id of the file
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a PropertyList instance
        '''        
        queryParams = self._validateQueryParameters(queryPars)                
        resourcePath = '/files/{Id}/properties'        
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)            
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse,
                                      resourcePath, method, queryParams, headerParams)

    def getGenomeById(self, Id, ):
        '''
        Returns an instance of Genome with the specified Id
        
        :param Id: The genome id
        :returns: a GenomeV1 instance
        '''
        # Parse inputs
        resourcePath = '/genomes/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(GenomeResponse.GenomeResponse,
                                      resourcePath, method, queryParams, headerParams)

    def getAvailableGenomes(self, queryPars=None):
        '''
        Returns a list of all available genomes
        
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of GenomeV1 instances
        '''        
        queryParams = self._validateQueryParameters(queryPars)
        resourcePath = '/genomes'
        method = 'GET'
        headerParams = {}
        return self.__listRequest__(GenomeV1.GenomeV1,
                                    resourcePath, method, queryParams, headerParams)

    def getIntervalCoverage(self, Id, Chrom, StartPos, EndPos):
        '''
        Returns metadata about an alignment, including max coverage and cov granularity.
        Note that HrefCoverage must be available for the provided BAM file.       
        
        :param Id: the Id of a BAM file
        :param Chrom: chromosome name
        :param StartPos: get coverage starting at this position
        :param EndPos: get coverage up to and including this position; the returned EndPos may be larger than requested due to rounding up to nearest window end coordinate        
        :returns: a Coverage instance
        '''
        resourcePath = '/coverage/{Id}/{Chrom}'
        method = 'GET'
        queryParams = {}
        headerParams = {}
        queryParams['StartPos'] = StartPos
        queryParams['EndPos'] = EndPos
        resourcePath = resourcePath.replace('{Chrom}', Chrom)
        resourcePath = resourcePath.replace('{Id}', Id)
        return self.__singleRequest__(CoverageResponse.CoverageResponse,
                                      resourcePath, method, queryParams, headerParams)

    def getCoverageMetaInfo(self, Id, Chrom):
        '''
        Returns metadata about coverage of a chromosome.
        Note that HrefCoverage must be available for the provided BAM file
        
        :param Id: the Id of a Bam file
        :param Chrom: chromosome name
        :returns: a CoverageMetaData instance
        '''
        resourcePath = '/coverage/{Id}/{Chrom}/meta'
        method = 'GET'
        queryParams = {}
        headerParams = {}
        resourcePath = resourcePath.replace('{Chrom}', Chrom)
        resourcePath = resourcePath.replace('{Id}', Id)        
        return self.__singleRequest__(CoverageMetaResponse.CoverageMetaResponse,
                                      resourcePath, method, queryParams, headerParams)

    def filterVariantSet(self,Id, Chrom, StartPos, EndPos, Format='json', queryPars=None):
        '''
        List the variants in a set of variants. Note the maximum returned records is 1000.
        
        :param Id: The id of the variant file 
        :param Chrom: Chromosome name
        :param StartPos: The start position of the sequence of interest
        :param EndPos: The start position of the sequence of interest
        :param Format: (optional) Format for results, possible values: 'vcf' (not implemented yet), 'json'(default, which actually returns an object)
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Variant instances, when Format is json; a string, when Format is vcf
        '''
        queryParams = self._validateQueryParameters(queryPars)
        resourcePath = '/variantset/{Id}/variants/{Chrom}'
        method = 'GET'        
        headerParams = {}
        queryParams['StartPos'] = StartPos
        queryParams['EndPos']   = EndPos
        queryParams['Format']   = Format
        resourcePath = resourcePath.replace('{Chrom}', Chrom)
        resourcePath = resourcePath.replace('{Id}', Id)
        if Format == 'vcf':
            raise NotImplementedError("Returning native VCF format isn't yet supported by BaseSpacePy")
        else:
            return self.__listRequest__(Variant.Variant, resourcePath, method, queryParams, headerParams)

    def getVariantMetadata(self, Id, Format='json'):
        '''        
        Returns the header information of a VCF file.
        
        :param Id: The Id of the VCF file
        :param Format: (optional) The return-value format, set to 'json' (default) to return return an object (not actually json format), or 'vcf' (not implemented yet) to return a string in VCF format.
        :returns: A VariantHeader instance
        '''
        resourcePath = '/variantset/{Id}'        
        method = 'GET'
        queryParams = {}
        headerParams = {}
        queryParams['Format'] = Format
        resourcePath = resourcePath.replace('{Id}', Id)
        if Format == 'vcf':
            raise NotImplementedError("Returning native VCF format isn't yet supported by BaseSpacePy")
        else:
            return self.__singleRequest__(VariantsHeaderResponse.VariantsHeaderResponse,
                                          resourcePath, method, queryParams, headerParams)
         
    def createAppResult(self, Id, name, desc, samples=None, appSessionId=None):
        '''
        Create an AppResult object.
        
        :param Id: The id of the project in which the AppResult is to be added
        :param name: The name of the AppResult
        :param desc: A description of the AppResult
        :param samples: (Optional) A list of one or more Samples Ids that the AppResult is related to 
        :param appSessionId: (Optional) If no appSessionId is given, the id used to initialize the BaseSpaceAPI instance will be used. If appSessionId is set equal to an empty string, a new appsession will be created for the appresult object 
        :raises Exception: when attempting to create AppResult in an AppSession that has a status other than 'running'.
        :returns: a newly created AppResult instance
        '''
        if (not self.appSessionId) and (appSessionId==None):
            raise Exception("This BaseSpaceAPI instance has no appSessionId set and no alternative id was supplied for method createAppResult")
        if samples is None:
            samples = []
        resourcePath = '/projects/{ProjectId}/appresults'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'
        resourcePath = resourcePath.replace('{ProjectId}', Id)
        queryParams = {}
        headerParams = {}
        postData = {}
        
        if appSessionId:
            queryParams['appsessionid'] = appSessionId
        if appSessionId==None:
            queryParams['appsessionid'] = self.appSessionId      # default case, we use the current appsession
        
        # add the sample references
        if len(samples):
            ref = []
            for s in samples:
                d = {"Rel": "using", "Type": "Sample", "HrefContent": self.version + '/samples/' + s.Id}
                ref.append(d)
            postData['References']  = ref
        # case, an appSession is provided, we need to check if the app is running
        if queryParams.has_key('appsessionid'):
            session = self.getAppSession(Id=queryParams['appsessionid'])
            if not session.canWorkOn():
                raise Exception('AppSession status must be "running," to create an AppResults. Current status is ' + session.Status)
            
        postData['Name'] = name
        postData['Description'] = desc
        return self.__singleRequest__(AppResultResponse.AppResultResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData)
            
    def appResultFileUpload(self, Id, localPath, fileName, directory, contentType):
        '''
        Uploads a file associated with an AppResult to BaseSpace and returns the corresponding file object.
        Small files are uploaded with a single-part upload method, while larger files (> 25 MB) are uploaded
        with multipart upload.
        
        :param Id: AppResult id.
        :param localPath: The local path to the file to be uploaded, including file name.
        :param fileName: The desired filename in the AppResult folder on the BaseSpace server.
        :param directory: The directory the file should be placed in on the BaseSpace server.
        :param contentType: The content-type of the file, eg. 'text/plain' for text files, 'application/octet-stream' for binary files
        :returns: a newly created File instance    
        '''
        multipart_min_file_size = 25000000 # bytes
        if os.path.getsize(localPath) > multipart_min_file_size:
            return self.multipartFileUpload('appresults',Id, localPath, fileName, directory, contentType)
        else:
            return self.__singlepartFileUpload__('appresults',Id, localPath, fileName, directory, contentType)

    def createSample(self, Id, name, experimentName, sampleNumber, sampleTitle, readLengths, countRaw, countPF, reference=None, appSessionId=None):
        '''
        Create a Sample object.
        
        :param Id: The id of the project in which the Sample is to be added
        :param name: The name of the Sample
        :param reference: (Optional) Reference genome that the sample relates to 
        :param appSessionId: (Optional) If no appSessionId is given, the id used to initialize the BaseSpaceAPI instance will be used. If appSessionId is set equal to an empty string, a new appsession will be created for the sample object 
        :raises Exception: when attempting to create Sample in an AppSession that has a status other than 'running'.
        :returns: a newly created Sample instance
        '''
        if (not readLengths) or (not isinstance(readLengths,list)):
            raise Exception("The 'readLengths' parameter has to be a list")
        if (not self.appSessionId) and (appSessionId==None):
            raise Exception("This BaseSpaceAPI instance has no appSessionId set and no alternative id was supplied for method createAppResult")
        resourcePath = '/projects/{ProjectId}/samples'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'
        resourcePath = resourcePath.replace('{ProjectId}', Id)
        queryParams = {}
        headerParams = {}
        postData = {}
        
        if appSessionId:
            queryParams['appsessionid'] = appSessionId
        if appSessionId==None:
            queryParams['appsessionid'] = self.appSessionId      # default case, we use the current appsession
        
        # case, an appSession is provided, we need to check if the app is running
        if queryParams.has_key('appsessionid'):
            session = self.getAppSession(Id=queryParams['appsessionid'])
            if not session.canWorkOn():
                raise Exception('AppSession status must be "running," to create a Sample. Current status is ' + session.Status)
            
        postData['Name'] = name
        postData['ExperimentName'] = experimentName
        postData['SampleNumber'] = sampleNumber
        postData['SampleId'] = sampleTitle
        postData['NumReadsRaw'] = countRaw
        postData['NumReadsPF'] = countPF
        postData['Read1'] = readLengths[0]
        postData['IsPairedEnd'] = False
        if len(readLengths) > 1:
            postData['Read2']  = readLengths[1]
            postData['IsPairedEnd'] = True
        if reference:
            postData['HrefGenome']  = self.version + '/genomes/' + reference

        return self.__singleRequest__(SampleResponse.SampleResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData)

    def sampleFileUpload(self, Id, localPath, fileName, directory, contentType):
        '''
        Uploads a file associated with a Sample to BaseSpace and returns the corresponding file object.
        Small files are uploaded with a single-part upload method, while larger files (> 25 MB) are uploaded
        with multipart upload.

        :param Id: Sample id.
        :param localPath: The local path to the file to be uploaded, including file name.
        :param fileName: The desired filename in the Sample folder on the BaseSpace server.
        :param directory: The directory the file should be placed in on the BaseSpace server.
        :param contentType: The content-type of the file, eg. 'text/plain' for text files, 'application/octet-stream' for binary files
        :returns: a newly created File instance
        '''
        multipart_min_file_size = 25000000 # bytes
        if os.path.getsize(localPath) > multipart_min_file_size:
            return self.multipartFileUpload('samples',Id, localPath, fileName, directory, contentType)
        else:
            return self.__singlepartFileUpload__('samples',Id, localPath, fileName, directory, contentType)

    def __singlepartFileUpload__(self, resourceType, resourceId, localPath, fileName, directory, contentType):
        '''
        Uploads a file associated with an Endpoint to BaseSpace and returns the corresponding file object.
        Intended for small files -- reads whole file into memory prior to upload.
        
        :param resourceType: resource type for the property
        :param resourceId: identifier for the resource
        :param localPath: The local path to the file to be uploaded, including file name.
        :param fileName: The desired filename in the Endpoint folder on the BaseSpace server.
        :param directory: The directory the file should be placed in on the BaseSpace server.
        :param contentType: The content-type of the file.
        :returns: a newly created File instance       
        '''
        if resourceType not in PROPERTY_RESOURCE_TYPES:
            raise IllegalParameterException(resourceType, PROPERTY_RESOURCE_TYPES)
        method                       = 'POST'
        resourcePath                 = '/{Resource}/{Id}/files'
        resourcePath                 = resourcePath.replace('{Id}', resourceId)
        resourcePath                 = resourcePath.replace('{Resource}', resourceType)
        queryParams                  = {}
        queryParams['name']          = fileName
        queryParams['directory']     = directory 
        headerParams                 = {}
        headerParams['Content-Type'] = contentType
        postData                     = open(localPath).read()
        return self.__singleRequest__(FileResponse.FileResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData)

    def __initiateMultipartFileUpload__(self, resourceType, resourceId, fileName, directory, contentType):
        '''
        Initiates multipart upload of a file to an AppResult in BaseSpace (does not actually upload file).  
        
        :param resourceType: resource type for the property
        :param resourceId: identifier for the resource
        :param fileName: The desired filename in the AppResult folder on the BaseSpace server.
        :param directory: The directory the file should be placed in on the BaseSpace server.
        :param contentType: The content-type of the file, eg. 'text/plain' for text files, 'application/octet-stream' for binary files
        :returns: A newly created File instance      
        '''
        if resourceType not in PROPERTY_RESOURCE_TYPES:
            raise IllegalParameterException(resourceType, PROPERTY_RESOURCE_TYPES)
        method                       = 'POST'
        resourcePath                 = '/{Resource}/{Id}/files'
        resourcePath                 = resourcePath.replace('{Id}', resourceId)
        resourcePath                 = resourcePath.replace('{Resource}', resourceType)
        queryParams                  = {}
        queryParams['name']          = fileName
        queryParams['directory']     = directory 
        headerParams                 = {}
        headerParams['Content-Type'] = contentType
                
        queryParams['multipart']     = 'true'
        postData                     = None
        # Set force post as this need to use POST though no data is being streamed
        return self.__singleRequest__(FileResponse.FileResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData, forcePost=1)

    def __uploadMultipartUnit__(self, Id, partNumber, md5, data):
        '''
        Uploads file part for multipart upload
        
        :param Id: file id 
        :param partNumber: the file part to be uploaded
        :param md5: md5 sum of datastream
        :param data: the name of the file containing only data to be uploaded
        :returns: A dictionary of the server response, with a 'Response' key that contains a dict, which contains an 'ETag' key and value on success. On failure, this method returns None 
        '''
        method                       = 'PUT'
        resourcePath                 = '/files/{Id}/parts/{partNumber}'
        resourcePath                 = resourcePath.replace('{Id}', Id)
        resourcePath                 = resourcePath.replace('{partNumber}', str(partNumber))
        queryParams                  = {}
        headerParams                 = {'Content-MD5':md5.strip()}
        return self.apiClient.callAPI(resourcePath, method, queryParams, data, headerParams=headerParams, forcePost=0)        

    def __finalizeMultipartFileUpload__(self, Id):
        '''
        Marks a multipart upload file as complete  
        
        :param Id: the File Id
        :returns: a File instance with UploadStatus attribute updated to 'complete'
        '''
        resourcePath                 = '/files/{Id}'
        method                       = 'POST'
        resourcePath                 = resourcePath.replace('{Id}', Id)
        headerParams                 = {}
        queryParams                  = {'uploadstatus':'complete'}
        postData                     = None        
        # Set force post as this need to use POST though no data is being streamed
        return self.__singleRequest__(FileResponse.FileResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData, forcePost=1)

    def multipartFileUpload(self, resourceType, resourceId, localPath, fileName, directory, contentType, tempDir=None, processCount=10, partSize=25):
        '''
        Method for multi-threaded file-upload for parallel transfer of very large files (currently only runs on unix systems)
        
        :param resourceType: resource type for the property
        :param resourceId: identifier for the resource
        :param localPath: The local path of the file to upload, including file name; local path will not be stored in BaseSpace (use directory argument for this)
        :param fileName: The desired filename on the server
        :param directory: The desired directory name on the server (empty string will place it in the root directory)
        :param contentType: The content type of the file
        :param tempdir: (optional) Temp directory to use for temporary file chunks to upload
        :param processCount: (optional) The number of processes to be used, default 10
        :param partSize: (optional) The size in MB of individual upload parts (must be >5 Mb and <=25 Mb), default 25
        :returns: a File instance, which has been updated after the upload has completed.
        '''
        if resourceType not in PROPERTY_RESOURCE_TYPES:
            raise IllegalParameterException(resourceType, PROPERTY_RESOURCE_TYPES)
        # First create file object in BaseSpace, then create multipart upload object and start upload
        if partSize <= 5 or partSize > 25:
            raise UploadPartSizeException("Multipart upload partSize must be >5 MB and <=25 MB")
        if tempDir is None:
            tempDir = mkdtemp()
        bsFile = self.__initiateMultipartFileUpload__(resourceType, resourceId, fileName, directory, contentType)
        myMpu = mpu(self, localPath, bsFile, processCount, partSize, temp_dir=tempDir)                
        return myMpu.upload()                

    def multipartFileUploadSample(self, Id, localPath, fileName, directory, contentType, tempDir=None, processCount=10, partSize=25):
        '''
        Method for multi-threaded file-upload for parallel transfer of very large files (currently only runs on unix systems)

        :param Id: The Sample ID number
        :param localPath: The local path of the file to upload, including file name; local path will not be stored in BaseSpace (use directory argument for this)
        :param fileName: The desired filename on the server
        :param directory: The desired directory name on the server (empty string will place it in the root directory)
        :param contentType: The content type of the file
        :param tempdir: (optional) Temp directory to use for temporary file chunks to upload
        :param processCount: (optional) The number of processes to be used, default 10
        :param partSize: (optional) The size in MB of individual upload parts (must be >5 Mb and <=25 Mb), default 25
        :returns: a File instance, which has been updated after the upload has completed.
        '''
        # First create file object in BaseSpace, then create multipart upload object and start upload
        if partSize <= 5 or partSize > 25:
            raise UploadPartSizeException("Multipart upload partSize must be >5 MB and <=25 MB")
        if tempDir is None:
            tempDir = mkdtemp()
        bsFile = self.__initiateMultipartFileUploadSample__(Id, fileName, directory, contentType)
        myMpu = mpu(self, localPath, bsFile, processCount, partSize, temp_dir=tempDir)
        return myMpu.upload()

    def fileDownload(self, Id, localDir, byteRange=None, createBsDir=False):
        '''
        Downloads a BaseSpace file to a local directory, and names the file with the BaseSpace file name.
        If the File has a directory in BaseSpace, it will be re-created locally in the provided localDir 
        (to disable this, set createBsPath=False).
        
        If the file is large, multi-part download will be used. 
        
        Byte-range requests are supported for only small byte ranges (single-part downloads).
        Byte-range requests are restricted to a single request of 'start' and 'end' bytes, without support for
        negative or empty values for 'start' or 'end'.
        
        :param Id: The file id
        :param localDir: The local directory to place the file in    
        :param byteRange: (optional) The byte range of the file to retrieve, provide a 2-element list with start and end byte values
        :param createBsDir: (optional) create BaseSpace File's directory inside localDir (default: False)
        :raises ByteRangeException: if the provided byte range is invalid
        :returns: a File instance                
        '''
        max_retries = 5
        multipart_min_file_size = 5000000 # bytes
        if byteRange:
            try:
                rangeSize = byteRange[1] - byteRange[0] + 1
            except IndexError:
                raise ByteRangeException("Byte range must include both start and end byte values")
            if rangeSize <= 0:
                raise ByteRangeException("Byte range must have smaller byte number first")
            if rangeSize > multipart_min_file_size:
                raise ByteRangeException("Byte range %d larger than maximum allowed size %d" % (rangeSize, multipart_min_file_size))
                
        bsFile = self.getFileById(Id)
        if (bsFile.Size < multipart_min_file_size) or (byteRange and (rangeSize < multipart_min_file_size)):
            # append File's directory to local dir, and create this path if it doesn't exist
            localDest = localDir
            if createBsDir:
                localDest = os.path.join(localDir, os.path.dirname(bsFile.Path))
                if not os.path.exists(localDest):
                    os.makedirs(localDest)            
            attempt = 0
            while attempt < max_retries:
                try:
                    self.__downloadFile__(Id, localDest, bsFile.Name, byteRange, standaloneRangeFile=True)
                    break
                except Exception as e:
                    logging.warn("download failed (%s), retry attempt: %s" % (str(e), attempt+1))
                    attempt += 1
            if attempt == max_retries:
                raise ServerResponseException("Max retries exceeded")
            return bsFile
        else:                        
            return self.multipartFileDownload(Id, localDir, createBsDir=createBsDir)

    def __downloadFile__(self, Id, localDir, name, byteRange=None, standaloneRangeFile=False, lock=None): #@ReservedAssignment
        '''
        Downloads a BaseSpace file to a local directory. 
        Supports byte-range requests; by default will seek() into local file for multipart downloads, 
        with option to save only range data in standalone file (no seek()).
        
        This method is for downloading relatively small files, eg. < 5 MB. 
        For larger files, use multipart download (which uses this method for file parts).                
        
        :param Id: The file id
        :param localDir: The local directory to place the file in
        :param name: The name of the local file
        :param byteRange: (Optional) The byte range of the file to retrieve, provide a 2-element list with start and end byte values
        :param standaloneRangeFile: (Optional) if True store only byte-range data in standalone file
        :param lock: (Optional) Multiprocessing lock to prevent multiple processes from writing to same output file concurrently - only needed when using multipart download
        :raises Exception: if REST API call to BaseSpace server fails
        :raises DownloadFailedException: if downloaded file size doesn't match the size in BaseSpace
        :returns: None
        '''
        if byteRange is None:
            byteRange = []
        resourcePath = '/files/{Id}/content'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryParams = {}
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams['redirect'] = 'meta' # we need to add this parameter to get the Amazon link directly 
        
        response = self.apiClient.callAPI(resourcePath, method, queryParams, None, headerParams)
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise Exception('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])
        
        # get the Amazon URL, then do the download; for range requests include
        # size to ensure reading until end of data stream. Create local file if
        # it doesn't exist (don't truncate in case other processes from 
        # multipart download also do this)
        req = urllib2.Request(response['Response']['HrefContent'])
        filename = os.path.join(localDir, name)
        if not os.path.exists(filename):
            open(filename, 'a').close()
        iter_size = 16*1024 # python default
        if len(byteRange):
            req.add_header('Range', 'bytes=%s-%s' % (byteRange[0], byteRange[1]))
        flo = urllib2.urlopen(req, timeout=self.getTimeout()) # timeout prevents blocking                
        totRead = 0
        with open(filename, 'r+b', 0) as fp:
            if len(byteRange) and standaloneRangeFile == False:
                fp.seek(byteRange[0])
            cur = flo.read(iter_size)
            while cur:
                if lock is not None:
                    with lock:
                        fp.write(cur)
                else:
                    fp.write(cur)
                totRead += len(cur)
                cur = flo.read(iter_size)
        # check that actual downloaded byte size is correct
        if len(byteRange):
            expSize = byteRange[1] - byteRange[0] + 1
            if totRead != expSize:
                raise DownloadFailedException("Ranged download size is not as expected: %d vs %d" % (totRead, expSize))
        else:
            bsFile = self.getFileById(Id)
            if totRead != bsFile.Size:
                raise DownloadFailedException("Downloaded file size doesn't match file size in BaseSpace: %d vs %d" % (totRead, bsFile.Size))

    def multipartFileDownload(self, Id, localDir, processCount=10, partSize=25, createBsDir=False, tempDir=""):
        '''
        Method for multi-threaded file-download for parallel transfer of very large files (currently only runs on unix systems)
        
        :param Id: The ID of the File to download 
        :param localDir: The local path in which to store the downloaded file
        :param processCount: (optional) The number of processes to be used, default 10
        :param partSize: (optional) The size in MB of individual file parts to download, default 25
        :param createBsDir: (optional) create BaseSpace File's directory in local_dir, default False
        :param tempDir: (optional) Set temp directory to use debug mode, which stores downloaded file chunks in individual files, then completes by 'cat'ing chunks into large file
        :returns: a File instance 
        '''
        myMpd = mpd(self, Id, localDir, processCount, partSize, createBsDir, tempDir)
        return myMpd.download()

    def fileUrl(self, Id):
        '''
        ** Deprecated in favor of fileS3metadata() **
        
        Returns URL of file (on S3)
        
        :param Id: The file id
        :raises Exception: if REST API call to BaseSpace server fails
        :returns: a URL
        '''
        resourcePath = '/files/{Id}/content'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryParams = {}
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams['redirect'] = 'meta' # we need to add this parameter to get the Amazon link directly 
        
        response = self.apiClient.callAPI(resourcePath, method, queryParams, None, headerParams)
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise Exception('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])                
        return response['Response']['HrefContent']

    def fileS3metadata(self, Id):
        '''
        Returns the S3 url and etag (md5 for small files uploaded as a single part) for a BaseSpace file
                
        :param Id: The file id
        :raises Exception: if REST API call to BaseSpace server fails
        :returns: Dict with s3 url ('url' key) and etag ('etag' key)
        '''
        ret = {}
        resourcePath = '/files/{Id}/content'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryParams = {}
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams['redirect'] = 'meta' # we need to add this parameter to get the Amazon link directly 
        
        response = self.apiClient.callAPI(resourcePath, method, queryParams,None, headerParams)
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise Exception('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])
        
        # record S3 URL
        ret['url'] = response['Response']['HrefContent']
        
        # TODO should use HEAD call here, instead do small GET range request
        # GET S3 url and record etag         
        req = urllib2.Request(response['Response']['HrefContent'])
        req.add_header('Range', 'bytes=%s-%s' % (0, 1))
        flo = urllib2.urlopen(req, timeout=self.getTimeout()) # timeout prevents blocking  
        try:
            etag = flo.headers['etag']
        except KeyError:
            etag = ''
        # strip quotes from etag
        if etag.startswith('"') and etag.endswith('"'):
            etag = etag[1:-1]
        ret['etag'] = etag
        return ret
    
    def _validateQueryParameters(self, queryPars):
        '''
        Initializes and validates Query Parameter arguments
        
        :param queryPars: a QueryParameter object        
        :return: dictionary of query parameters
        '''
        if queryPars is None:
            queryPars = qp()
        try:
            queryPars.validate()
        except AttributeError:
            raise QueryParameterException("Query parameter argument must be a QueryParameter object")
        return queryPars.getParameterDict()

    def __dictionaryToProperties__(self, rawProperties, namespace):
        '''
        Turns a dictionary of properties into the right format to upload to BaseSpace

        :param rawProperties: a key/value mapping of properties
        :param namespace: a string to be used as a prefix to all property names

        This only supports unnested properties at the moment, so therefore no lists or maps inside properties
        The BaseSpace backend does support these, but inferring their structure is complicated
        '''
        LEGAL_KEY_TYPES = [str, int, float, bool]
        propList = []
        for key, value in rawProperties.iteritems():
            if type(value) not in LEGAL_KEY_TYPES:
                raise IllegalParameterException(type(value), LEGAL_KEY_TYPES)
            propName = "%s.%s" % (namespace, key)
            propType = "String"
            propDescription = ""
            # every property in BaseSpace is a string
            propValue = str(value)
            thisProp = {
                "Type" : propType,
                "Name" : propName,
                "Description" : propDescription,
                "Content" : propValue
            }
            propList.append(thisProp)
        return {
            "Properties" : propList
        }

    def setResourceProperties(self, resourceType, resourceId, rawProperties, namespace="apiset"):
        '''
        Pushes a set of properties into a BaseSpace resource:

        https://developer.basespace.illumina.com/docs/content/documentation/rest-api/api-reference#Properties

        :param resourceType: resource type for the property
        :param resourceId: identifier for the resource
        :param rawProperties: a key/value dictionary (no nesting!) of properties to set
        :param namespace: the prefix to be used for property names
        '''
        if resourceType not in PROPERTY_RESOURCE_TYPES:
            raise IllegalParameterException(resourceType, PROPERTY_RESOURCE_TYPES)
        resourcePath = '/%s/%s/properties' % (resourceType, resourceId)
        method = 'POST'
        postData = self.__dictionaryToProperties__(rawProperties, namespace)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse,
                                      resourcePath, method, queryParams, headerParams, postData=postData)


    def getResourceProperties(self, resourceType, resourceId):
        '''
        Gets the properties for an arbitrary resource:

        https://developer.basespace.illumina.com/docs/content/documentation/rest-api/api-reference#Properties   
        
        :param resourceType: resource type for the property

        Because of this generic treatment of properties (which is fairly new in BaseSpace)
        we could probably factor away these SDK methods:
            getAppSessionPropertiesById()
            getAppResultPropertiesById()
            getProjectPropertiesById()
            getRunPropertiesById()
            getSamplePropertiesById()

        but not this one, because files are not generic yet:
            getFilePropertiesById()

        '''
        if resourceType not in PROPERTY_RESOURCE_TYPES:
            raise UnknownParameterException(resourceType, PROPERTY_RESOURCE_TYPES)
        resourcePath = '/%s/%s/properties' % (resourceType, resourceId)
        method = 'GET'
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(PropertiesResponse.PropertiesResponse,
                                      resourcePath, method, queryParams, headerParams)
