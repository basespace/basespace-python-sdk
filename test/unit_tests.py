from unittest import TestCase, TestSuite, TestLoader, TextTestRunner, skip
import os
import sys
from tempfile import mkdtemp
import shutil
from urlparse import urlparse, urljoin
import multiprocessing
import hashlib
import webbrowser
import time
import json
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI, deviceURL
from BaseSpacePy.api.BaseAPI import BaseAPI
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import *
from BaseSpacePy.model import *
from BaseSpacePy.model.MultipartFileTransfer import Utils
from BaseSpacePy.model.QueryParameters import QueryParameters as qp



# Dependencies:
# ============
# 1. Create a profile named 'unit_tests' in ~/.basespacepy.cfg that has the credentials for an app on https://portal-hoth.illumina.com;
#    (there should also be a 'DEFALT' profile in the config file)
# 2. Import the following data from Public Dataset 'MiSeq B. cereus demo data' on cloud-hoth.illumina.com:
#    2.a.  Project name 'BaseSpaceDemo' (Id 596596), and
#    2.b.  Run name 'BacillusCereus' (Id 555555)
# 3. Download the following fastq file from BaseSpaceDemo's samples section: 
#    < https://cloud-hoth.illumina.com/sample/855866/files/tree/BC-12_S12_L001_R2_001.fastq.gz?id=9896135 >
#    and place it into the 'data' directory of this repository. It's 56MB in size.
#
# Note that large file upload download tests may take minutes each to complete, and oauth tests will open web browsers.

tconst = { 
           # for download tests
           'file_id_small': '9896072', # 2.2 KB,  public data B. cereus Project, data/intentisties/basecalls/Alignment/DemultiplexSummaryF1L1.9.txt
           'file_id_large': '9896135', # 55.31 MB  public data B. cereus Project, data/intensities/basecalls/BC-12_S12_L001_R2_001.fastq.gz           
           'file_small_md5': '4c3328bcf26ffb54da4de7b3c8879f94', # for file id 9896072
           'file_large_md5': '9267236a2d870da1d4cb73868bb51b35', # for file id 9896135 
           # for upload tests
           'file_small_upload': 'data/test.small.upload.txt',
           'file_large_upload': 'data/BC-12_S12_L001_R2_001.fastq.gz',
           'file_small_upload_size': 11,
           'file_large_upload_size': 57995799,
           'file_small_upload_content_type' : 'text/plain',
           'file_large_upload_content_type' : 'application/octet-stream',
           'file_small_upload_md5' : '2145401ac1bb1ca2ba1b3a382c9c67d0',
           #'file_small_upload_md5' : 'ff88b8bdbb86f219d19a22a3a0795429',
           'file_large_upload_md5' : '9267236a2d870da1d4cb73868bb51b35',
           'create_project_name': 'Python SDK Unit Test Data',
           'create_sample_name': 'Python SDK Unit Test Data',
           # for runs, genomes, projects, samples, appresults
           'run_id': '555555',
           'genome_id': '1',
           'project_id': '596596',
           'sample_id': '855855',
           'read_length': 140,
           'raw_count': '446158',
           # zcat data/BC-12_S12_L001_R2_001.fastq.gz | grep "@:89:A0172" | grep "N" | wc -l
           'PF_count': '446158',
           'appresult_id': '1213212',
           'appresult_referenced_sample_id': '855855',
           #'appsession_id': '1305304', TEMP           
           # for coverage and variant apis
           'bam_file_id': '9895890',
           'bam_cov_chr_name': 'chr',
           'bam_cov_start_coord': '1',
           'bam_cov_end_coord': '128', # must be divisible by 128
           'vcf_file_id': '9895892',
           'vcf_chr_name': 'chr',
           'vcf_start_coord': '1',
           'vcf_end_coord': '200000',  
          }

class TestFileDownloadMethods(TestCase):
    '''
    Tests methods of File objects
    '''
    def setUp(self):        
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.file = self.api.getFileById(tconst['file_id_small'])
        self.temp_dir = mkdtemp()    
            
    def tearDown(self):
        shutil.rmtree(self.temp_dir) 
        
    def testDownloadFile(self):
        new_file = self.file.downloadFile(
            self.api,
            localDir = self.temp_dir,            
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        with open(file_path, "r+b") as fp:
            self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)
        
    def testDownloadFileWithBsDirectoryArg(self):
        new_file = self.file.downloadFile(
            self.api,
            localDir = self.temp_dir,
            createBsDir = True,    
            )
        file_path = os.path.join(self.temp_dir, new_file.Path)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        with open(file_path, "r+b") as fp:
            self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)
        
    def testDownloadFileWithByteRangeArg(self):
        new_file = self.file.downloadFile(
            self.api,
            localDir = self.temp_dir,
            byteRange = [1000,2000]            
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size is correct
        self.assertEqual(1001, os.stat(file_path).st_size)
        os.remove(file_path)        

class TestAPIFileUploadMethods_SmallFiles(TestCase):
    '''
    Tests single and multi-part upload methods
    '''
    @classmethod
    def setUpClass(cls):    
        '''
        For all upload unit tests (not per test):
        Create a new 'unit test' project, or get it if exists, to upload to data to.
        Then create a new app result in this project, getting a new app session id
        '''        
        cls.api = BaseSpaceAPI(profile='unit_tests')        
        cls.proj = cls.api.createProject(tconst['create_project_name'])                        
        cls.ar = cls.proj.createAppResult(cls.api, "test upload", "test upload", appSessionId="")
    
    def test__singlepartFileUpload__(self):                    
        testDir = "testSinglePartSmallFileUploadDirectory"
        fileName = os.path.basename(tconst['file_small_upload'])
        myFile = self.api.__singlepartFileUpload__(
            resourceType = 'appresults',
            resourceId = self.ar.Id,
            localPath=tconst['file_small_upload'], 
            fileName=fileName, 
            directory=testDir, 
            contentType=tconst['file_small_upload_content_type'])                
        self.assertEqual(myFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(myFile.Size, tconst['file_small_upload_size'])
        self.assertEqual(myFile.UploadStatus, 'complete')
        # test fresh File object
        newFile = self.api.getFileById(myFile.Id)
        self.assertEqual(newFile.Path, os.path.join(testDir, fileName))        
        self.assertEqual(newFile.Size, tconst['file_small_upload_size'])
        self.assertEqual(newFile.UploadStatus, 'complete')                        

    def testAppResultFileUpload_SmallUpload(self):
        testDir = "testSmallUploadDirectory"
        fileName = os.path.basename(tconst['file_small_upload'])
        myFile = self.api.appResultFileUpload(
            Id=self.ar.Id, 
            localPath=tconst['file_small_upload'], 
            fileName=fileName, 
            directory=testDir, 
            contentType=tconst['file_small_upload_content_type'])                
        self.assertEqual(myFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(myFile.Size, tconst['file_small_upload_size'])
        self.assertEqual(myFile.UploadStatus, 'complete')
        # test fresh File object
        newFile = self.api.getFileById(myFile.Id)
        self.assertEqual(newFile.Path, os.path.join(testDir, fileName))        
        self.assertEqual(newFile.Size, tconst['file_small_upload_size'])
        self.assertEqual(newFile.UploadStatus, 'complete')

    def test__initiateMultipartFileUpload__(self):
        testDir = "test__initiateMultipartFileUpload__"
        file = self.api.__initiateMultipartFileUpload__(
            resourceType = 'appresults',
            resourceId = self.ar.Id,
            fileName = os.path.basename(tconst['file_small_upload']),            
            directory = testDir,
            contentType=tconst['file_small_upload_content_type'])
        self.assertEqual(file.Name, os.path.basename(tconst['file_small_upload']))                    
        
    def test__uploadMultipartUnit__(self):
        testDir = "test__uploadMultipartUnit__"
        file = self.api.__initiateMultipartFileUpload__(
            resourceType = 'appresults',
            resourceId = self.ar.Id,
            fileName = os.path.basename(tconst['file_small_upload']),            
            directory = testDir,
            contentType=tconst['file_small_upload_content_type'])
        with open(tconst['file_small_upload']) as fp:
            out = fp.read()
            md5 = hashlib.md5(out).digest().encode('base64')  
        response = self.api.__uploadMultipartUnit__(
            Id = file.Id,
            partNumber = 1,
            md5 = md5,
            data = tconst['file_small_upload'])
        self.assertNotEqual(response, None, 'Upload part failure will return None')
        self.assertTrue('ETag' in response['Response'], 'Upload part success will contain a Response dict with an ETag element')
            
    def test__finalizeMultipartFileUpload__(self):
        testDir = "test__finalizeMultipartFileUpload__"
        file = self.api.__initiateMultipartFileUpload__(
            resourceType = 'appresults',
            resourceId = self.ar.Id,
            fileName = os.path.basename(tconst['file_small_upload']),            
            directory = testDir,
            contentType=tconst['file_small_upload_content_type'])
        with open(tconst['file_small_upload']) as fp:
            out = fp.read()
            md5 = hashlib.md5(out).digest().encode('base64')  
        response = self.api.__uploadMultipartUnit__(
            Id = file.Id,
            partNumber = 1,
            md5 = md5,
            data = tconst['file_small_upload'])
        final_file = self.api.__finalizeMultipartFileUpload__(file.Id)
        self.assertEqual(final_file.UploadStatus, 'complete')

    def testMultiPartFileUpload_SmallPartSizeException(self):
        with self.assertRaises(UploadPartSizeException):
            myFile = self.api.multipartFileUpload(
                resourceType = 'appresults',
                resourceId = self.ar.Id,
                localPath=tconst['file_large_upload'], 
                fileName=os.path.basename(tconst['file_large_upload']), 
                directory="",                          
                contentType=tconst['file_large_upload_content_type'],            
                partSize=5, # MB, chunk size                        
                )

    def testMultiPartFileUpload_LargePartSizeException(self):
        with self.assertRaises(UploadPartSizeException):
            myFile = self.api.multipartFileUpload(
                resourceType = 'appresults',
                resourceId = self.ar.Id,
                localPath=tconst['file_large_upload'], 
                fileName=os.path.basename(tconst['file_large_upload']), 
                directory="",                          
                contentType=tconst['file_large_upload_content_type'],            
                partSize=26, # MB, chunk size                        
                )

    def testIntegration_SmallFileUploadThenDownload(self):            
        upFile = self.api.appResultFileUpload(
            Id=self.ar.Id, 
            localPath=tconst['file_small_upload'], 
            fileName=os.path.basename(tconst['file_small_upload']), 
            directory="test_upload_download_dir", 
            contentType=tconst['file_small_upload_content_type'])        
        tempDir = mkdtemp()        
        downFile = self.api.fileDownload(upFile.Id, tempDir, createBsDir=True)
        downPath = os.path.join(tempDir, upFile.Path)
        self.assertTrue(os.path.isfile(downPath), "Failed to find path %s" % downPath)
        # confirm file size and md5 are correct
        self.assertEqual(os.path.getsize(tconst['file_small_upload']), os.path.getsize(downPath))
        with open(downPath, "r+b") as fp:
            self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_upload_md5'])
        os.remove(downPath)                        


class TestMultipartFileTransferMethods(TestCase):
    '''
    Tests classes and methods in MultipartFileTransfer.py
    '''
    @skip('Tests not written yet')
    def testTODO(self):
        pass

class TestAPIFileUploadMethods_LargeFiles(TestCase):
    '''
    Tests multi-part upload methods on large(-ish) files -- may be time consuming
    '''
    @classmethod
    def setUpClass(cls):    
        '''
        For all upload unit tests (not per test):
        Create a new 'unit test' project, or get it if exists, to upload to data to.
        Then create a new app result in this project, getting a new app session id
        '''        
        cls.api = BaseSpaceAPI(profile='unit_tests')
        cls.proj = cls.api.createProject(tconst['create_project_name'])
        cls.ar = cls.proj.createAppResult(cls.api, "test upload", "test upload", appSessionId="")
 
#    @skip('large upload')
    def testAppResultFileUpload_LargeUpload(self):
        testDir = "testLargeUploadDirectory"
        fileName = os.path.basename(tconst['file_large_upload'])            
        myFile = self.api.appResultFileUpload(
            Id=self.ar.Id, 
            localPath=tconst['file_large_upload'], 
            fileName=fileName, 
            directory=testDir, 
            contentType=tconst['file_small_upload_content_type'])
        self.assertEqual(myFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(myFile.Size, tconst['file_large_upload_size'])
        self.assertEqual(myFile.UploadStatus, 'complete')
        # test fresh File object
        newFile = self.api.getFileById(myFile.Id)
        self.assertEqual(newFile.Path, os.path.join(testDir, fileName))        
        self.assertEqual(newFile.Size, tconst['file_large_upload_size'])
        self.assertEqual(newFile.UploadStatus, 'complete')
        
#    @skip('large upload')
    def testMultiPartFileUpload(self):
        testDir = "testMultipartUploadDir"
        fileName = os.path.basename(tconst['file_large_upload']) 
        myFile = self.api.multipartFileUpload(
            resourceType = 'appresults',
            resourceId = self.ar.Id,
            localPath=tconst['file_large_upload'], 
            fileName=fileName, 
            directory=testDir,                          
            contentType=tconst['file_large_upload_content_type'],
            tempDir=None, 
            processCount = 4,
            partSize= 10, # MB, chunk size            
            #tempDir = args.temp_dir
            )            
        self.assertEqual(myFile.Size, tconst['file_large_upload_size'])
        self.assertEqual(myFile.Name, fileName)
        self.assertEqual(myFile.Path, os.path.join(testDir, fileName))    
        self.assertEqual(myFile.UploadStatus, 'complete')    

#    @skip('large upload and download')
    def testIntegration_LargeFileUploadThenDownload(self):            
        upFile = self.api.appResultFileUpload(
            Id=self.ar.Id, 
            localPath=tconst['file_large_upload'], 
            fileName=os.path.basename(tconst['file_large_upload']), 
            directory="test_upload_download_dir", 
            contentType=tconst['file_large_upload_content_type'])        
        tempDir = mkdtemp()        
        downFile = self.api.fileDownload(upFile.Id, tempDir, createBsDir=True)
        downPath = os.path.join(tempDir, upFile.Path)
        self.assertTrue(os.path.isfile(downPath), "Failed to find path %s" % downPath)
        # confirm file size and md5 are correct
        self.assertEqual(os.path.getsize(tconst['file_large_upload']), os.path.getsize(downPath))
        with open(downPath, "r+b") as fp:
            self.assertEqual(Utils.md5_for_file(fp), tconst['file_large_upload_md5'])
        os.remove(downPath)                        
 
class TestAPIFileDownloadMethods_SmallFiles(TestCase):
    '''
    Tests single and multi-part download methods
    '''
    def setUp(self):        
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.temp_dir = mkdtemp()    
            
    def tearDown(self):
        shutil.rmtree(self.temp_dir) 

    def test__downloadFile__(self):
        file_name = 'testfile.abc'
        bs_file = self.api.getFileById(tconst['file_id_small'])
        self.api.__downloadFile__(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,
            name = file_name,            
            )
        file_path = os.path.join(self.temp_dir, file_name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertEqual(bs_file.Size, os.stat(file_path).st_size)
        with open(file_path, "r+b") as fp:
            self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)
        
    def test__downloadFile__WithByteRangeArg(self):
        file_name = 'testfile.abc'        
        self.api.__downloadFile__(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,
            name = file_name,
            byteRange = [2000,3000]            
            )
        file_path = os.path.join(self.temp_dir, file_name)
        self.assertTrue(os.path.isfile(file_path))        
        self.assertEqual(3001, os.stat(file_path).st_size) # seek() into file, so size is larger
        os.remove(file_path)

    def test__downloadFile__WithByteRangeStoredInStandaloneFile(self):
        file_name = 'testfile.abc'
        self.api.__downloadFile__(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,
            name = file_name,
            byteRange = [2000,3000],
            standaloneRangeFile = True,         
            )
        file_path = os.path.join(self.temp_dir, file_name)
        self.assertTrue(os.path.isfile(file_path))        
        self.assertEqual(1001, os.stat(file_path).st_size) # no seek() into standalone file, so size is only range data
        os.remove(file_path)
        
    def test__downloadFile__WithLockArg(self):
        lock = multiprocessing.Lock() # just testing that passing in a lock won't crash anything
        file_name = 'testfile.abc'
        bs_file = self.api.getFileById(tconst['file_id_small'])
        self.api.__downloadFile__(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,
            name = file_name,
            lock = lock,            
            )
        file_path = os.path.join(self.temp_dir, file_name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertEqual(bs_file.Size, os.stat(file_path).st_size)
        with open(file_path, "r+b") as fp:
            self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)        
        
    def testFileDownload_SmallFile(self):
        new_file = self.api.fileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,            
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)

    def testFileDownload_SmallFileWithBsDirectoryArg(self):
        new_file = self.api.fileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,
            createBsDir = True,         
            )
        file_path = os.path.join(self.temp_dir, new_file.Path)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)

    def testFileDownload_WithByteRangeArg(self):
        new_file = self.api.fileDownload(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,
            byteRange = [1000,2000]            
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size is correct
        self.assertEqual(1001, os.stat(file_path).st_size)
        os.remove(file_path)        

    def testFileDownload_LargeByteRangeException(self):
        with self.assertRaises(ByteRangeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1,10000001]            
                )        

    def testFileDownload_MisorderedByteRangeException(self):
        with self.assertRaises(ByteRangeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1000, 1]            
                )

    def testFileDownload_PartialByteRangeException(self):
        with self.assertRaises(ByteRangeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1000]            
                )

    def testMultipartFileDownload_SmallFile(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,
            processCount = 10,
            partSize = 12
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path), "Failed to find file, expected here: %s" % file_path)
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)

    def testMultipartFileDownload_WithBsDirectoryArg(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,
            processCount = 10,
            partSize = 12,
            createBsDir = True,
            )
        file_path = os.path.join(self.temp_dir, new_file.Path)
        self.assertTrue(os.path.isfile(file_path), "Failed to find file, expected here: %s" % file_path)
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)

    def testMultipartFileDownload_WithTempFileArg(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,            
            tempDir = self.temp_dir
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct        
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)

    def testMultipartFileDownload_WithTempFileAndBsDirArgs(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,            
            tempDir = self.temp_dir,
            createBsDir = True,
            )
        file_path = os.path.join(self.temp_dir, new_file.Path)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct        
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_small_md5'])
        os.remove(file_path)

