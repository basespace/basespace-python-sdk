from BaseSpacePy.api.BaseSpaceAPI import *
import urllib
import pycurl
import httplib
import cStringIO
import json

# Uris for obtaining a access token, user verification code, and app trigger information
tokenURL                   = 'oauthv2/token'
deviceURL                  = "oauthv2/deviceauthorization"
webAuthorize               = 'oauth/authorize'

class BaseSpaceAuth():
    '''
    A class for handling authentication requests to the BaseSpace REST server
    For more details on the authentication procedure please visit:
    https://developer.basespace.illumina.com/docs/content/documentation/authentication/obtaining-access-tokens
    '''
    
    # TO-DO, this should be a singleton class
    def __init__(self,clientKey,clientSecret,baseSpaceUrl,version):
        self.key    = clientKey
        self.secret = clientSecret
        self.baseUrl= baseSpaceUrl.replace('api.','')
        self.url    = baseSpaceUrl + version
#        self.api    = APIClient('',self.url)

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
    
    def getVerificationCode(self,scope,device=1,redirect=''):
        '''
        Returns the BaseSpace dictionary containing the verification code and verification url for the user to approve
        access to a specific data scope.  
        
        Corresponding curl call:
        curlCall = 'curl -d "response_type=device_code" -d "client_id=' + client_key + '" -d "scope=' + scope + '" ' + deviceURL
        
        For details see:
        https://developer.basespace.illumina.com/docs/content/documentation/authentication/obtaining-access-tokens
            
        :param scope: The scope that access is requested for
        '''
        data = [('client_id',self.key),('scope', scope),('response_type','device_code')]
        return self.__makeCurlRequest__(data,self.url + deviceURL)
    
    def getWebVerificationCode(self,scope,redirectURL,state=''):
        '''
        Generates the URL the user should be redirected to for web-based authentication
         
        :param scope: The scope that access is requested for
        :param redirectURL: The redirect URL
        :state: An optional state paramter that will passed through to redirect response
        '''
        data = {'client_id':self.key,'redirect_uri':redirectURL,'scope':scope,'response_type':'code',"state":state}
        return self.baseUrl + webAuthorize + '?' + urllib.urlencode(data)
    
    def getAccessToken(self,deviceCode):
        '''
        Returns a user specific access token.    
        :param deviceCode: The device code returned by the verification code method
        '''
        data = [('client_id',self.key),('client_secret', self.secret),('code',deviceCode),('grant_type','device'),('redirect_uri','google.com')]
        dict = self.__makeCurlRequest__(data,self.url + tokenURL)
        return dict['access_token']
    
    def getBaseSpaceApi(self,deviceCode):
        '''
        Returns a BaseSpaceAPI object related to a access-token obtained with the supplied deviceCode 
        :param deviceCode: The device code returned by the verification code method
        '''
        token  = self.getAccessToken(deviceCode)
        return BaseSpaceAPI(AccessToken=token,apiServer= self.url)
    
    def getAppTrigger(self,ApplicationActionId):
        '''
        Returns an app launch object containing user and datatype the app was triggered by/on 
        :param ApplicationActionId: The applicationActionId that triggered the app
        '''
        # This is a dummy BaseSpaceAPI initialized w/o access_token, 
        # should not be used for any further calls
        resourcePath = self.url + 'applicationactions/{ApplicationActionId}'
        resourcePath = resourcePath.replace('{ApplicationActionId}', ApplicationActionId)
        print resourcePath
        api = BaseSpaceAPI(AccessToken='',apiServer = self.url)
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL,resourcePath)
        c.setopt(pycurl.USERPWD,self.key + ":" + self.secret)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        obj = json.loads(response.getvalue())
        return api.__getTriggerObject__(obj)
                                    
        