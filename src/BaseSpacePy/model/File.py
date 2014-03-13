
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
        :returns: True on success
        
        '''
        err = 'The File object has not been initialized yet'
        try:
            if not self.Id:
                raise ModelNotInitializedException(err)
        except AttributeError:
            raise ModelNotInitializedException(err)
        return True        
        
    def isValidFileOption(self, filetype):
        '''
        ** Deprecated - HrefCoverage should be present for all BAM files in BaseSpace.
                        However, the attribute may be missing when there has been an error
                        when BaseSpace internally generates coverage data from the BAM file. 
                        This is the same situation for HrefVariants on all VCF files. **
                                
        Is called to test if the File instance matches the filetype parameter         
              
        :param filetype: The filetype for coverage or variant requests (eg., 'bam', 'vcf')                
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

    def getIntervalCoverage(self, api, Chrom, StartPos, EndPos):
        '''
        Returns mean coverage levels over a sequence interval.
        Note that HrefCoverage must be available for the provided BAM file.
        
        :param api: An instance of BaseSpaceAPI
        :param Chrom: Chromosome name as a string - for example 'chr2'
        :param StartPos: get coverage starting at this position
        :param EndPos: get coverage up to and including this position; the returned EndPos may be larger than requested due to rounding up to nearest window end coordinate        
        :returns: A Coverage object
        '''
        self.isInit()
        return api.getIntervalCoverage(self.Id, Chrom, StartPos, EndPos)

    def getCoverageMeta(self, api, Chrom):
        '''
        Returns metadata about an alignment, including max coverage and cov granularity.        
        Note that HrefCoverage must be available for the provided BAM file.
        
        :param api: An instance of BaseSpaceAPI.
        :param Chrom: Chromosome name
        :returns: a CoverageMetaData object
        '''
        self.isInit()        
        return api.getCoverageMetaInfo(self.Id, Chrom)
        
    def filterVariant(self, api, Chrom, StartPos, EndPos, Format='json', queryPars=None):
        '''
        List the variants in a set of variants. Note the maximum returned records is 1000.
        
        :param api: An instance of BaseSpaceAPI
        :param Chrom: Chromosome name
        :param StartPos: The start position of region of interest as a string
        :param EndPos: The end position of region of interest as a string
        :param Format: (optional) Format for results, possible values: 'vcf' (not implemented yet), 'json'(default, which actually returns an object)
        :param queryPars: An (optional) object of type QueryParameters for custom sorting and filtering
        :returns: a list of Variant objects, when Format is json; a string, when Format is vcf
        '''
        self.isInit()
        return api.filterVariantSet(self.Id, Chrom, StartPos, EndPos, Format, queryPars)

    def getVariantMeta(self, api, Format='json'):
        '''        
        Returns the header information of a VCF file.
        
        :param api: An instance of BaseSpaceAPI
        :param Format: (optional) The return-value format, set to 'vcf' to VCF format (string) or 'json' (default, which acutally returns on object)
        :returns: A VariantHeader object
        '''
        self.isInit()
        return api.getVariantMetadata(self.Id, Format)