class TestAPIFileDownloadMethods_LargeFiles(TestCase):
    '''
    Tests multi-part download methods on large(-ish) files -- may be time consuming
    '''
    def setUp(self):        
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.temp_dir = mkdtemp()    
            
    def tearDown(self):
        shutil.rmtree(self.temp_dir) 

#    @skip('large download')
    def testFileDownload_LargeFile(self):
        new_file = self.api.fileDownload(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,            
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size is correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_large_md5'])
        os.remove(file_path)

#    @skip('large download')
    def testFileDownload_LargeFileWithBsDirectoryArg(self):
        new_file = self.api.fileDownload(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,
            createBsDir = True,         
            )
        file_path = os.path.join(self.temp_dir, new_file.Path)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size is correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_large_md5'])
        os.remove(file_path)

#    @skip('large download')
    def testMultipartFileDownload_LargeFile(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,
            processCount = 10,
            partSize = 12
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path), "Failed to find file, expected here: %s" % file_path)
        # confirm file size and md5 are correct
        self.assertEqual(new_file.Size, os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertEqual(Utils.md5_for_file(fp), tconst['file_large_md5'])
        os.remove(file_path)

class TestAppResultMethods(TestCase):
    '''
    Tests AppResult object methods
    '''
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.appResult = self.api.getAppResultById(tconst['appresult_id'])
                
    def testIsInit(self):        
        self.assertEqual(self.appResult.isInit(), True)
            
    def testIsInitException(self):
        appResult = AppResult.AppResult()        
        with self.assertRaises(ModelNotInitializedException):
            appResult.isInit()                                      

    def testGetAccessString(self):
        self.assertEqual(self.appResult.getAccessStr(), 'write appresult ' + self.appResult.Id)
        
    def testGetAccessStringWithArg(self):
        self.assertEqual(self.appResult.getAccessStr('read'), 'read appresult ' + self.appResult.Id)
            
    def testGetReferencedSamplesIds(self):
        self.assertEqual(self.appResult.getReferencedSamplesIds(), [tconst['appresult_referenced_sample_id']])
        
    def testGetReferencedSamples(self):
        samples = self.appResult.getReferencedSamples(self.api)
        self.assertEqual(samples[0].Id, tconst['appresult_referenced_sample_id'])
    
    def testGetFiles(self):
        files = self.appResult.getFiles(self.api)        
        self.assertTrue(hasattr(files[0], 'Id'))

    def testGetFilesWithQp(self):
        files = self.appResult.getFiles(self.api, qp({'Limit':1}))        
        self.assertTrue(hasattr(files[0], 'Id'))
        self.assertEqual(len(files), 1)
    
    def testUploadFile(self):
        '''
        Create a new 'unit test' project, or get it if exists, to upload to data to.
        Then create a new appresult in this project, getting a new appsession id
        Then...upload a file to the new appresult
        '''
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test appresult upload", "test appresult upload", appSessionId="")
        testDir = "testSmallUploadAppResultDirectory"
        fileName = os.path.basename(tconst['file_small_upload'])
        myFile = ar.uploadFile(
            api=self.api, 
            localPath=tconst['file_small_upload'], 
            fileName=fileName, 
            directory=testDir, 
            contentType=tconst['file_small_upload_content_type'])
        self.assertEqual(myFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(myFile.Size, tconst['file_small_upload_size'])
        self.assertEqual(myFile.UploadStatus, 'complete')
        # test fresh File object
        newFile = self.api.getFileById(myFile.Id)
        self.assertEqual(newFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(newFile.Size, tconst['file_small_upload_size'])
        self.assertEqual(newFile.UploadStatus, 'complete')                

class TestAPIAppResultMethods(TestCase):
    '''
    Tests API object AppResult methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')

    def testGetAppResultById(self):
        appresult = self.api.getAppResultById(tconst['appresult_id'])
        self.assertTrue(appresult.Id, 'appresult_id')
        
    def testGetAppResultByIdWithQp(self):
        appresult = self.api.getAppResultById(tconst['appresult_id'], qp({'Limit':1})) # Limit doesn't make sense here
        self.assertTrue(appresult.Id, 'appresult_id')        
            
    def testGetAppResultPropertiesById(self):
        props = self.api.getAppResultPropertiesById(tconst['appresult_id'])        
        self.assertTrue(hasattr(props, 'TotalCount'))
        
    def testGetAppResultPropertiesByIdWithQp(self):
        props = self.api.getAppResultPropertiesById(tconst['appresult_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(props, 'TotalCount')) 
        self.assertEqual(len(props.Items), 1)

    def testGetAppResultFilesById(self):
        files = self.api.getAppResultFilesById(tconst['appresult_id'])        
        self.assertTrue(hasattr(files[0], 'Id'))
        
    def testGetAppResultFilesByIdWithQp(self):
        files = self.api.getAppResultFilesById(tconst['appresult_id'], qp({'Limit':1}))        
        self.assertTrue(hasattr(files[0], 'Id'))
        self.assertEqual(len(files), 1)    
            
    def testGetAppResultFiles(self):
        files = self.api.getAppResultFiles(tconst['appresult_id'])        
        self.assertTrue(hasattr(files[0], 'Id'))
        
    def testGetAppResultFilesWithQp(self):
        files = self.api.getAppResultFiles(tconst['appresult_id'], qp({'Limit':1}))        
        self.assertTrue(hasattr(files[0], 'Id'))
        self.assertEqual(len(files), 1)    

    def testGetAppResultsByProject(self):
        appresults = self.api.getAppResultsByProject(tconst['project_id'])
        self.assertTrue(hasattr(appresults[0], 'Id'))
        
    def testGetAppResultsByProjectWithQp(self):
        appresults = self.api.getAppResultsByProject(tconst['project_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(appresults[0], 'Id'))
        self.assertEqual(len(appresults), 1)
        
    def testGetAppResultsByProjectWithStatusesArg(self):
        appresults = self.api.getAppResultsByProject(tconst['project_id'], statuses=['complete'])
        self.assertTrue(hasattr(appresults[0], 'Id'))
        
    def testCreateAppResultNewAppSsn(self):
        '''
        Create a new 'unit test' project, or get it if exists.
        Create a new app result that creates a new app ssn.        
        '''
        proj = self.api.createProject(tconst['create_project_name'])   
        ar = self.api.createAppResult(proj.Id, name="test create appresult new ssn", 
            desc="test create appresult new ssn", appSessionId="")
        self.assertTrue(hasattr(ar, 'Id'))        

    def testCreateAppResultCredentialsAppSsn(self):
        '''
        Create a new 'unit test' project, or get it if exists.
        Create a new app result that creates a new app ssn,
        then create a new api obj with the new ssn,
        then create an appresult in the new ssn
        '''
        proj = self.api.createProject(tconst['create_project_name'])   
        ar = self.api.createAppResult(proj.Id, name="test create appresult creds ssn", 
            desc="test create appresult creds ssn", appSessionId="")
        #url = urlparse(self.api.apiClient.apiServer)
        #newApiServer = url.scheme + "://" + url.netloc
        #new_api = BaseSpaceAPI(self.api.key, self.api.secret, newApiServer, 
        new_api = BaseSpaceAPI(self.api.key, self.api.secret, self.api.apiServer,
            self.api.version, ar.AppSession.Id, self.api.getAccessToken())
        ar2 = new_api.createAppResult(proj.Id, name="test create appresult creds ssn 2", 
            desc="test create appresult creds ssn 2")
        self.assertTrue(hasattr(ar2, 'Id'))
        
    def testCreateAppResultProvidedAppSsn(self):
        '''
        Create a new app result that creates a new app ssn,
        then create a new api obj with the new ssn,
        then create an appresult in the new ssn
        '''
        proj = self.api.createProject(tconst['create_project_name'])   
        ar = self.api.createAppResult(proj.Id, name="test create appresult provided ssn", 
            desc="test create appresult provided ssn", appSessionId="")
        ar2 = self.api.createAppResult(proj.Id, name="test create appresult provided ssn 2", 
            desc="test create appresult provided ssn 2", appSessionId=ar.AppSession.Id)
        self.assertTrue(hasattr(ar2, 'Id'))
        
    # Note that appResultFileUpload() is tested with other file upload methods 
    # (in a separate suite: TestAPIUploadMethods)
    
class TestRunMethods(TestCase):
    '''
    Tests Run object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.run = self.api.getRunById(tconst['run_id'])                                        

    def testIsInit(self):        
        self.assertEqual(self.run.isInit(), True)
            
    def testIsInitException(self):
        run = Run.Run()
        with self.assertRaises(ModelNotInitializedException):
            run.isInit()                                      

    def testGetAccessString(self):
        self.assertEqual(self.run.getAccessStr(), 'write run ' + self.run.Id)
        
    def testGetAccessStringWithArg(self):
        self.assertEqual(self.run.getAccessStr('read'), 'read run ' + self.run.Id)

    def testRunGetFiles(self):
        rf = self.run.getFiles(self.api)                
        self.assertTrue(hasattr(rf[0], 'Id'))
        
    def testRunGetFilesWithQp(self):
        rf = self.run.getFiles(self.api, qp({'Limit':200}))        
        self.assertTrue(hasattr(rf[0], 'Id'))
        self.assertEqual(len(rf), 200)

    def testRunSamples(self):
        rs = self.run.getSamples(self.api)        
        self.assertTrue(hasattr(rs[0], 'Id'))
        
    def testRunSamplesWithQp(self):
        rs = self.run.getSamples(self.api, qp({'Limit':1}))
        self.assertTrue(hasattr(rs[0], 'Id'))
        self.assertEqual(len(rs), 1)

class TestAPIRunMethods(TestCase):
    '''
    Tests API object Run methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')

    def testGetAccessibleRunsByUser(self):
        runs = self.api.getAccessibleRunsByUser()
        self.assertIsInstance(int(runs[0].Id), int)

    def testGetAccessibleRunsByUserWithQp(self):
        runs = self.api.getAccessibleRunsByUser(qp({'Limit':500}))
        run = next(r for r in runs if r.Id == tconst['run_id'])
        self.assertTrue(run.Id, tconst['run_id'])
        
    def testGetRunById(self):                                                    
        rf = self.api.getRunById(tconst['run_id'])        
        self.assertEqual(rf.Id, tconst['run_id'])
        
    def testGetRunByIdWithQp(self):                                                    
        rf = self.api.getRunById(tconst['run_id'], qp({'Limit':1})) # limit doesn't make much sense here            
        self.assertEqual(rf.Id, tconst['run_id'])
        
    def testGetRunPropertiesById(self):                                                    
        props = self.api.getRunPropertiesById(tconst['run_id'])        
        self.assertTrue(hasattr(props, 'TotalCount'))        
        
    def testGetRunPropertiesByIdWithQp(self):                                                    
        props = self.api.getRunPropertiesById(tconst['run_id'], qp({'Limit':1}))                
        self.assertTrue(hasattr(props, 'TotalCount'))
        self.assertEqual(len(props.Items), 1)
    
    def testGetRunFilesById(self):                                                    
        rf = self.api.getRunFilesById(tconst['run_id'])                
        self.assertTrue(hasattr(rf[0], 'Id'))
        
    def testGetRunFilesByIdWithQp(self):
        rf = self.api.getRunFilesById(tconst['run_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(rf[0], 'Id'))
        self.assertEqual(len(rf), 1)        

    def testRunSamplesById(self):
        rs = self.api.getRunSamplesById(tconst['run_id'])        
        self.assertTrue(hasattr(rs[0], 'Id'))
        
    def testRunSamplesByIdWithQp(self):
        rs = self.api.getRunSamplesById(tconst['run_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(rs[0], 'Id'))
        self.assertEqual(len(rs), 1)

class TestSampleMethods(TestCase):
    '''
    Tests Sample object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.sample = self.api.getSampleById(tconst['sample_id'])
        
    def testIsInit(self):        
        self.assertEqual(self.sample.isInit(), True)
            
    def testIsInitException(self):
        sample = Sample.Sample()
        with self.assertRaises(ModelNotInitializedException):
            sample.isInit()                                      

    def testGetAccessString(self):
        self.assertEqual(self.sample.getAccessStr(), 'write sample ' + self.sample.Id)
        
    def testGetAccessStringWithArg(self):
        self.assertEqual(self.sample.getAccessStr('read'), 'read sample ' + self.sample.Id)
            
    def testGetReferencedAppResults(self):
        ars = self.sample.getReferencedAppResults(self.api)
        self.assertTrue(hasattr(ars[0], 'Id'), "Referenced AppResult should have an Id (assuming this Sample has been analyzed)")
    
    def testGetFiles(self):
        files = self.sample.getFiles(self.api)        
        self.assertTrue(hasattr(files[0], "Id"))

    def testGetFilesWithQp(self):
        files = self.sample.getFiles(self.api, qp({'Limit':1}))        
        self.assertTrue(hasattr(files[0], "Id"))
        self.assertEqual(len(files), 1)

    def testUploadFile(self):
        '''
        Create a new 'unit test' project, or get it if exists, to upload to data to.
        Then create a new sample in this project, getting a new appsession id
        Then...upload a file to the new sample
        '''
        proj = self.api.createProject(tconst['create_project_name'])
        s = proj.createSample(self.api, "SRA123456", "SRA Import", 3,
                              tconst['create_sample_name'], [tconst['read_length']],
                              tconst['raw_count'], tconst['PF_count'], appSessionId="")
        testDir = "testLargeUploadSampleDirectory"
        fileName = os.path.basename(tconst['file_large_upload'])
        myFile = s.uploadFile(
            api=self.api, 
            localPath=tconst['file_large_upload'], 
            fileName=fileName, 
            directory=testDir, 
            contentType=tconst['file_large_upload_content_type'])
        self.assertEqual(myFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(myFile.Size, tconst['file_large_upload_size'])
        self.assertEqual(myFile.UploadStatus, 'complete')
        # test fresh File object
        newFile = self.api.getFileById(myFile.Id)
        self.assertEqual(newFile.Path, os.path.join(testDir, fileName))
        self.assertEqual(newFile.Size, tconst['file_large_upload_size'])
        self.assertEqual(newFile.UploadStatus, 'complete')

class TestAPISampleMethods(TestCase):
    '''
    Tests API Sample object methods
    '''
    def setUp(self):
        self.api = BaseSpaceAPI(profile='unit_tests')
              
    def testGetSamplesByProject(self):
        samples = self.api.getSamplesByProject(tconst['project_id'])
        self.assertIsInstance(int(samples[0].Id), int)

    def testGetSamplesByProjectWithQp(self):
        samples = self.api.getSamplesByProject(tconst['project_id'], qp({'Limit':1}))
        self.assertIsInstance(int(samples[0].Id), int)
        self.assertEqual(len(samples), 1)        

    def testGetSampleById(self):        
        sample = self.api.getSampleById(tconst['sample_id'])
        self.assertEqual(sample.Id, tconst['sample_id'])

    def testGetSampleByIdWithQp(self):        
        sample = self.api.getSampleById(tconst['sample_id'], qp({'Limit':1})) # Limit doesn't make much sense here
        self.assertEqual(sample.Id, tconst['sample_id'])        
    
    def testGetSamplePropertiesById(self):
        props = self.api.getSamplePropertiesById(tconst['sample_id'])
        self.assertTrue(hasattr(props, 'TotalCount'))        

    def testGetSamplePropertiesByIdWithQp(self):
        props = self.api.getSamplePropertiesById(tconst['sample_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(props, 'TotalCount'))        
        self.assertEqual(len(props.Items), 1)
        
    def testGetSampleFilesById(self):
        files = self.api.getSampleFilesById(tconst['sample_id'])
        self.assertTrue(hasattr(files[0], 'Id'))
        
    def testGetSampleFilesByIdWithQp(self):
        files = self.api.getSampleFilesById(tconst['sample_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(files[0], 'Id'))
        self.assertEqual(len(files), 1)

class TestProjectMethods(TestCase):
    '''
    Tests Project object methods
    '''
    def setUp(self):
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.project = self.api.getProjectById(tconst['project_id'])
        
    def testIsInit(self):        
        self.assertEqual(self.project.isInit(), True)
            
    def testIsInitException(self):
        project = Project.Project()
        with self.assertRaises(ModelNotInitializedException):
            project.isInit()

    def testGetAccessString(self):
        self.assertEqual(self.project.getAccessStr(), 'write project ' + self.project.Id)
        
    def testGetAccessStringWithArg(self):
        self.assertEqual(self.project.getAccessStr('read'), 'read project ' + self.project.Id)            
    
    def testGetAppResults(self):
        appresults = self.project.getAppResults(self.api)
        self.assertTrue(hasattr(appresults[0], 'Id'))
            
    def testGetAppResultsWithOptionalArgs(self):
        appresults = self.project.getAppResults(self.api, qp({'Limit':1}), statuses=['complete'])
        self.assertTrue(hasattr(appresults[0], 'Id'))
        self.assertEqual(len(appresults), 1)

    def testGetSamples(self):
        samples = self.project.getSamples(self.api)
        self.assertIsInstance(int(samples[0].Id), int)
    
    def testGetSamplesWithOptionalArgs(self):
        samples = self.project.getSamples(self.api, qp({'Limit':1}))
        self.assertIsInstance(int(samples[0].Id), int)
        self.assertEqual(len(samples), 1)

    def testCreateAppResult(self):
        '''
        Create a new 'unit test' project, or get it if exists.
        Create a new app result that creates a new app ssn,
        then create a new api obj with the new ssn,
        then create an appresult in the new ssn
        '''
        proj = self.api.createProject(tconst['create_project_name'])   
        ar = proj.createAppResult(self.api, name="test create appresult creds ssn, project obj", 
            desc="test create appresult creds ssn, project obj", appSessionId="")
        #url = urlparse(self.api.apiClient.apiServer)
        #newApiServer = url.scheme + "://" + url.netloc        
        #new_api = BaseSpaceAPI(self.api.key, self.api.secret, newApiServer, 
        new_api = BaseSpaceAPI(self.api.key, self.api.secret, self.api.apiServer,                               
            self.api.version, ar.AppSession.Id, self.api.getAccessToken())
        ar2 = proj.createAppResult(new_api, name="test create appresult creds ssn, project obj 2", 
            desc="test create appresult creds ssn, proejct obj 2")
        self.assertTrue(hasattr(ar2, 'Id'))        

    def testCreateAppResultWithOptionalArgs(self):
        '''
        Create a new 'unit test' project, or get it if exists.
        Create a new app result that creates a new app ssn.        
        '''
        proj = self.api.createProject(tconst['create_project_name'])   
        ar = proj.createAppResult(self.api, name="test create appresult new ssn, project obj", 
            desc="test create appresult new ssn, project obj", samples=[], appSessionId="")
        self.assertTrue(hasattr(ar, 'Id'))        

    def testCreateSample(self):
        '''
        Create a new 'unit test' project, or get it if exists.
        Create a new sample that creates a new app ssn,
        then create a new api obj with the new ssn,
        then create a sample in the new ssn
        '''
        proj = self.api.createProject(tconst['create_project_name'])   
        s = proj.createSample(self.api, "SRA123456", "SRA Import", 1,
                              tconst['create_sample_name'], [tconst['read_length']],
                              tconst['raw_count'], tconst['PF_count'], appSessionId="")
        new_api = BaseSpaceAPI(self.api.key, self.api.secret, self.api.apiServer,
            self.api.version, s.AppSession.Id, self.api.getAccessToken())
        s2 = proj.createSample(self.api, "SRA123456_2", "2nd SRA Import", 2,
                              tconst['create_sample_name'], [tconst['read_length']],
                              tconst['raw_count'], tconst['PF_count'], appSessionId="")
        self.assertTrue(hasattr(s2, 'Id'))

class TestAPIProjectMethods(TestCase):
    '''
    Tests API Project object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')

    def testCreateProject(self):
        proj = self.api.createProject(tconst['create_project_name'])
        self.assertEqual(proj.Name, tconst['create_project_name'])        
              
    def testGetProjectById(self):
        proj = self.api.getProjectById(tconst['project_id'])
        self.assertEqual(proj.Id, tconst['project_id'])

    def testGetProjectByIdWithQp(self):
        proj = self.api.getProjectById(tconst['project_id'], qp({'Limit':1})) # Limit doesn't make sense here
        self.assertEqual(proj.Id, tconst['project_id'])                        

    def testGetProjectPropertiesById(self):
        props = self.api.getProjectPropertiesById(tconst['project_id'])
        self.assertTrue(hasattr(props, 'TotalCount'))                         

    def testGetProjectPropertiesByIdWithQp(self):
        props = self.api.getProjectPropertiesById(tconst['project_id'], qp({'Limit':1}))         
        self.assertTrue(hasattr(props, 'TotalCount'))      
        # test project has no properties, so can't test Limit

    def testGetProjectByUser(self):
        projects = self.api.getProjectByUser()        
        self.assertTrue(hasattr(projects[0], 'Id'))
        
    def testGetProjectByUserWithQp(self):
        projects = self.api.getProjectByUser(qp({'Limit':1}))        
        self.assertTrue(hasattr(projects[0], 'Id'))        

class TestUserMethods(TestCase):
    '''
    Tests User object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.user = self.api.getUserById('current')
        
    def testIsInit(self):        
        self.assertEqual(self.user.isInit(), True)
            
    def testIsInitException(self):
        user = User.User()
        with self.assertRaises(ModelNotInitializedException):
            user.isInit()
            
    def testGetProjects(self):
        projects = self.user.getProjects(self.api)        
        self.assertTrue(hasattr(projects[0], 'Id'))
        
    def testGetProjectsWithQp(self):
        projects = self.user.getProjects(self.api, queryPars=qp({'Limit':1}))        
        self.assertTrue(hasattr(projects[0], 'Id'))
        self.assertTrue(len(projects), 1)
    
    def testGetRuns(self):
        runs = self.user.getRuns(self.api)        
        self.assertTrue(hasattr(runs[0], 'Id'))
        
    def testGetRunsWithQp(self):
        runs = self.user.getRuns(self.api, queryPars=qp({'Limit':1}))        
        self.assertTrue(hasattr(runs[0], 'Id'))
        self.assertTrue(len(runs), 1)

class TestAPIUserMethods(TestCase):
    '''
    Tests API User object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
                          
    def testGetUserById(self):
        user = self.api.getUserById('current')
        self.assertTrue(hasattr(user, 'Id'), 'User object should contain Id attribute')

class TestFileMethods(TestCase):
    '''
    Tests File object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.file = self.api.getFileById(tconst['file_id_small'])
        
    def testIsInit(self):        
        self.assertEqual(self.file.isInit(), True)
            
    def testIsInitException(self):
        file = File.File()
        with self.assertRaises(ModelNotInitializedException):
            file.isInit()
    
    # not testing isValidFileOption() -- deprecated   

    # downloadFile() is tested in a separate suite
    
    def testGetFileUrl(self):
        url = self.file.getFileUrl(self.api)
        url_parts = urlparse(url)
        self.assertEqual(url_parts.scheme, 'https')
    
    def testGetFileS3metadata(self):
        meta = self.file.getFileS3metadata(self.api)        
        self.assertTrue('url' in meta)
        self.assertTrue('etag' in meta)        

    def testGetIntervalCoverage(self):
        bam = self.api.getFileById(tconst['bam_file_id'])
        cov = bam.getIntervalCoverage(
            self.api,
            Chrom = tconst['bam_cov_chr_name'],
            StartPos = tconst['bam_cov_start_coord'],
            EndPos = tconst['bam_cov_end_coord'] )
        self.assertEqual(cov.Chrom, tconst['bam_cov_chr_name'])

    def testGetCoverageMeta(self):
        bam = self.api.getFileById(tconst['bam_file_id'])
        cov_meta = bam.getCoverageMeta(
            self.api,
            Chrom = tconst['bam_cov_chr_name'] )
        self.assertTrue(hasattr(cov_meta, 'MaxCoverage'))                    
        
    def testFilterVariant(self):
        vcf = self.api.getFileById(tconst['vcf_file_id'])
        vars = vcf.filterVariant(
            self.api, 
            Chrom = tconst['vcf_chr_name'],
            StartPos = tconst['vcf_start_coord'],
            EndPos = tconst['vcf_end_coord'], )            
        self.assertEqual(vars[0].CHROM, tconst['vcf_chr_name'])
    
    def testFilterVariantWithQp(self):
        vcf = self.api.getFileById(tconst['vcf_file_id'])
        vars = vcf.filterVariant(
            self.api, 
            Chrom = tconst['vcf_chr_name'],
            StartPos = tconst['vcf_start_coord'],
            EndPos = tconst['vcf_end_coord'],
            Format = 'json',
            queryPars = qp({'Limit':1}) )
        self.assertEqual(vars[0].CHROM, tconst['vcf_chr_name'])
        self.assertEqual(len(vars), 1)
        
    def testFilterVariantReturnVCFString(self):
        vcf = self.api.getFileById(tconst['vcf_file_id'])
        with self.assertRaises(NotImplementedError): # for now...
            vars = vcf.filterVariant(
                self.api, 
                Chrom = tconst['vcf_chr_name'],
                StartPos = tconst['vcf_start_coord'],
                EndPos = tconst['vcf_end_coord'],
                Format = 'vcf')
            #self.assertEqual(type(vars), str)            
    
    def testGetVariantMeta(self):
        vcf = self.api.getFileById(tconst['vcf_file_id'])
        hdr = vcf.getVariantMeta(self.api)
        self.assertTrue(hasattr(hdr, 'Metadata'))

    def testGetVariantMetaReturnVCFString(self):
        vcf = self.api.getFileById(tconst['vcf_file_id'])
        with self.assertRaises(NotImplementedError): # for now...
            hdr = vcf.getVariantMeta(self.api, Format='vcf')
            #self.assertEqual(type(hdr), str)

class TestAPIFileMethods(TestCase):
    '''
    Tests API File object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
                          
    def testGetFileById(self):
        file = self.api.getFileById(tconst['file_id_small'])
        self.assertTrue(file.Id, tconst['file_id_small'])

    def testGetFileByIdWithQp(self):
        file = self.api.getFileById(tconst['file_id_small'], qp({'Limit':1})) # Limit doesn't make much sense here
        self.assertEqual(file.Id, tconst['file_id_small'])        

    def testGetFilesBySample(self):
        files = self.api.getFilesBySample(tconst['sample_id'])
        self.assertTrue(hasattr(files[0], 'Id'))
        
    def testGetFilesBySampleWithQp(self):
        files = self.api.getFilesBySample(tconst['sample_id'], qp({'Limit':1}))
        self.assertTrue(hasattr(files[0], 'Id'))
        self.assertEqual(len(files), 1)

    def testGetFilePropertiesById(self):
        props = self.api.getFilePropertiesById(tconst['file_id_small'])
        self.assertTrue(hasattr(props, 'TotalCount'))
        
    def testGetFilePropertiesByIdWithQp(self):
        props = self.api.getFilePropertiesById(tconst['file_id_small'], qp({'Limit':1}))
        self.assertTrue(hasattr(props, 'TotalCount'))
        # can't test limit since test file has no properties

    def testFileUrl(self):
        url = self.api.fileUrl(tconst['file_id_small'])
        url_parts = urlparse(url)
        self.assertEqual(url_parts.scheme, 'https')
    
    def testFileS3metadata(self):
        meta = self.api.fileS3metadata(tconst['file_id_small'])        
        self.assertTrue('url' in meta)
        self.assertTrue('etag' in meta)

    # api file upload/download methods are tested in a separate suite:                
        # __initiateMultipartFileUpload__()    
        # __uploadMultipartUnit__()        
        # __finalizeMultipartFileUpload__()        
        # __singlepartFileUpload__()                        
        # multipartFileUpload()            
                        
        # __downloadFile__()
        # fileDownload()
        # multipartFileDownload()        

class TestAppSessionSemiCompactMethods(TestCase):
    '''
    Tests AppSessionSemiCompact object methods
    '''        
    @classmethod
    def setUpClass(cls):                        
        cls.api = BaseSpaceAPI(profile='unit_tests')
        # create an app session, since the client key and secret must match those of the ssn application
        cls.proj = cls.api.createProject(tconst['create_project_name'])                        
        cls.ar = cls.proj.createAppResult(cls.api, "test AppSessionSemiCompact Methods", "test AppSessionSemiCompact Methods", appSessionId="")
        cls.ssn = cls.ar.AppSession # this is an AppSessionSemiCompact instance

    def testIsInit(self):        
        self.assertEqual(self.ssn.isInit(), True)
            
    def testIsInitException(self):
        ssn = AppSessionSemiCompact.AppSessionSemiCompact()        
        with self.assertRaises(ModelNotInitializedException):
            ssn.isInit()                                      
                    
    def testCanWorkOn(self):
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test canWorkOn()", "test canWorkOn()", appSessionId="")
        self.assertEqual(ar.AppSession.canWorkOn(), True)
        ar.AppSession.setStatus(self.api, 'NeedsAttention', "Will you look into this?")
        self.assertEqual(ar.AppSession.canWorkOn(), True)
        ar.AppSession.setStatus(self.api, 'TimedOut', "This is taking forever")
        self.assertEqual(ar.AppSession.canWorkOn(), True)
        ar.AppSession.setStatus(self.api, 'Complete', "Time to wrap things up")
        self.assertEqual(ar.AppSession.canWorkOn(), False)            

    def testCanWorkOn_Aborted(self):
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test canWorkOn() Aborted", "test canWorkOn() Aborted", appSessionId="")
        self.assertEqual(ar.AppSession.canWorkOn(), True)
        ar.AppSession.setStatus(self.api, 'Aborted', "Abandon Ship!")
        self.assertEqual(ar.AppSession.canWorkOn(), False)            
    
    def setStatus(self):
        status = 'Complete'
        statusSummary = "Let's go home now"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setStatus()", "test setStatus()", appSessionId="")
        ar.AppSession.setStatus(self.api, status, statusSummary)
        self.assertEqual(ar.AppSession.Status, status)
        self.assertEqual(ar.AppSession.StatusSummary, statusSummary)
    
    def testSetStatus_CompleteStatusException(self):
        status = 'Complete'
        statusSummary = "Let's go"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setStatus() Complete exception", "test setStatus() Complete exception", appSessionId="")
        ar.AppSession.setStatus(self.api, status, statusSummary)
        status = 'Aborted'
        statusSummary = '(Too) late breaking changes'
        with self.assertRaises(AppSessionException):
            ar.AppSession.setStatus(self.api, status, statusSummary)

    def testSetStatus_AbortedStatusException(self):
        status = 'Aborted'
        statusSummary = "Let's go"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setStatus() aborted exception", "test setStatus() aborted exception", appSessionId="")
        ar.AppSession.setStatus(self.api, status, statusSummary)
        status = 'Running'
        statusSummary = "I thought everything was peachy?"
        with self.assertRaises(AppSessionException):
            ar.AppSession.setStatus(self.api, status, statusSummary)
                        
class TestAppSessionMethods(TestCase):
    '''
    Tests AppSession object methods
    '''        
    @classmethod
    def setUpClass(cls):                        
        cls.api = BaseSpaceAPI(profile='unit_tests')
        # create an app session, since the client key and secret must match those of the ssn application
        cls.proj = cls.api.createProject(tconst['create_project_name'])                        
        cls.ar = cls.proj.createAppResult(cls.api, "test AppSession Methods", "test AppSession Methods", appSessionId="")
        cls.ssn = cls.api.getAppSessionById(cls.ar.AppSession.Id) # this is an AppSession instance        

    def testIsInit(self):        
        self.assertEqual(self.ssn.isInit(), True)
            
    def testIsInitException(self):
        ssn = AppSession.AppSession()        
        with self.assertRaises(ModelNotInitializedException):
            ssn.isInit()                                      
                    
    def testCanWorkOn(self):
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test canWorkOn()", "test canWorkOn()", appSessionId="")
        ssn = self.api.getAppSessionById(ar.AppSession.Id)
        self.assertEqual(ssn.canWorkOn(), True)
        ssn.setStatus(self.api, 'NeedsAttention', "Will you look into this?")
        self.assertEqual(ssn.canWorkOn(), True)
        ssn.setStatus(self.api, 'TimedOut', "This is taking forever")
        self.assertEqual(ssn.canWorkOn(), True)
        ssn.setStatus(self.api, 'Complete', "Time to wrap things up")
        self.assertEqual(ssn.canWorkOn(), False)            

    def testCanWorkOn_Aborted(self):
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test canWorkOn() Aborted", "test canWorkOn() Aborted", appSessionId="")
        ssn = self.api.getAppSessionById(ar.AppSession.Id)
        self.assertEqual(ssn.canWorkOn(), True)
        ssn.setStatus(self.api, 'Aborted', "Abandon Ship!")
        self.assertEqual(ssn.canWorkOn(), False)            
    
    def setStatus(self):
        status = 'Complete'
        statusSummary = "Let's go home now"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setStatus()", "test setStatus()", appSessionId="")
        ssn = self.api.getAppSessionById(ar.AppSession.Id)
        ssn.setStatus(self.api, status, statusSummary)
        self.assertEqual(ssn.Status, status)
        self.assertEqual(ssn.StatusSummary, statusSummary)
    
    def testSetStatus_CompleteStatusException(self):
        status = 'Complete'
        statusSummary = "Let's go"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setStatus() Complete exception", "test setStatus() Complete exception", appSessionId="")
        ssn = self.api.getAppSessionById(ar.AppSession.Id)        
        ssn.setStatus(self.api, status, statusSummary)
        status = 'Aborted'
        statusSummary = '(Too) late breaking changes'
        with self.assertRaises(AppSessionException):
            ssn.setStatus(self.api, status, statusSummary)

    def testSetStatus_AbortedStatusException(self):
        status = 'Aborted'
        statusSummary = "Let's go"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setStatus() aborted exception", "test setStatus() aborted exception", appSessionId="")
        ssn = self.api.getAppSessionById(ar.AppSession.Id)        
        ssn.setStatus(self.api, status, statusSummary)
        status = 'Running'
        statusSummary = "I thought everything was peachy?"
        with self.assertRaises(AppSessionException):
            ssn.setStatus(self.api, status, statusSummary)
            
    def test__deserializeReferences__(self):                
        asla = AppSessionLaunchObject.AppSessionLaunchObject()
        asla.Type = 'Project'
        asla.Content = { "Id": "123", 
                    "UserOwnedBy": {"Id": "321",
                                    "Href": "v1pre3/users/321",
                                    "Name": "Jay Flatley" },
                    "Href": "v1pre3/projects/123",
                    "Name": "Project Boomtown",
                    "DataCreated": "2020-01-01T01:01:01.0000000" }
        ssn = AppSession.AppSession()
        ssn.References = [asla]
        ssn.__deserializeReferences__(self.api)
        self.assertEqual(ssn.References[0].Content.Id, "123")

class TestAppSessionLaunchObjectMethods(TestCase):
    '''
    Tests AppSessionLaunchObject object methods
    '''
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')    
    
    def test__deserializeObject__(self):
        asla = AppSessionLaunchObject.AppSessionLaunchObject()
        asla.Type = 'Project'
        asla.Content = { "Id": "123", 
                    "UserOwnedBy": {"Id": "321",
                                    "Href": "v1pre3/users/321",
                                    "Name": "Jay Flatley" },
                    "Href": "v1pre3/projects/123",
                    "Name": "Project Boomtown",
                    "DataCreated": "2020-01-01T01:01:01.0000000" }        
        asla.__deserializeObject__(self.api)
        self.assertEqual(asla.Content.Id, "123")
    
class TestAPIAppSessionMethods(TestCase):
    '''
    Tests API AppSession object methods
    '''        
    @classmethod
    def setUpClass(cls):                        
        cls.api = BaseSpaceAPI(profile='unit_tests')
        # create an app session, since the client key and secret must match those of the ssn application
        cls.proj = cls.api.createProject(tconst['create_project_name'])                        
        cls.ar = cls.proj.createAppResult(cls.api, "test API AppSession Methods", "test API AppSession Methods", appSessionId="")
        cls.ssn = cls.ar.AppSession

    def test__deserializeAppSessionResponse__(self):        
        # very similar to 2nd half of BaseAPI.__singleRequest__()
        references = [ { "Type": "Project",
                       "Href": "v1pre3/projects/321", 
                       "Content": {"Id": "321", } } ]                                          
        ssn_dict = { "ResponseStatus": {},
                     "Notifications": {}, 
                     "Response": {"Id": "123",
                                  "Href": "v1pre3/appsessions/123",
                                  "References": references, } }                                                            
        ssn = self.api.__deserializeAppSessionResponse__(ssn_dict)
        self.assertEqual(ssn.Id, "123")
        self.assertEqual(ssn.References[0].Content.Id, "321")

    def test__deserializeAppSessionResponse__ErrorCodeException(self):
        ssn_dict = { "ResponseStatus": { "ErrorCode": "666", "Message": "We are dying" } }
        with self.assertRaises(AppSessionException):
            self.api.__deserializeAppSessionResponse__(ssn_dict)    
    
    def testGetAppSessionById(self):                
        ssn = self.api.getAppSessionById(self.ssn.Id)
        self.assertEqual(ssn.Id, self.ssn.Id)

    def testGetAppSession(self):
        self.api.appSessionId = self.ssn.Id
        ssn = self.api.getAppSession()
        self.assertEqual(ssn.Id, self.ssn.Id)

    def testGetAppSessionWithId(self):
        ssn = self.api.getAppSession(self.ssn.Id)
        self.assertEqual(ssn.Id, self.ssn.Id)

    def testGetAppSessionPropertiesById(self):
        props = self.api.getAppSessionPropertiesById(self.ssn.Id)
        self.assertTrue(any((prop.Items[0].Id == self.ar.Id) for prop in props.Items if prop.Name == "Output.AppResults"))         

    def testGetAppSessionPropertiesByIdWithQp(self):
        props = self.api.getAppSessionPropertiesById(self.ssn.Id, qp({'Limit':1}))
        self.assertTrue(any((prop.Items[0].Id == self.ar.Id) for prop in props.Items if prop.Name == "Output.AppResults"))
        self.assertEqual(len(props.Items), 1)         

    def testGetAppSessionPropertyByName(self):
        prop = self.api.getAppSessionPropertyByName(self.ssn.Id, 'Output.AppResults')
        self.assertEqual(prop.Items[0].Content.Id, self.ar.Id)
        # TODO Hmm, it's odd that 'Content' is needed here but not in the prior test -- bug? difference in server response?

    def testGetAppSessionPropertyByNameWithQp(self):
        ars = self.api.getAppSessionPropertyByName(self.ssn.Id, 'Output.AppResults', qp({'Limit':1})) # Limit doesn't make much sense here
        self.assertEqual(ars.Items[0].Content.Id, self.ar.Id)
        # TODO same as test above

    def testGetAppSessionInputsById(self):
        props = self.api.getAppSessionInputsById(self.ssn.Id)
        self.assertEqual(len(props), 0)
        # TODO can't test this easily since self-created ssn don't have inputs. Add POST properties for ssns, and manually add an 'Input.Test' property, then test for it?
    
    def testGetAppSessionInputsByIdWithQp(self):
        props = self.api.getAppSessionInputsById(self.ssn.Id, qp({'Limit':1}))
        self.assertEqual(len(props), 0)
        # TODO same as test above

    def testSetAppSessionState_UpdatedStatus(self):
        status = 'Running'
        statusSummary = 'here we go, here we go'
        ssn = self.api.setAppSessionState(self.ssn.Id, status, statusSummary)
        self.assertEqual(ssn.Status, status)
        self.assertEqual(ssn.StatusSummary, statusSummary)
    
    def testSetAppSessionStateToComplete(self):
        status = 'Complete'
        statusSummary = 'things are looking good'
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setAppSessionState to " + status, "test setAppSessionState to " + status, appSessionId="")
        ssn = self.api.setAppSessionState(ar.AppSession.Id, status, statusSummary)
        self.assertEqual(ssn.Status, status)
        self.assertEqual(ssn.StatusSummary, statusSummary)

    def testSetAppSessionStateToNeedsAttention(self):
        status = 'NeedsAttention'
        statusSummary = 'things are looking shaky'
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setAppSessionState to " + status, "test setAppSessionState to " + status, appSessionId="")
        ssn = self.api.setAppSessionState(ar.AppSession.Id, status, statusSummary)
        self.assertEqual(ssn.Status, status)
        self.assertEqual(ssn.StatusSummary, statusSummary)
    
    def testSetAppSessionStateToTimedOut(self):
        status = 'TimedOut'
        statusSummary = 'things are falling behind'
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setAppSessionState to " + status, "test setAppSessionState to " + status, appSessionId="")
        ssn = self.api.setAppSessionState(ar.AppSession.Id, status, statusSummary)
        self.assertEqual(ssn.Status, status)
        self.assertEqual(ssn.StatusSummary, statusSummary)

    def testSetAppSessionStateToAborted(self):
        status = 'Aborted'
        statusSummary = 'things are looking bad'
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test setAppSessionState to " + status, "test setAppSessionState to " + status, appSessionId="")
        ssn = self.api.setAppSessionState(ar.AppSession.Id, status, statusSummary)
        self.assertEqual(ssn.Status, status)
        self.assertEqual(ssn.StatusSummary, statusSummary)
        
    def testSetAppSessionState_StatusException(self):
        status = 'PrettyMuchWorkingKindaSorta'
        statusSummary = 'tests, what tests'
        with self.assertRaises(AppSessionException):
            ssn = self.api.setAppSessionState(self.ssn.Id, status, statusSummary)

    def test__deserializeObject__Project(self):        
        type = 'Project'
        dct = { "HrefSamples": "testurl",
                "Gibberish": "more Gibberish" }
        new_obj = self.api.__deserializeObject__(dct, type)        
        self.assertEqual(new_obj.HrefSamples, "testurl")
        with self.assertRaises(AttributeError):
            self.assertEqual(new_obj.Gibberish, "more Gibberish")
    
    def test__deserializeObject__Sample(self):
        type = 'Sample'
        dct = { "SampleNumber": "123",
                "Gibberish": "more Gibberish" }
        new_obj = self.api.__deserializeObject__(dct, type)        
        self.assertEqual(new_obj.SampleNumber, 123)
        with self.assertRaises(AttributeError):
            self.assertEqual(new_obj.Gibberish, "more Gibberish")
    
    def test__deserializeObject__AppResult(self):
        type = 'AppResult'
        dct = { "Description": "Fuzzy",
                "Gibberish": "more Gibberish" }
        new_obj = self.api.__deserializeObject__(dct, type)        
        self.assertEqual(new_obj.Description, "Fuzzy")
        with self.assertRaises(AttributeError):
            self.assertEqual(new_obj.Gibberish, "more Gibberish")
    
    def test__deserializeObject__Other(self):
        type = 'Other'
        dct = { "Description": "Fuzzy",
                "Gibberish": "more Gibberish" }
        new_obj = self.api.__deserializeObject__(dct, type)        
        self.assertEqual(new_obj, dct)        
    
class TestAPICoverageMethods(TestCase):
    '''
    Tests API Coverage object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        
    def testGetIntervalCoverage(self):
        cov = self.api.getIntervalCoverage(
            Id = tconst['bam_file_id'],
            Chrom = tconst['bam_cov_chr_name'],
            StartPos = tconst['bam_cov_start_coord'],
            EndPos = tconst['bam_cov_end_coord'])        
        self.assertEqual(cov.Chrom, tconst['bam_cov_chr_name'])
        self.assertEqual(cov.StartPos, int(tconst['bam_cov_start_coord']))
        self.assertEqual(cov.EndPos, int(tconst['bam_cov_end_coord']))      

    def testGetCoverageMetaInfo(self):
        cov_meta = self.api.getCoverageMetaInfo(
            Id = tconst['bam_file_id'],
            Chrom = tconst['bam_cov_chr_name'])
        self.assertTrue(hasattr(cov_meta, 'MaxCoverage'))
        
class TestAPIVariantMethods(TestCase):
    '''
    Tests API Variant object methods
    '''        
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
    
    def testFilterVariantSet(self):        
        vars = self.api.filterVariantSet(
            Id = tconst['vcf_file_id'], 
            Chrom = tconst['vcf_chr_name'],
            StartPos = tconst['vcf_start_coord'],
            EndPos = tconst['vcf_end_coord'], )            
        self.assertEqual(vars[0].CHROM, tconst['vcf_chr_name'])
    
    def testFilterVariantWithQp(self):
        vars = self.api.filterVariantSet(
            Id = tconst['vcf_file_id'], 
            Chrom = tconst['vcf_chr_name'],
            StartPos = tconst['vcf_start_coord'],
            EndPos = tconst['vcf_end_coord'],
            Format = 'json',
            queryPars = qp({'Limit':1}) )
        self.assertEqual(vars[0].CHROM, tconst['vcf_chr_name'])
        self.assertEqual(len(vars), 1)
        
    def testFilterVariantReturnVCFString(self):        
        with self.assertRaises(NotImplementedError): # for now...
            vars = self.api.filterVariantSet(
                Id = tconst['vcf_file_id'],
                Chrom = tconst['vcf_chr_name'],
                StartPos = tconst['vcf_start_coord'],
                EndPos = tconst['vcf_end_coord'],
                Format = 'vcf')
            #self.assertEqual(type(vars), str)            
    
    def testGetVariantMeta(self):        
        hdr = self.api.getVariantMetadata(tconst['vcf_file_id'])
        self.assertTrue(hasattr(hdr, 'Metadata'))

    def testGetVariantMetaReturnVCFString(self):        
        with self.assertRaises(NotImplementedError): # for now...
            hdr = self.api.getVariantMetadata(tconst['vcf_file_id'], Format='vcf')            
            #self.assertEqual(type(hdr), str)
    
class TestAPICredentialsMethods(TestCase):
    '''
    Tests API object credentials methods
    '''        
    def setUp(self):        
        self.profile = 'unit_tests'
        self.api = BaseSpaceAPI(profile=self.profile)
        
    def test_setCredentials_AllFromProfile(self):                                                            
        creds = self.api._setCredentials(clientKey=None, clientSecret=None,
            apiServer=None, apiVersion=None, appSessionId='', accessToken='',
            profile=self.profile)
        self.assertEqual(creds['clientKey'], self.api.key)
        self.assertEqual('profile' in creds, True)
        self.assertEqual(creds['clientSecret'], self.api.secret)
        self.assertEqual(urljoin(creds['apiServer'], creds['apiVersion']), self.api.apiClient.apiServerAndVersion)
        self.assertEqual(creds['apiVersion'], self.api.version)
        self.assertEqual(creds['appSessionId'], self.api.appSessionId)
        self.assertEqual(creds['accessToken'], self.api.getAccessToken())

    def test_setCredentials_AllFromConstructor(self):                                                            
        creds = self.api._setCredentials(clientKey='test_key', clientSecret='test_secret',
            apiServer='https://www.test.server.com', apiVersion='test_version', appSessionId='test_ssn',
            accessToken='test_token', profile=self.profile)
        self.assertNotEqual(creds['clientKey'], self.api.key)
        self.assertNotEqual('profile' in creds, True)
        self.assertNotEqual(creds['clientSecret'], self.api.secret)
        self.assertNotEqual(urljoin(creds['apiServer'], creds['apiVersion']), self.api.apiClient.apiServerAndVersion)
        self.assertNotEqual(creds['apiVersion'], self.api.version)
        self.assertNotEqual(creds['appSessionId'], self.api.appSessionId)
        self.assertNotEqual(creds['accessToken'], self.api.getAccessToken())

    def test_setCredentials_MissingConfigCredsException(self):
        # Danger: if this test fails unexpectedly, the config file may not be renamed back to the original name
        # 1) mv current .basespacepy.cfg, 2) create new with new content,
        # 3) run test, 4) erase new, 5) mv current back        
        cfg = os.path.expanduser('~/.basespacepy.cfg')
        tmp_cfg = cfg + '.unittesting.donotdelete'
        shutil.move(cfg, tmp_cfg)                
        new_cfg_content = ("[" + self.profile + "]\n"
                          "accessToken=test\n"
                          "appSessionId=test\n")
        with open(cfg, "w") as f:
            f.write(new_cfg_content)
        with self.assertRaises(CredentialsException):
            creds = self.api._setCredentials(clientKey=None, clientSecret=None,
                apiServer=None, apiVersion=None, appSessionId='', accessToken='',
                profile=self.profile)
        os.remove(cfg)
        shutil.move(tmp_cfg, cfg)

    def test__setCredentials_DefaultsForOptionalArgs(self):
        # Danger: if this test fails unexpectedly, the config file may not be renamed back to the original name
        # 1) mv current .basespacepy.cfg, 2) create new with new content,
        # 3) run test, 4) erase new, 5) mv current back
        cfg = os.path.expanduser('~/.basespacepy.cfg')
        tmp_cfg = cfg + '.unittesting.donotdelete'
        shutil.move(cfg, tmp_cfg)                
        new_cfg_content = ("[" + self.profile + "]\n"                       
                          "clientKey=test\n"
                          "clientSecret=test\n"                                                    
                          "apiServer=test\n"
                          "apiVersion=test\n")                          
        with open(cfg, "w") as f:
            f.write(new_cfg_content)    
        creds = self.api._setCredentials(clientKey=None, clientSecret=None,
                apiServer=None, apiVersion=None, appSessionId='', accessToken='',
                profile=self.profile)
        self.assertEqual(creds['appSessionId'], '')
        self.assertEqual(creds['accessToken'], '')
        os.remove(cfg)
        shutil.move(tmp_cfg, cfg)        

    def test__getLocalCredentials(self):                                                            
        creds = self.api._getLocalCredentials(profile='unit_tests')
        self.assertEqual('name' in creds, True)
        self.assertEqual('clientKey' in creds, True)
        self.assertEqual('clientSecret' in creds, True)
        self.assertEqual('apiServer' in creds, True)
        self.assertEqual('apiVersion' in creds, True)
        self.assertEqual('appSessionId' in creds, True)
        self.assertEqual('accessToken' in creds, True)

    def test__getLocalCredentials_DefaultProfile(self):
        creds = self.api._getLocalCredentials(profile=self.profile)
        self.assertEqual('name' in creds, True)
        self.assertEqual('clientKey' in creds, True)
        self.assertEqual('clientSecret' in creds, True)
        self.assertEqual('apiServer' in creds, True)
        self.assertEqual('apiVersion' in creds, True)
        self.assertEqual('appSessionId' in creds, True)
        self.assertEqual('accessToken' in creds, True)

    def test__getLocalCredentials_MissingProfile(self):                                                        
        with self.assertRaises(CredentialsException):
            creds = self.api._getLocalCredentials(profile="SuperCallaFragaListic AppTastic")                

class TestAPIGenomeMethods(TestCase):
    '''
    Tests API object Genome methods
    '''        
    def setUp(self):                
        self.api = BaseSpaceAPI(profile='unit_tests')

    def testGetAvailableGenomes(self):
        genomes = self.api.getAvailableGenomes()        
        #self.assertIsInstance(g[0], GenomeV1.GenomeV1)
        self.assertIsInstance(int(genomes[0].Id), int)
        
    def testGetAvailableGenomesWithQp(self):
        genomes = self.api.getAvailableGenomes(qp({'Limit':200}))
        genome = next(gen for gen in genomes if gen.Id == tconst['genome_id'])
        self.assertTrue(genome.Id, tconst['genome_id'])        
        
    def testGetGenomeById(self):
        g = self.api.getGenomeById(tconst['genome_id'])
        self.assertEqual(g.Id, tconst['genome_id'])

class TestAPIUtilityMethods(TestCase):
    '''
    Tests utility methods of the API object
    '''
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        
    def test_validateQueryParametersDefault(self):
        self.assertEqual(self.api._validateQueryParameters(None), {})
        
    def test_validateQueryParameters(self):
        queryPars = {'Limit':10}
        self.assertEqual(self.api._validateQueryParameters( qp(queryPars) ), queryPars)
    
    def test_validateQueryParametersException(self):
        with self.assertRaises(QueryParameterException):
            self.api._validateQueryParameters({'Limit':10})

class TestQueryParametersMethods(TestCase):
    '''
    Tests QueryParameters methods
    '''
    def testGetParameterDictAndValidate(self):        
        queryp = qp({'Limit':1}, ['Limit'])
        passed = queryp.getParameterDict()        
        self.assertEqual(passed, {'Limit':1})
        self.assertEqual(queryp.validate(), None)
        
    def testNoDictException(self):
        with self.assertRaises(QueryParameterException):
            queryp = qp('test')

    def testValidateMissingRequiredParameterException(self):
        queryp = qp({'Limit':1}, ['I am required'])
        with self.assertRaises(UndefinedParameterException):
            queryp.validate()
        
    def testValidateUnknownParameterException(self):
        queryp = qp({'Crazy New Parameter':66})
        with self.assertRaises(UnknownParameterException):
            queryp.validate()
    
    def testValidateIllegalValueForKnownQpKeyException(self):
        queryp = qp({'SortBy': 'abc'})        
        with self.assertRaises(IllegalParameterException):
            queryp.validate()

class TestListResponseMethods(TestCase):
    '''
    Tests ListResponse methods
    '''
    def testConvertToObjectList(self):
        lr = ListResponse.ListResponse()
        lr.Response = ResourceList.ResourceList()
        lr.Response.Items = ['{ "Id": "123", "Href": "asdf", "UserOwnedBy": { "Id":"321" }, "TotalSize": 555 }',
                             '{ "Id": "456", "Href": "asdf", "UserOwnedBy": { "Id":"321" }, "TotalSize": 666 }',]
        objs = lr._convertToObjectList()
        self.assertEqual(objs[0]['Id'], "123")
        self.assertEqual(objs[1]['TotalSize'], 666)
        self.assertEqual(objs[0]['UserOwnedBy']['Id'], "321")

class TestAPIOAuthMethods(TestCase):
    '''
    Tests API Oauth methods
    '''
    def setUp(self):                            
        self.api = BaseSpaceAPI(profile='unit_tests')
        
    def testGetAccess_Device(self):
        proj = self.api.getProjectById(tconst['project_id'])
        resp = self.api.getAccess(proj, accessType='browse')
        self.assertTrue('device_code' in resp)

    def testGetAccess_DeviceModelNotSupportedException(self):        
        with self.assertRaises(ModelNotSupportedException):
            self.api.getAccess("test")        
    
    def testGetAccess_Web(self):
        proj = self.api.getProjectById(tconst['project_id'])
        url = self.api.getAccess(proj, accessType='browse', web=True, redirectURL='http://www.basespacepy.tv', state='working')
        self.assertTrue(url.startswith('http'))
    
    def testGetVerificationCode(self):
        resp = self.api.getVerificationCode('browse project ' + tconst['project_id'])
        self.assertTrue('device_code' in resp)
    
    def testGetWebVerificationCode(self):
        url = self.api.getWebVerificationCode('browse project ' + tconst['project_id'], redirectURL='http://www.basespacepy.tv')
        self.assertTrue(url.startswith('http'))
        self.assertTrue('state=' in url)        
    
    def testGetWebVerificationCode_WithStateParam(self):
        url = self.api.getWebVerificationCode('browse project ' + tconst['project_id'], redirectURL='http://www.basespacepy.tv', state='working')
        self.assertTrue(url.startswith('http'))
        self.assertTrue('state=working' in url)
    
    def testObtainAccessToken_DeviceApp(self):
        resp = self.api.getVerificationCode('browse project ' + tconst['project_id'])
        webbrowser.open(resp['verification_with_code_uri'])        
        time.sleep(25) # wait for user to accept oauth request
        self.assertTrue(isinstance(self.api.obtainAccessToken(resp['device_code']), str))

    @skip("Not sure how to test, since must parse auth code from redirect url - use django.test assertRedirects()?")
    def testObtainAccessToken_WebApp(self):
        with self.assertRaises(Exception):
            self.api.obtainAccessToken('123456', grantType='authorization_code', redirect_uri='http://www.basespacepy.tv')
            

    def testObtainAccessToken_WebAppRedirectURIException(self):        
        with self.assertRaises(OAuthException):
            self.api.obtainAccessToken('123456', grantType='authorization_code', redirect_uri=None)
            
    def testUpdatePrivileges_DeviceApp(self):
        resp = self.api.getVerificationCode('browse project ' + tconst['project_id'])
        webbrowser.open(resp['verification_with_code_uri'])        
        time.sleep(25) # wait for user to accept oauth request
        origToken = self.api.getAccessToken()
        self.api.updatePrivileges(resp['device_code'])
        self.assertNotEqual(self.api.getAccessToken(), origToken)
        self.assertTrue(isinstance(self.api.getAccessToken(), str))

    @skip("Not sure how to test, since must parse auth code from redirect url - use django.test assertRedirects()?")
    def testUpdatePrivileges_WebApp(self):
        with self.assertRaises(Exception):
            self.api.updatePrivileges('123456', grantType='authorization_code', redirect_uri='http://www.basespacepy.tv')            

class TestBaseSpaceAPIMethods(TestCase):
    '''
    Tests BaseSpace API constructor and attributes; all methods tested in other testcases
    '''
    def setUp(self):
        self.api = BaseSpaceAPI(profile='unit_tests')        
        
    def test__init__(self):
        creds = self.api._getLocalCredentials(profile='unit_tests')
        self.assertEqual(creds['appSessionId'], self.api.appSessionId)
        self.assertEqual(creds['clientKey'], self.api.key)
        self.assertEqual(creds['clientSecret'], self.api.secret)
        self.assertEqual(creds['apiServer'], self.api.apiServer)
        self.assertEqual(creds['apiVersion'], self.api.version)
        self.assertEqual(creds['name'], self.api.profile)
        self.assertEqual(creds['apiServer'].replace('api.',''), self.api.weburl)

class TestBaseAPIMethods(TestCase):
    '''
    Tests Base API methods
    '''
    def setUp(self):
        api = BaseSpaceAPI(profile='unit_tests')                                                    
        self.bapi = BaseAPI(api.getAccessToken(), api.apiClient.apiServerAndVersion)
        
    def test__init__(self):
        accessToken = "123"
        apiServerAndVersion = "http://api.tv"
        timeout = 50
        bapi = BaseAPI(accessToken, apiServerAndVersion, timeout)
        self.assertEqual(bapi.apiClient.apiKey, accessToken)
        self.assertEqual(bapi.apiClient.apiServerAndVersion, apiServerAndVersion)
        self.assertEqual(bapi.apiClient.timeout, timeout)

    def test__singleRequest__(self):
        # get current user
        resourcePath = '/users/current'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        user = self.bapi.__singleRequest__(UserResponse.UserResponse, resourcePath, method, queryParams, headerParams)
        self.assertTrue(hasattr(user, 'Id'))

    def test__singleRequest__WithPostData(self):
        # create a project
        resourcePath = '/projects/'        
        method = 'POST'
        queryParams = {}
        headerParams = {}
        postData = { 'Name': tconst['create_project_name'] }            
        proj = self.bapi.__singleRequest__(ProjectResponse.ProjectResponse, 
            resourcePath, method, queryParams, headerParams, postData=postData)
        self.assertEqual(proj.Name, tconst['create_project_name'])
    
    def test__singleRequest__WithForcePost(self):
        # initiate a multipart upload -- requires a POST with no post data ('force post')
        api = BaseSpaceAPI(profile='unit_tests')                                                    
        proj = api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(api, "test __singleResult__WithForcePost", "test __singleResult__WithForcePost", appSessionId="") 
        resourcePath = '/appresults/{Id}/files'        
        method = 'POST'
        resourcePath = resourcePath.replace('{Id}', ar.Id)
        queryParams = {}
        queryParams['name']          = "test file name"
        queryParams['directory']     = "test directory"
        queryParams['multipart']     = 'true' 
        headerParams                 = {}
        headerParams['Content-Type'] = 'text/plain'                        
        postData                     = None        
        file = self.bapi.__singleRequest__(FileResponse.FileResponse, resourcePath, method,
            queryParams, headerParams, postData=postData, forcePost=1)
        self.assertTrue(hasattr(file, 'Id'), 'Successful force post should return file object with Id attribute here')                            

    def test__singleRequest__Verbose(self):
        # get current user
        resourcePath = '/users/current'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        user = self.bapi.__singleRequest__(UserResponse.UserResponse, resourcePath, method, queryParams, headerParams, verbose=True)
        self.assertTrue(hasattr(user, 'Id'))

    @skip("Not sure how to test this, requires no response from api server")
    def test__singleRequest__NoneResponseException(self):
        pass
    
    def test__singleRequest__ErrorResponseException(self):
        # malformed resoucePath, BadRequest Error and Message in response
        resourcePath = '/users/curren'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        with self.assertRaises(ServerResponseException):
            self.bapi.__singleRequest__(UserResponse.UserResponse, resourcePath, method, queryParams, headerParams)

    def test__singleRequest__UnrecognizedPathResponseException(self):
        # malformed resoucePath, Message in response is 'not recognized path' (no error code)
        resourcePath = '/users/current/run'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        with self.assertRaises(ServerResponseException):
            self.bapi.__singleRequest__(UserResponse.UserResponse, resourcePath, method, queryParams, headerParams)

    def test__listRequest__(self):
        # get current user
        resourcePath = '/users/current/runs'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        runs = self.bapi.__listRequest__(Run.Run, resourcePath, method, queryParams, headerParams)
        self.assertTrue(isinstance(runs, list))
        self.assertTrue(hasattr(runs[0], "Id"))

    def test__listRequest__Verbose(self):
        # get current user
        resourcePath = '/users/current/runs'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        runs = self.bapi.__listRequest__(Run.Run, resourcePath, method, queryParams, headerParams, verbose=True)
        self.assertTrue(isinstance(runs, list))
        self.assertTrue(hasattr(runs[0], "Id"))

    @skip("Not sure how to test this, requires no response from api server")
    def test__listRequest__NoneResponseException(self):
        pass
    
    def test__listRequest__ErrorResponseException(self):
        # Unauthorized - use nonsense acccess token
        api = BaseSpaceAPI(profile='unit_tests')                                                    
        bapi = BaseAPI(AccessToken="123123123123123123", apiServerAndVersion=api.apiClient.apiServerAndVersion)

        resourcePath = '/users/current/uns'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        with self.assertRaises(ServerResponseException):
            bapi.__listRequest__(Run.Run, resourcePath, method, queryParams, headerParams)

    def test__listRequest__UnrecognizedPathResponseException(self):
        # malformed resoucePath, not recognized path message
        resourcePath = '/users/current/uns'        
        method = 'GET'        
        queryParams = {}
        headerParams = {}
        with self.assertRaises(ServerResponseException):
            self.bapi.__listRequest__(Run.Run, resourcePath, method, queryParams, headerParams)

    @skip("Don't need to test curl itself if we can achieve the functionality we need without direct curls")
    def test__makeCurlRequest__(self):
        api = BaseSpaceAPI(profile='unit_tests')
        scope = 'browse project ' + tconst['project_id']
        postData = [('client_id', api.key), ('scope', scope),('response_type', 'device_code')]
        resp = self.bapi.__makeCurlRequest__(postData, api.apiClient.apiServerAndVersion + deviceURL)        
        self.assertTrue('device_code' in resp)

    @skip("Not sure how to test this, requires no response from api server")
    def test__makeCurlRequest__NoneResponseException(self):
        pass

    @skip("Don't need to test curl itself if we can achieve the functionality we need without direct curls")
    def test__makeCurlRequest__ServerErrorException(self):
        # gibberish client id causes server error
        api = BaseSpaceAPI(profile='unit_tests')
        scope = 'browse project ' + tconst['project_id']
        postData = [('client_id', 'gibberish'), ('scope', scope),('response_type', 'device_code')]
        with self.assertRaises(ServerResponseException):
            self.bapi.__makeCurlRequest__(postData, api.apiClient.apiServerAndVersion + deviceURL)        

    def testGetTimeout(self):
        self.assertEqual(self.bapi.getTimeout(), 10)
        
    def testSetTimeout(self):
        self.bapi.setTimeout(20) 
        self.assertEqual(self.bapi.apiClient.timeout, 20)
        
    def testGetAccessToken(self):
        api = BaseSpaceAPI(profile='unit_tests')
        self.assertEqual(self.bapi.getAccessToken(), api.apiClient.apiKey)
        
    def testSetAccessToken(self):
        self.bapi.setAccessToken("abc")
        self.assertEqual(self.bapi.getAccessToken(), "abc")

class TestAPIClientMethods(TestCase):
    '''
    Tests APIClient methods
    '''
    def setUp(self):
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.apiClient = APIClient(self.api.apiClient.apiKey, self.api.apiClient.apiServerAndVersion)                                                    
    
    def test__init__(self):
        accessToken = "abc"
        apiServerAndVersion = "http://basesinspaces.tv"
        timeout = 20
        apiClient = APIClient(AccessToken=accessToken, apiServerAndVersion=apiServerAndVersion, timeout=timeout)
        self.assertEqual(accessToken, apiClient.apiKey)                                                    
        self.assertEqual(apiServerAndVersion, apiClient.apiServerAndVersion)
        self.assertEqual(timeout, apiClient.timeout)

    def test__forcePostCall__(self):
        # initiate a multipart upload -- requires a POST with no post data ('force post')
        # all method params are required for success in this example - resourcePath, headerParams, and postData(queryParams                                                        
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test__forcePostCall__", "test__forcePostCall__", appSessionId="") 
        
        resourcePath = '/appresults/{Id}/files'
        resourcePath = resourcePath.replace('{Id}', ar.Id)
        queryParams = {}
        queryParams['name'] = "test file name"
        queryParams['directory'] = "test directory"
        queryParams['multipart'] = 'true' 
        headerParams = {}
        headerParams['Content-Type'] = 'text/plain'
        # normally added by callAPI()
        headerParams['Authorization'] = 'Bearer ' + self.apiClient.apiKey                                    

        jsonResp = self.apiClient.__forcePostCall__(resourcePath=self.apiClient.apiServerAndVersion + resourcePath, postData=queryParams, headers=headerParams)    
        dictResp = json.loads(jsonResp)
        self.assertTrue('Response' in dictResp, 'Successful force post should return json with Response attribute: ' + str(dictResp))       
        self.assertTrue('Id' in dictResp['Response'], 'Successful force post should return json with Response with Id attribute: ' + str(dictResp))        

    def test__putCall__(self):
        # upload a part of a multipart upload (the only PUT call in BaseSpacePy, for now)
        testDir = "test__putCall__"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test__putCall__", "test__putCall__", appSessionId="")
        file = self.api.__initiateMultipartFileUpload__(
            resourceType = 'appresults',
            resourceId = ar.Id,
            fileName = os.path.basename(tconst['file_small_upload']),            
            directory = testDir,
            contentType = tconst['file_small_upload_content_type'])
        with open(tconst['file_small_upload']) as fp:
            out = fp.read()
            md5 = hashlib.md5(out).digest().encode('base64')
                        
        method                       = 'PUT'
        resourcePath                 = '/files/{Id}/parts/{partNumber}'
        resourcePath                 = resourcePath.replace('{Id}', file.Id)
        resourcePath                 = resourcePath.replace('{partNumber}', str(1))        
        headerParams                 = {'Content-MD5': md5}
        transFile                    = tconst['file_small_upload']
        putResp = self.apiClient.__putCall__(resourcePath=self.apiClient.apiServerAndVersion + resourcePath, headers=headerParams, transFile=transFile)
        #print "RESPONSE is: " + putResp        
        jsonResp =  putResp.split()[-1] # normally done in callAPI()
        dictResp = json.loads(jsonResp)
        self.assertTrue('Response' in dictResp, 'Successful force post should return json with Response attribute: ' + str(dictResp))       
        self.assertTrue('ETag' in dictResp['Response'], 'Successful force post should return json with Response with Id attribute: ' + str(dictResp))                                                                    

    def testCallAPI_GET(self):   
        # get current user uses GET                                 
        resourcePath = '/users/current'        
        method = 'GET'        
        queryParams = {}
        #headerParams = {}
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=None)#, headerParams=None, forcePost=False)
        self.assertTrue('Response' in dictResp, 'response is: ' + str(dictResp))       
        self.assertTrue('Id' in dictResp['Response'])                                                                    
        
    @skip('There are no GET calls in the BaseSpace API that require headerParams')
    def testCallAPI_GETwithHeaderParams(self):
        pass
    
    def testCallAPI_POST(self):
        # create a project uses POST
        resourcePath            = '/projects/'        
        method                  = 'POST'
        queryParams             = {}
        #headerParams            = {}
        postData                = {}
        postData['Name']        = tconst['create_project_name']        
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=postData)#, headerParams=None, forcePost=False)
        self.assertTrue('Response' in dictResp)
        self.assertTrue('Id' in dictResp['Response'])

    def testCallAPI_POSTwithHeaderAndQueryParams(self):
        # single part file upload uses POST with required qp and hdrs        
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test upload", "test upload", appSessionId="")                        
        testDir = "testCallAPI_POSTwithHeaderAndQueryParams"
        fileName = os.path.basename(tconst['file_small_upload'])
        localPath=tconst['file_small_upload']
        
        method = 'POST'
        resourcePath = '/appresults/{Id}/files'        
        resourcePath                 = resourcePath.replace('{Id}', ar.Id)
        queryParams                  = {}
        queryParams['name']          = fileName
        queryParams['directory']     = testDir 
        headerParams                 = {}
        headerParams['Content-Type'] = tconst['file_small_upload_content_type']                
        postData                     = open(localPath).read()
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=postData, headerParams=headerParams)#, forcePost=False)                
        self.assertTrue('Response' in dictResp)
        self.assertTrue('Id' in dictResp['Response'])        
        self.assertEqual(dictResp['Response']['Path'], os.path.join(testDir, fileName))

    def testCallAPI_ForcePOST(self):
        # initiate a multipart upload -- requires a POST with no post data ('force post')
        # all method params are required for success in this example - resourcePath, headerParams, and postData(queryParams                                                        
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "test__forcePostCall__", "test__forcePostCall__", appSessionId="") 
        
        method = 'POST'
        resourcePath = '/appresults/{Id}/files'
        resourcePath = resourcePath.replace('{Id}', ar.Id)
        queryParams = {}
        queryParams['name'] = "test file name"
        queryParams['directory'] = "test directory"
        queryParams['multipart'] = 'true' 
        headerParams = {}
        headerParams['Content-Type'] = 'text/plain'
        postData = None
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=postData, headerParams=headerParams, forcePost=True)
        self.assertTrue('Response' in dictResp, 'Successful force post should return json with Response attribute: ' + str(dictResp))       
        self.assertTrue('Id' in dictResp['Response'], 'Successful force post should return json with Response with Id attribute: ' + str(dictResp))        

    def testCallAPI_PUT(self):
        # upload a part of a multipart upload (the only PUT call in BaseSpacePy, for now)
        testDir = "testCallAPI_PUT"
        proj = self.api.createProject(tconst['create_project_name'])                        
        ar = proj.createAppResult(self.api, "testCallAPI_PUT", "testCallAPI_PUT", appSessionId="")
        file = self.api.__initiateMultipartFileUpload__(
            resourceType = 'appresults',
            resourceId = ar.Id,
            fileName = os.path.basename(tconst['file_small_upload']),            
            directory = testDir,
            contentType = tconst['file_small_upload_content_type'])
        with open(tconst['file_small_upload']) as fp:
            out = fp.read()
            md5 = hashlib.md5(out).digest().encode('base64')
                        
        method                       = 'PUT'
        resourcePath                 = '/files/{Id}/parts/{partNumber}'
        resourcePath                 = resourcePath.replace('{Id}', file.Id)
        resourcePath                 = resourcePath.replace('{partNumber}', str(1))        
        headerParams                 = {'Content-MD5': md5}
        queryParams                  = {} # not used for PUT calls
        transFile                    = tconst['file_small_upload']
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=transFile, headerParams=headerParams)
        self.assertTrue('Response' in dictResp, 'Successful force post should return json with Response attribute: ' + str(dictResp))       
        self.assertTrue('ETag' in dictResp['Response'], 'Successful force post should return json with Response with Id attribute: ' + str(dictResp))                                                                    

    def testCallAPI_DELETE(self):        
        method                       = 'DELETE'
        resourcePath                 = ''        
        queryParams                  = {}        
        with self.assertRaises(NotImplementedError):
            dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=None)

    def testCallAPI_UnrecognizedRESTmethodException(self):
        method                       = 'TAKEOVERTHEWORLD'
        resourcePath                 = ''        
        queryParams                  = {}        
        with self.assertRaises(RestMethodException):
            dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=None)

    def testCallAPI_HandleHttpError_ForGET(self):
        # bad access token throws 401 Error and HTTPError exception by urllib2; get current user uses GET                                 
        self.apiClient.apiKey = 'badtoken'
        resourcePath = '/users/current'        
        method = 'GET'        
        queryParams = {}
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=None)
        self.assertTrue('ResponseStatus' in dictResp, 'response is: ' + str(dictResp))       
        self.assertTrue('ErrorCode' in dictResp['ResponseStatus'])
        self.assertTrue('Message' in dictResp['ResponseStatus'])
        self.assertEqual(dictResp['ResponseStatus']['Message'], 'Unauthorized')

    def testCallAPI_HandleHttpError_ForPOST(self):
        # bad access token throws 401 Error and HTTPError exception by urllib2;  create a project uses POST                                 
        self.apiClient.apiKey = 'badtoken'        
        resourcePath            = '/projects/'        
        method                  = 'POST'
        queryParams             = {}
        postData                = {}
        postData['Name']        = tconst['create_project_name']        
        dictResp = self.apiClient.callAPI(resourcePath, method, queryParams, postData=postData)
        self.assertTrue('ResponseStatus' in dictResp, 'response is: ' + str(dictResp))       
        self.assertTrue('ErrorCode' in dictResp['ResponseStatus'])
        self.assertTrue('Message' in dictResp['ResponseStatus'])
        self.assertEqual(dictResp['ResponseStatus']['Message'], 'Unauthorized')

    @skip('Not sure how to cause json returned from server to be malformed, in order to cause an exception in json parsing')
    def testCallAPI_JsonParsingException(self):
        pass

    def testDeserialize_ClassObjClass_String(self):
        obj = "test"
        objClass = str
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)
        
    def testDeserialize_ClassObjClass_Integer(self):
        obj = 123
        objClass = int
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)

    def testDeserialize_ClassObjClass_Boolean(self):
        obj = True
        objClass = bool
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)

    def testDeserialize_ClassObjClass_Float(self):
        obj = 1.23
        objClass = float
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)
        
    def testDeserialize_StringObjClass_String(self):
        obj = "test"
        objClass = 'str'
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)

    def testDeserialize_StringObjClass_Integer(self):
        obj = 123
        objClass = 'int'
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)

    def testDeserialize_StringObjClass_Boolean(self):
        obj = True
        objClass = 'bool'
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)

    def testDeserialize_StringObjClass_Float(self):
        obj = 1.23
        objClass = 'float'
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out, obj)

    def testDeserialize_ClassObjClass_Project(self):
        obj = {"Id":"123"}
        objClass = Project.Project
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.Id, "123")

    # not testing passing in an unknown class
    
    def testDeserialize_StringObjClass_Project(self):
        obj = {"Id":"123"}
        objClass = "Project"
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.Id, "123")

    def testDeserialize_StringObjClass_File(self):
        obj = {"Id":"123"}
        objClass = "File"
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.Id, "123")

    # not testing passing in an unknown class

    def testDeserialize_ClassObjClass_DynamicType(self):        
        obj = { 'ResponseStatus': 'test',
                'Response': { # DynamicType
                    # MultiValueAppResultList                             
                    'Type': 'appresult[]',                                     
                    'DisplayedCount': 10,
                    },               
                'Notifications': ''
              }
        objClass = MultiValuePropertyResponse.MultiValuePropertyResponse
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.Response.DisplayedCount, 10)

    # not testing passing in an unrecognized dynamic type - should warn    
        
    def testDeserialize_ClassObjClass_List(self):
        obj = { 'CHROM': 'chr3',                 
                'ID': ['1', '2', '3'] }  # 'list<Str>'
        objClass = Variant.Variant
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.ID[0], '1')

    def testDeserialize_ClassObjClass_ListOfDynamicTypes(self):
        obj = { 'Items': [  # 'list<DynamicType>',
                          {'Type': 'string', 'Name': 'teststring'}, # PropertyString
                          {'Type': 'project', 'Name': 'testproject'}, # PropertyProject
                          ], }                             
        objClass = PropertyList.PropertyList
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.Items[0].Name, 'teststring')
        self.assertEqual(out.Items[1].Name, 'testproject')
        
    def testDeserialize_ClassObjClass_ListOfLists(self):
        obj = { 'Items': [  #'listoflists<PropertyMapKeyValues>',
                          [ {'Key': 'testA1'}, {'Key': 'testA2'}], # PropertyMapKeyValues
                          [ {'Key': 'testB1'}, {'Key': 'testB2'}], # PropertyMapKeyValues
                          ], }
        objClass = PropertyMaps.PropertyMaps
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.Items[0][0].Key, 'testA1')
        self.assertEqual(out.Items[1][1].Key, 'testB2')

    def testDeserialize_ClassObjClass_Dict(self):
        obj = { 'INFO': 'test' } # dict    
        objClass = Variant.Variant
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.INFO, 'test')
    
    def testDeserialize_ClassObjClass_Datetime(self):
        obj = { 'DateCreated': '2013-10-03T19:40:26.0000000' } # datetime    
        objClass = Run.Run
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.DateCreated.year, 2013)

    def testDeserialize_ClassObjClass_Recursion(self):
        obj = { 'UserOwnedBy': { 'Id': '123' } }
        objClass = Project.Project
        out = self.apiClient.deserialize(obj, objClass)
        self.assertEqual(out.UserOwnedBy.Id, '123')

