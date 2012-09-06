#!/usr/bin/env python
#import sys
#sys.path.append('/home/mkallberg/workspace/BaseSpacePy_v0.1/src/')
from pprint import pprint
import urllib2
import shutil
import urllib
import pycurl
import httplib
import cStringIO
import json

from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import * #@UnusedWildImport
from BaseSpacePy.model.MultipartUpload import MultipartUpload as mpu #@UnresolvedImport
from BaseSpacePy.model.QueryParameters import QueryParameters as qp #@UnresolvedImport
from BaseSpacePy.model import * #@UnusedWildImport

# Uris for obtaining a access token, user verification code, and app trigger information
tokenURL                   = 'oauthv2/token'
deviceURL                  = "oauthv2/deviceauthorization"
webAuthorize               = 'oauth/authorize'


class BaseSpaceAPI(object):
    '''
    The main API class used for all communication with with the REST server
    '''

    def __init__(self, clientKey, clientSecret, apiServer, version, appSessionId, AccessToken=''):
        if not apiServer[-1]=='/': apiServer = apiServer + '/'
        if not version[-1]=='/': version = version + '/'
        
        self.appSessionId   = appSessionId
        self.key            = clientKey
        self.secret         = clientSecret
        self.apiServer      = apiServer + version
        self.weburl         = apiServer.replace('api.','')
        self.setAccessToken(AccessToken)        # logic for setting the access-token 

    def __updateAccessToken__(self,AccessToken):
        self.apiClient.apiKey = AccessToken

    def setAccessToken(self,token):
        self.apiClient      = None
        if token: 
            apiClient = APIClient(AccessToken=token,apiServer=self.apiServer)
            self.apiClient = apiClient

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

    def getAppSession(self,Id=''):
        '''
        Returns an AppSession instance containing user and data-type the app was triggered by/on 
        :param Id: (Optional) The AppSessionId, id not supplied the AppSessionId used for instantiating
        the BaseSpaceAPI instance.
        '''
        resourcePath = self.apiServer + 'appsessions/{AppSessionId}'
        if not Id:
            resourcePath = resourcePath.replace('{AppSessionId}', self.appSessionId)
        else:
            resourcePath = resourcePath.replace('{AppSessionId}', Id)
#        print resourcePath
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL,resourcePath)
        c.setopt(pycurl.USERPWD,self.key + ":" + self.secret)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        obj = json.loads(response.getvalue())
