#!/usr/bin/env python
import sys
sys.path.append('/home/mkallberg/workspace/BaseSpacePy_v0.1/src/')
from pprint import pprint
import urllib2
import shutil
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import * #@UnusedWildImport
from BaseSpacePy.model.MultipartUpload import MultipartUpload as mpu #@UnresolvedImport
from BaseSpacePy.model.QueryParameters import QueryParameters as qp #@UnresolvedImport
from BaseSpacePy.model import * #@UnusedWildImport

class BaseSpaceAPI(object):
    '''
    The main API class used for all communication with with the REST server
    '''

    def __init__(self, apiServer,AccessToken=''):
        '''
        
        :param AccessToken:
        :param apiServer:
        '''
        apiClient      = None
        if apiClient      = APIClient(AccessToken=AccessToken,apiServer=apiServer)
        self.apiClient = apiClient
        self.apiServer = apiServer 

    def __updateAccessToken__(self,AccessToken):
        self.apiClient.apiKey = AccessToken

    def setAccessToken(self):
        pass

    def __singleRequest__(self,myModel,resourcePath, method, queryParams, headerParams,postData=None,verbose=0,forcePost=0):

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

    def __listRequest__(self,myModel,resourcePath, method, queryParams, headerParams,verbose=0):
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

    def __str__(self):
        return "BaseSpaceAPI instance - using token=" + self.getAccessToken()
    
    def __repr__(self):
        return str(self)  

    def getAccessToken(self):
        '''
        Returns the access-token that was used to initialize the BaseSpaceAPI object.
        '''
        return self.apiClient.apiKey
    
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
        resourcePath = '/analyses/{Id}/files'
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
    
    def getAnalysisByProject(self, Id, queryPars=qp()):
        '''
        Returns a list of Analysis object associated with the project with Id
        
        :param Id: The project id
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        '''
        # Parse inputs
        resourcePath = '/projects/{Id}/analyses'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'
        queryPars.validate()
        queryParams = queryPars.getParameterDict()
        headerParams = {}
        resourcePath = resourcePath.replace('{Id}',Id)
        return self.__listRequest__(Analysis.Analysis,resourcePath, method, queryParams, headerParams)

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
        
    def markAnalysisState(self,Id,Status,Summary):
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
        statusAllowed = ['working', 'completed', 'blocked', 'aborted']
        if not Status.lower() in statusAllowed:
            raise Exception("Analysis state must be in " + str(statusAllowed))
        postData['status'] = Status.lower()
        postData['statussummary'] = Summary
        return self.__singleRequest__(AnalysisResponse.AnalysisResponse,resourcePath, method,\
                                      queryParams, headerParams,postData=postData,verbose=0)
        
    def __getTriggerObject__(self,obj):
        '''
        Warning this method is not for general use and should only be called 
        from the BaseSpaceAuth module method.
        :param obj: The appTrigger json 
        '''
        
        response = obj
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise Exception('BaseSpace error: ' + str(response['ResponseStatus']['ErrorCode']) + ": " + response['ResponseStatus']['Message'])
         
        response  = self.apiClient.deserialize(obj, AppLaunchResponse.AppLaunchResponse) #@UndefinedVariable
        
        return response.Response
        