class TestBillingAPIMethods(TestCase):
    '''
    Tests BillingAPI methods
    '''
    @skip('Test not written yet')
    def test__init__(self):
        pass
    
class TestQueryParameterPurchasedProductMethods(TestCase):
    '''
    Tests QueryParameterPurchasedProduct methods
    '''
    @skip('Test not written yet')
    def test__init__(self):
        pass


#if __name__ == '__main__':   
#    main()         # unittest.main()
large_file_transfers = TestSuite([
    TestLoader().loadTestsFromTestCase( TestAPIFileUploadMethods_LargeFiles ),
    TestLoader().loadTestsFromTestCase( TestAPIFileDownloadMethods_LargeFiles ),
    TestLoader().loadTestsFromTestCase( TestMultipartFileTransferMethods ), ])                                  

small_file_transfers = TestSuite([
    TestLoader().loadTestsFromTestCase(TestFileDownloadMethods),
    TestLoader().loadTestsFromTestCase(TestAPIFileUploadMethods_SmallFiles),
    TestLoader().loadTestsFromTestCase(TestAPIFileDownloadMethods_SmallFiles), ])

runs_users_files = TestSuite([
    TestLoader().loadTestsFromTestCase(TestRunMethods),
    TestLoader().loadTestsFromTestCase(TestAPIRunMethods),
    TestLoader().loadTestsFromTestCase(TestUserMethods),
    TestLoader().loadTestsFromTestCase(TestAPIUserMethods),
    TestLoader().loadTestsFromTestCase(TestFileMethods),
    TestLoader().loadTestsFromTestCase(TestAPIFileMethods), ])                                                      

