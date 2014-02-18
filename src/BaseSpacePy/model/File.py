
from BaseSpacePy.api.BaseSpaceException import ModelNotInitializedException, WrongFiletypeException

class File(object):
    '''
    Represents a BaseSpace file object
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
        return self.Name 
             
    def __repr__(self):
        return str(self)
    
    def isInit(self):
        '''        
        Tests if the File instance has been initialized.
        
        :raises ModelNotInitializedException: if the Id variable is not set
        :return True on success
        '''
        err = 'The File object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        
        
    def isValidFileOption(self,filetype):
        '''
        Is called to test if the File instance is matches the filtype parameter 
              
        :param filetype: The filetype for coverage or variant requests
        '''
        self.isInit()
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
        self.isInit()
        return api.fileDownload(self.Id, localDir, byteRange=byteRange, createBsDir=createBsDir)        

    def getFileUrl(self, api):
        '''
        ** Deprecated in favor of getFileS3metadata() **
        
        Return the S3 url of the file.
        
        :param api: A BaseSpaceAPI with read access on the scope including the file object.
        '''
        self.isInit()
        return api.fileUrl(self.Id)
    
    def getFileS3metadata(self, api):
        '''
        Returns the S3 url and etag (md5 for small files uploaded as a single part) for a BaseSpace file
                
        :param api: A BaseSpaceAPI with read access on the scope including the file object.
        :returns: Dict with s3 url ('url' key) and etag ('etag' key)
        '''
        self.isInit()
        return api.fileS3metadata(self.Id)

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