#        pprint(obj)
        return self.__getTriggerObject__(obj) 

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
        return self.__makeCurlRequest__(data,self.apiServer + deviceURL)

    def getWebVerificationCode(self,scope,redirectURL,state=''):
        '''
        Generates the URL the user should be redirected to for web-based authentication
         
        :param scope: The scope that access is requested for
        :param redirectURL: The redirect URL
        :state: An optional state paramter that will passed through to redirect response
        '''
        data = {'client_id':self.key,'redirect_uri':redirectURL,'scope':scope,'response_type':'code',"state":state}
        return self.weburl + webAuthorize + '?' + urllib.urlencode(data)

    def obtainAccessToken(self,deviceCode):
        '''
        Returns a user specific access token.    
        :param deviceCode: The device code returned by the verification code method
        '''
        data = [('client_id',self.key),('client_secret', self.secret),('code',deviceCode),('grant_type','device'),('redirect_uri','google.com')]
        dict = self.__makeCurlRequest__(data,self.apiServer + tokenURL)
        return dict['access_token']

    def updatePrivileges(self,code):
        token = self.obtainAccessToken(code)
        self.setAccessToken(token)
            
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

    def getUserById(self, Id, ):
        '''
        Returns the User object corresponding to Id
        
        :param Id: The Id of the user
        '''
        # Parse inputs
        resourcePath = '/users/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(UserResponse.UserResponse,resourcePath, method, queryParams, headerParams)
           
    def getAnalysisById(self, Id, ):
        '''
        Returns an Analysis object corresponding to Id
        
        :param Id: The Id of the Analysis
        '''
        # Parse inputs
        resourcePath = '/analyses/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(AnalysisResponse.AnalysisResponse,resourcePath, method, queryParams, headerParams)

    def getAnalysisFiles(self, Id, queryPars=qp()):
        '''
        Returns a list of File object for the Analysis with id  = Id
        
        :param Id: The id of the analysis.
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering 
        '''
        # Parse inputs
        resourcePath = '/appresults/{Id}/files'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(File.File,resourcePath, method, queryParams, headerParams,verbose=0)

    def getProjectById(self, Id, ):
        '''
        Request a project object by Id
        
        :param Id: The Id of the project
        '''
        # Parse inputs
        resourcePath = '/projects/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(ProjectResponse.ProjectResponse,resourcePath, method, queryParams, headerParams)
           
    def getProjectByUser(self, Id, queryPars=qp()):
        '''
        Returns a list available projects for a User with the specified Id
        
        :param Id: The id of the user
        :param qp: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/users/{Id}/projects'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        if Id != None: resourcePath = resourcePath.replace('{Id}', Id)
        return self.__listRequest__(Project.Project,resourcePath, method, queryParams, headerParams)
       
    def getAccessibleRunsByUser(self, Id, queryPars=qp()):
        '''
        Returns a list of accessible runs for the User with id=Id
        
        :param Id: An user id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/users/{Id}/runs'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(RunCompact.RunCompact,resourcePath, method, queryParams, headerParams)
    
    def getAppResultsByProject(self, Id, queryPars=qp()):
        '''
        Returns a list of Analysis object associated with the project with Id
        
        :param Id: The project id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/projects/{Id}/appresults'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(AppResult.AppResult,resourcePath, method, queryParams, headerParams,verbose=0)

    def getSamplesByProject(self, Id, queryPars=qp()):
        '''
        Returns a list of samples associated with a project with Id
        
        :param Id: The id of the project
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/projects/{Id}/samples'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(Sample.Sample,resourcePath, method, queryParams, headerParams)

    def getSampleById(self, Id, ):
        '''
        Returns a Sample object
        
        :param Id: The id of the sample
        '''
        # Parse inputs
        resourcePath = '/samples/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(SampleResponse.SampleResponse,resourcePath, method, queryParams, headerParams)

    def getFilesBySample(self, Id, queryPars=qp()):
        '''
        Returns a list of File objects associated with sample with Id
        
        :param Id: A Sample id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/samples/{Id}/files'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(File.File,resourcePath, method, queryParams, headerParams,verbose=0)
    
    def getFileById(self, Id, ):
        '''
        Returns a file object by Id
        
        :param Id: The id of the file
        '''
        # Parse inputs
        resourcePath = '/files/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(FileResponse.FileResponse,resourcePath, method,\
                                      queryParams, headerParams,verbose=0)

    def getGenomeById(self, Id, ):
        '''
        Returns an instance of Genome with the specified Id
        
        :param Id: The genome id
        '''
        # Parse inputs
        resourcePath = '/genomes/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        return self.__singleRequest__(GenomeResponse.GenomeResponse,resourcePath, method, queryParams, headerParams)

    def getAvailableGenomes(self, queryPars=qp()):
        '''
        Returns a list of all available genomes
        
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        
        # Parse inputs
        resourcePath = '/genomes'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        return self.__listRequest__(GenomeV1.GenomeV1,resourcePath, method, queryParams, headerParams,verbose=0)
    
    # TODO, needs more work in parsing meta data, currently only map keys are returned 
    
    def getVariantMetadata(self, Id, Format,):
        '''
        Returns a VariantMetadata object for the variant file
        
        :param Id: The Id of the VCF file
        :param Format: Set to 'vcf' to get the results as lines in VCF format
        '''
        # Parse inputs
        resourcePath = '/variantset/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryParams = {}
        headerParams = {}
        queryParams['Format'] = self.apiClient.toPathValue(Format)
        resourcePath = resourcePath.replace('{Id}', Id)
        return self.__singleRequest__(VariantsHeaderResponse.VariantsHeaderResponse,resourcePath, method,\
                                      queryParams, headerParams,verbose=0)
    
    def filterVariantSet(self,Id, Chrom, StartPos, EndPos, Format, queryPars=qp(pars={'SortBy':'Position'})):
        '''
        List the variants in a set of variants. Maximum returned records is 1000
        
        :param Id: The id of the variant file 
        :param Chrom: The chromosome of interest
        :param StartPos: The start position of the sequence of interest
        :param EndPos: The start position of the sequence of interest
        :param Format: Set to 'vcf' to get the results as lines in VCF format
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/variantset/{Id}/variants/chr{Chrom}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        queryParams['StartPos'] = StartPos
        queryParams['EndPos']   = EndPos
        queryParams['Format']   = Format
        resourcePath = resourcePath.replace('{Chrom}', Chrom)
        resourcePath = resourcePath.replace('{Id}', Id)
        return self.__listRequest__(Variant.Variant,resourcePath, method, queryParams, headerParams,verbose=0)
    
    def getIntervalCoverage(self, Id, Chrom, StartPos=None, EndPos=None, ):
        '''
        Mean coverage levels over a sequence interval
        
        :param Id: Chromosome to query
        :param Chrom: The Id of the resource
        :param StartPos: Get coverage starting at this position. Default is 1
        :param EndPos: Get coverage up to and including this position. Default is StartPos + 1280
        
        :return:CoverageResponse -- an instance of CoverageResponse
        '''
        # Parse inputs
        resourcePath = '/coverage/{Id}/{Chrom}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryParams = {}
        headerParams = {}
        queryParams['StartPos'] = self.apiClient.toPathValue(StartPos)
        queryParams['EndPos'] = self.apiClient.toPathValue(EndPos)
        resourcePath = resourcePath.replace('{Chrom}', Chrom)
        resourcePath = resourcePath.replace('{Id}', Id)
        return self.__singleRequest__(CoverageResponse.CoverageResponse,resourcePath, method,\
                                      queryParams, headerParams,verbose=0)

    def getCoverageMetaInfo(self, Id, Chrom):
        '''
        Returns Metadata about coverage as a CoverageMetadata instance
        
        :param Id: he Id of the Bam file 
        :param Chrom: Chromosome to query
        '''
        # Parse inputs
        resourcePath = '/coverage/{Id}/{Chrom}/meta'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryParams = {}
        headerParams = {}
        resourcePath = resourcePath.replace('{Chrom}', Chrom)
        resourcePath = resourcePath.replace('{Id}', Id)
        
        return self.__singleRequest__(CoverageMetaResponse.CoverageMetaResponse,resourcePath, method,\
                                      queryParams, headerParams,verbose=0)
     
    def createAnalyses(self,Id,name,desc):
        '''
        Create an analysis object
        
        :param Id: The id for the project in which the analysis is to be added
        :param name: The name of the analysis
        :param desc: A describtion of the analysis
        '''
        # Parse inputs
        resourcePath = '/projects/{ProjectId}/analyses'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'
        resourcePath = resourcePath.replace('{ProjectId}', Id)
        queryParams = {}
        headerParams = {}
        postData = {}
        postData['Name'] = name
        postData['Description'] = desc
        return self.__singleRequest__(AnalysisResponse.AnalysisResponse,resourcePath, method, queryParams, headerParams,postData=postData,verbose=0)
            
  
    #TODO
    
    def analysisFileUpload(self, Id, localPath, fileName, directory, contentType, multipart=0):
        '''
        Uploads a file associated with an analysis to BaseSpace and returns the corresponding file object  
        
        :param Id: Analysis id.
        :param localPath: The local path to the file to be uploaded.
        :param fileName: The desired filename in the Analysis folder on the BaseSpace server.
        :param directory: The directory the file should be placed in.
        :param contentType: The content-type of the file.
         
        '''
        resourcePath = '/analyses/{Id}/files'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'
        resourcePath                 = resourcePath.replace('{Id}', Id)
        queryParams                  = {}
        queryParams['name']          = fileName
        queryParams['directory']     = directory 
        headerParams                 = {}
        headerParams['Content-Type'] = contentType
        # three cases, two for multipart, starting 
        if multipart==1:
            queryParams['multipart']          = 'true'
            postData = None
            # Set force post as this need to use POST though no data is being streamed
            return self.__singleRequest__(FileResponse.FileResponse,resourcePath, method,\
                                      queryParams, headerParams,postData=postData,verbose=0,forcePost=1)
        elif multipart==2:
            queryParams          = {'uploadstatus':'complete'}
            postData = None
            # Set force post as this need to use POST though no data is being streamed
            return self.__singleRequest__(FileResponse.FileResponse,resourcePath, method,\
                                      queryParams, headerParams,postData=postData,verbose=0,forcePost=1)
        else:
            postData                     = open(localPath).read()
            return self.__singleRequest__(FileResponse.FileResponse,resourcePath, method,\
                                      queryParams, headerParams,postData=postData,verbose=0)

    def fileDownload(self,Id,localDir,name,range=[]): #@ReservedAssignment
        '''
        Downloads a BaseSpace file to a local directory
        
        :param Id: The file id
        :param localDir: The local directory to place the file in
        :param name: The name of the local file
        :param range: (Optional) The byte range of the file to retrieve (not yet implemented)
        '''
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
        
        # get the Amazon URL 
        fileUrl = response['Response']['HrefContent']
        req = urllib2.urlopen(fileUrl)
        if len(range):
#            print "Case range request" 
            req.headers['Range']='bytes=%s-%s' % (range[0], range[1])
        
        # Do the download
        with open(localDir + name, 'wb') as fp:
            shutil.copyfileobj(req, fp)
        return 1

#    def largeFileDownload(self):
#        '''
#        Not yet implemented
#        '''
#        raise Exception('Not yet implemented')
            
    def __uploadMultipartUnit__(self,Id,partNumber,md5,data):
        '''
        Helper method, do not call
        
        :param Id: file id 
        :param partNumber: the file part to be uploaded
        :param md5: md5 sum of datastream
        :param data: the data-stream to be uploaded
        '''
        resourcePath                 = '/files/{Id}/parts/{partNumber}'
        resourcePath                 = resourcePath.replace('{format}', 'json')
        method                       = 'PUT'
        resourcePath                 = resourcePath.replace('{Id}', Id)
        resourcePath                 = resourcePath.replace('{partNumber}', str(partNumber))
        queryParams                  = {}
        headerParams                 = {'Content-MD5':md5.strip()}
        out = self.apiClient.callAPI(resourcePath, method, queryParams, data, headerParams=headerParams,forcePost=0)
        return out