samples_appresults_projects = TestSuite([
    TestLoader().loadTestsFromTestCase(TestSampleMethods),
    TestLoader().loadTestsFromTestCase(TestAPISampleMethods),
    TestLoader().loadTestsFromTestCase(TestAppResultMethods),
    TestLoader().loadTestsFromTestCase(TestAPIAppResultMethods),
    TestLoader().loadTestsFromTestCase(TestProjectMethods),
    TestLoader().loadTestsFromTestCase(TestAPIProjectMethods), ])

appsessions = TestSuite([
    TestLoader().loadTestsFromTestCase(TestAppSessionSemiCompactMethods),
    TestLoader().loadTestsFromTestCase(TestAppSessionMethods),
    TestLoader().loadTestsFromTestCase(TestAppSessionLaunchObjectMethods),
    TestLoader().loadTestsFromTestCase(TestAPIAppSessionMethods), ])

cov_variant = TestSuite([
    TestLoader().loadTestsFromTestCase(TestAPICoverageMethods),
    TestLoader().loadTestsFromTestCase(TestAPIVariantMethods), ])

cred_genome_util_lists = TestSuite([
    TestLoader().loadTestsFromTestCase(TestAPICredentialsMethods),
    TestLoader().loadTestsFromTestCase(TestAPIGenomeMethods),
    TestLoader().loadTestsFromTestCase(TestAPIUtilityMethods),
    TestLoader().loadTestsFromTestCase(TestQueryParametersMethods),
    TestLoader().loadTestsFromTestCase(TestListResponseMethods), ])

