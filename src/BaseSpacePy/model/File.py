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

from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException,WrongFiletypeException

class File(object):
    '''
    Represents a BaseSpace file object.
    '''

    def __init__(self):
        self.swaggerTypes = {
            'Name': 'str',
            'HrefCoverage': 'str',
            'HrefParts': 'str',
            'DateCreated': 'datetime',
            'UploadStatus': 'str',
            'Id': 'str',
            'Href': 'str',
            'HrefContent': 'str',
            'HrefVariants': 'str',
            'ContentType': 'str',
            'Path': 'str',
            'Size': 'int',
            'Properties': 'PropertyList',
        }

    def __str__(self):
        s =  self.Name 
        try:
            s += " - status: " + self.UploadStatus
        except:
            e=1
        return s 
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''
        Is called to test if the File instance has been initialized.
        
        Throws:
            ModelNotInitializedException if the instance has not been populated yet.
        '''
        try:self.Id
        except: raise ModelNotInitializedException('The File model has not been initialized yet')
        
    def isValidFileOption(self,filetype):
        '''
        Is called to test if the File instance is matches the filtype parameter 
              
        :param filetype: The filetype for coverage or variant requests
        '''
        if filetype=='bam':
            try: 
                self.HrefCoverage
            except:
                raise WrongFiletypeException(self.Name)
            
        if filetype=='vcf':
            try: 
                self.HrefVariants
            except:
                raise WrongFiletypeException(self.Name)

    def downloadFile(self, api, localDir, byteRange=None, createBsDir=False):
        '''
        Download the file object to the specified localDir or a byte range of the file, by specifying the 
        start and stop byte in the range.
        
        :param api: A BaseSpaceAPI with read access on the scope including the file object.
        :param localDir: The local directory to place the file in.
        :param byteRange: (optional) Specify the start and stop byte of the file chunk that needs retrieved (as a 2-element list).
        :param createBsDir: (optional) create BaseSpace File's directory inside localDir (default: False)                
        '''        
        return api.fileDownload(self.Id, localDir, byteRange=byteRange, createBsDir=createBsDir)        

    def getFileUrl(self,api):
        '''
        Return the S3 url of the file.
        
        :param api: A BaseSpaceAPI with read access on the scope including the file object.
        '''
        return api.fileUrl(self.Id)

    def deleteFile(self,api):
        raise Exception('Not yet implemented')

    def getIntervalCoverage(self,api,Chrom, StartPos, EndPos):
        '''
        Return a coverage object for the specified region and chromosome.
        
        :param api: An instance of BaseSpaceAPI
        :param Chrom: Chromosome as a string - for example 'chr2'
        :param StartPos: The start position of region of interest as a string
        :param EndPos: The end position of region of interest as a string
        '''
        self.isInit()
        self.isValidFileOption('bam')
        Id = self.HrefCoverage.split('/')[-1]
        return api.getIntervalCoverage(Id,Chrom, StartPos, EndPos)
    
    # TODO allow to pass a queryParameters object for custom filtering
    def filterVariant(self,api,Chrom,StartPos, EndPos,q=None):
        '''
        Returns a list of Variant objects available in the specified region
        
        :param api: An instance of BaseSpaceAPI
        :param Chrom: Chromosome as a string - for example 'chr2'
        :param StartPos: The start position of region of interest as a string
        :param EndPos: The end position of region of interest as a string
        :param q: An instance of 
        '''
        self.isInit()
        self.isValidFileOption('vcf')
        Id = self.HrefVariants.split('/')[-1]
        return api.filterVariantSet(Id, Chrom, StartPos, EndPos, 'txt')

    def getCoverageMeta(self,api,Chrom):
        '''
        Return an object of CoverageMetadata for the selected region
        
        :param api: An instance of BaseSpaceAPI.
        :param Chrom: The chromosome of interest.
        '''
        self.isInit()
        self.isValidFileOption('bam')
        Id = self.HrefCoverage.split('/')[-1]
        return api.getCoverageMetaInfo(Id,Chrom)

    def getVariantMeta(self, api):
        '''
        Return the the meta info for a VCF file as a VariantInfo object
        
        :param api: An instance of BaseSpaceAPI
        '''
        self.isInit()
        self.isValidFileOption('vcf')
        Id = self.HrefVariants.split('/')[-1]
        return api.getVariantMetadata(Id,'txt')
    
#    def markAsComplete(self,api):
#        '''
#        Mark a file object created as part of a multipart upload as complete
#        :param api: An instance of BaseSpaceAPI
#        '''
#        api.markFileState(self.Id)
#        self.UploadStatus ='Complete'
        
        
    
        self.Name = None # str

        # If set, provides the relative Uri to fetch the mean coverage statistics for data stored in the file
        self.HrefCoverage = None # str

        # If set, provides the relative Uri to fetch a list of completed file parts for multi-part file uploads in progress
        self.HrefParts = None # str

        # 
        self.DateCreated = None # str

        # 
        self.UploadStatus = None # str

        # 
        self.Id = None # str

        # 
        self.Href = None # str

        # 
        self.HrefContent = None # str

        # If set, provides the relative Uri to fetch the variants stored in the file
        self.HrefVariants = None # str

        # 
        self.ContentType = None # str

        # 
        self.Path = None # str

        # 
        self.Size = None # int