#        curl -v -H "x-access-token: {access token}" \
#        -H "Content-MD5: 9mvo6qaA+FL1sbsIn1tnTg==" \
#        -T reportarchive.zipaa \
#        -X PUT https://api.cloud-endor.illumina.com/v1pre2/files/7094087/parts/1
    
    def multipartFileUpload(self,Id, localPath, fileName, directory, contentType, tempdir='',cpuCount=2,partSize=25,verbose=0):
        '''
        Method for multi-threaded file-upload for parallel transfer of very large files (currently only runs on unix systems)
        
        
        :param Id: The analysis ID
        :param localPath: The local path of the file to be uploaded
        :param fileName: The desired filename on the server
        :param directory: The server directory to place the file in (empty string will place it in the root directory)
        :param contentType: The content type of the file
        :param tempdir: Temp directory to use, if blank the directory for 'localPath' will be used
        :param cpuCount: The number of CPUs to be used
        :param partSize: The size of individual upload parts (must be between 5 and 25mb)
        :param verbose: Write process output to stdout as upload progresses
        '''
 
        # Create file object on server
        myFile = self.analysisFileUpload(Id, localPath, fileName, directory, contentType,multipart=1)
        
        # prepare multi-par upload objects
        myMpu = mpu(self,Id,localPath,myFile,cpuCount,partSize,tempdir=tempdir,verbose=verbose)
        return myMpu

    def markFileState(self,Id):
        pass
        
    def setAppsessionState(self,Id,Status,Summary):
        '''
        Set the status of an Analysis object
        
        :param Id: The id of the analysis
        :param Status: The status assignment string must
        :param Summary: The summary string
        '''
        # Parse inputs
        resourcePath = '/analyses/{Id}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'
        resourcePath = resourcePath.replace('{Id}', Id)
        queryParams = {}
        headerParams = {}
        postData = {}
        statusAllowed = ['running', 'complete', 'needattention', 'aborted','error']
        if not Status.lower() in statusAllowed:
            raise Exception("Analysis state must be in " + str(statusAllowed))
        postData['status'] = Status.lower()
        postData['statussummary'] = Summary
        return self.__singleRequest__(AppResultResponse.AppResultResponse,resourcePath, method,\
                                      queryParams, headerParams,postData=postData,verbose=0)
        
    def __getTriggerObject__(self,obj):
        '''
        Warning this method is not for general use and should only be called 
        from the getAppSession.
        :param obj: The appTrigger json 
        '''
        response = obj
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise Exception('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])
        tempApi   = APIClient(AccessToken='', apiServer=self.apiServer)
        response  = tempApi.deserialize(obj, AppSessionResponse.AppSessionResponse) #@UndefinedVariable
        res = response.Response
        res = res.__serializeReferences__(self)
        return res
    
    def __serializeObject__(self,d,type):
        tempApi   = APIClient(AccessToken='', apiServer=self.apiServer)
        if type.lower()=='project':
            return tempApi.deserialize(d, Project.Project)
        if type.lower()=='sample':
            return tempApi.deserialize(d, Sample.Sample)        
        return d
        
    
        