oauth = TestSuite([
    TestLoader().loadTestsFromTestCase(TestAPIOAuthMethods), ])

basespaceapi_baseapi_apiclient = TestSuite([
    TestLoader().loadTestsFromTestCase(TestBaseSpaceAPIMethods),
    TestLoader().loadTestsFromTestCase(TestBaseAPIMethods),
    TestLoader().loadTestsFromTestCase(TestAPIClientMethods), ])

billing_qppp = TestSuite([
    TestLoader().loadTestsFromTestCase(TestBillingAPIMethods),
    TestLoader().loadTestsFromTestCase(TestQueryParameterPurchasedProductMethods), ])


if __name__ == "__main__":
    tests = []

    if(len(sys.argv) == 1):
        # to test all test cases:
        tests.extend([ 
              small_file_transfers, 
              runs_users_files, 
              samples_appresults_projects,
              appsessions, 
              cred_genome_util_lists,
              cov_variant, 
              basespaceapi_baseapi_apiclient,
              billing_qppp,
        ])
        #tests.append(oauth) # these tests will open a web browser and clicking 'Accept' (also requires BaseSpace login)
        tests.append(large_file_transfers) # these tests may take tens of minutes to complete
    else:
        # to test individual test cases: 
        for t in sys.argv[1:]:
            tests.append( TestLoader().loadTestsFromTestCase( eval(t) ) )
    TextTestRunner(verbosity=2).run( TestSuite(tests) )
