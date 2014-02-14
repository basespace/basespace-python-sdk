import unittest
import os
import sys
from tempfile import mkdtemp
import shutil
import urlparse
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import *
from BaseSpacePy.model import *
from BaseSpacePy.model.MultipartFileTransfer import Utils
from BaseSpacePy.model.QueryParameters import QueryParameters as qp



# Dependencies:
# 1. Create a profile named 'unit_tests' in ~/.basespacepy.cfg that has the credentials for an app on https://portal-hoth.illumina.com; there should also be a 'DEFALT' profile in the config file
# 2. Import the following data from Public Data on cloud-hoth.illumina.com:
#    from Public Dataset 'B. cereus': Project name 'BaseSpaceDemo' (Id 596596), and Run name 'BacillusCereus' (Id 555555)

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
           'file_small_upload_md5' : 'ff88b8bdbb86f219d19a22a3a0795429',
           'file_large_upload_md5' : '9267236a2d870da1d4cb73868bb51b35',
           'create_project_name': 'Python SDK Unit Test Data',
           # for runs, genomes, projects, samples, appresults 
           'run_id': '555555', # public data B. cereus Run
           'run_name': 'BacillusCereus',
           'run_property_samples_0_name': 'BC_1',        
           'run_file_0_name': 'RTAComplete.txt',
           'run_sample_0_name': 'BC_1',           
           'genome_id': '1',           
           'project_id': '596596',
           'project_appresult_0_id': '1213212',
           'project_property_count': 0, 
           'sample_id': '855855',
           'sample_property_0_id': '555555',
           'sample_file_0_id': '9895905',
           'appresult_id': '1213212',
           'appresult_file_0_id': '9895886',
           'appresult_property_0_id': '855855',
          }

class TestFileDownloadMethods(unittest.TestCase):
    '''
    Tests methods of File objects
    '''
    def setUp(self):        
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.file = self.api.getFileById(tconst['file_id_small'])
        self.temp_dir = mkdtemp()    
            
    def tearDown(self):
        shutil.rmtree(self.temp_dir) 
        
    def test_file_basic_download(self):
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
        
    def test_file_small_download_with_directory(self):
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
        
    def test_file_byte_range_download(self):
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

class TestAPIUploadMethods(unittest.TestCase):
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

    def test_small_upload(self):
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

#    @unittest.skip('large upload')
    def test_large_upload(self):
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

#    @unittest.skip('large upload')
    def test_multipart_upload(self):
        testDir = "testMultipartUploadDir"
        fileName = os.path.basename(tconst['file_large_upload']) 
        myFile = self.api.multipartFileUpload(
            Id=self.ar.Id,
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

    def test_small_part_size_multipart_upload_exception(self):
        with self.assertRaises(UploadPartSizeException):
            myFile = self.api.multipartFileUpload(
                Id=self.ar.Id,
                localPath=tconst['file_large_upload'], 
                fileName=os.path.basename(tconst['file_large_upload']), 
                directory="",                          
                contentType=tconst['file_large_upload_content_type'],            
                partSize=5, # MB, chunk size                        
                )

    def test_large_part_size_multipart_upload_exception(self):
        with self.assertRaises(UploadPartSizeException):
            myFile = self.api.multipartFileUpload(
                Id=self.ar.Id,
                localPath=tconst['file_large_upload'], 
                fileName=os.path.basename(tconst['file_large_upload']), 
                directory="",                          
                contentType=tconst['file_large_upload_content_type'],            
                partSize=26, # MB, chunk size                        
                )

    def test_small_upload_download(self):            
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

#    @unittest.skip('large upload and download')
    def test_large_upload_download(self):            
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
 
class TestAPIDownloadMethods(unittest.TestCase):
    '''
    Tests single and multi-part download methods
    '''
    def setUp(self):        
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.temp_dir = mkdtemp()    
            
    def tearDown(self):
        shutil.rmtree(self.temp_dir) 
        
    def test_small_download(self):
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

    def test_small_download_with_directory(self):
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

#    @unittest.skip('large download')
    def test_large_download(self):
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

#    @unittest.skip('large download')
    def test_large_download_with_directory(self):
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

    def test_byte_range_download(self):
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

    def test_large_byte_range_download_exception(self):
        with self.assertRaises(ByteRangeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1,10000001]            
                )        

    def test_misordered_byte_range_download_exception(self):
        with self.assertRaises(ByteRangeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1000, 1]            
                )

    def test_partial_byte_range_download_exception(self):
        with self.assertRaises(ByteRangeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1000]            
                )

    def test_small_multipartDownload(self):
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

#    @unittest.skip('large download')
    def test_large_multipartDownload(self):
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

    def test_multipartDownload_with_directory(self):
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

    def test_multipartDownload_via_temp_file(self):
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

    def test_multipartDownload_via_temp_file_with_directory(self):
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

class TestAppResultMethods(unittest.TestCase):
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
        
    # not testing getReferencedSamplesIds() or getReferencedSamples since References are deprecated
    
    def testGetFiles(self):
        files = self.appResult.getFiles(self.api)        
        self.assertEqual(files[0].Id, tconst['appresult_file_0_id'])

    def testGetFilesWithQp(self):
        files = self.appResult.getFiles(self.api, qp({'Limit':1}))        
        self.assertEqual(files[0].Id, tconst['appresult_file_0_id'])
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

class TestAPIAppResultMethods(unittest.TestCase):
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
        self.assertEqual(props.Items[0].Items[0].Id, tconst['appresult_property_0_id'])
        
    def testGetAppResultPropertiesByIdWithQp(self):
        props = self.api.getAppResultPropertiesById(tconst['appresult_id'], qp({'Limit':1}))
        self.assertEqual(props.Items[0].Items[0].Id, tconst['appresult_property_0_id']) 
        self.assertEqual(len(props.Items), 1)
            
    def testGetAppResultFiles(self):
        files = self.api.getAppResultFiles(tconst['appresult_id'])        
        self.assertEqual(files[0].Id, tconst['appresult_file_0_id'])
        
    def testGetAppResultFilesWithQp(self):
        files = self.api.getAppResultFiles(tconst['appresult_id'], qp({'Limit':1}))        
        self.assertEqual(files[0].Id, tconst['appresult_file_0_id'])
        self.assertEqual(len(files), 1)    

    def testGetAppResultsByProject(self):
        appresults = self.api.getAppResultsByProject(tconst['project_id'])
        self.assertEqual(appresults[0].Id, tconst['project_appresult_0_id'])
        
    def testGetAppResultsByProjectWithQp(self):
        appresults = self.api.getAppResultsByProject(tconst['project_id'], qp({'Limit':1}))
        self.assertEqual(appresults[0].Id, tconst['project_appresult_0_id'])
        self.assertEqual(len(appresults), 1)
        
    def testGetAppResultsByProjectWithStatusesArg(self):
        appresults = self.api.getAppResultsByProject(tconst['project_id'], statuses=['complete'])
        self.assertEqual(appresults[0].Id, tconst['project_appresult_0_id'])
        
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
        url = urlparse.urlparse(self.api.apiServer)
        newApiServer = url.scheme + "://" + url.netloc
        new_api = BaseSpaceAPI(self.api.key, self.api.secret, newApiServer, 
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
    
class TestRunMethods(unittest.TestCase):
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
        self.assertEqual(rf[0].Name, tconst['run_file_0_name'])
        
    def testRunGetFilesWithQp(self):
        rf = self.run.getFiles(self.api, qp({'Limit':200}))
        self.assertEqual(rf[0].Name, tconst['run_file_0_name'])
        self.assertEqual(len(rf), 200)

    def testRunSamples(self):
        rs = self.run.getSamples(self.api)        
        self.assertEqual(rs[0].Name, tconst['run_sample_0_name'])
        
    def testRunSamplesWithQp(self):
        rs = self.run.getSamples(self.api, qp({'Limit':1}))
        self.assertEqual(rs[0].Name, tconst['run_sample_0_name'])
        self.assertEqual(len(rs), 1)

class TestAPIRunMethods(unittest.TestCase):
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
        self.assertEqual(rf.Name, tconst['run_name'])
        
    def testGetRunByIdWithQp(self):                                                    
        rf = self.api.getRunById(tconst['run_id'], qp({'Limit':1})) # limit doesn't make much sense here            
        self.assertEqual(rf.Name, tconst['run_name'])
        
    def testGetRunPropertiesById(self):                                                    
        rp = self.api.getRunPropertiesById(tconst['run_id'])        
        self.assertEqual(rp.Items[0].Items[0].Name, tconst['run_property_samples_0_name'])
        
    def testGetRunPropertiesByIdWithQp(self):                                                    
        rp = self.api.getRunPropertiesById(tconst['run_id'], qp({'Limit':1}))
        self.assertEqual(len(rp.Items), 1)        
        self.assertEqual(rp.Items[0].Items[0].Name, tconst['run_property_samples_0_name'])
    
    def testGetRunFilesById(self):                                                    
        rf = self.api.getRunFilesById(tconst['run_id'])        
        self.assertEqual(rf[0].Name, tconst['run_file_0_name'])
        
    def testGetRunFilesByIdWithQp(self):
        rf = self.api.getRunFilesById(tconst['run_id'], qp({'Limit':1}))
        self.assertEqual(len(rf), 1)
        self.assertEqual(rf[0].Name, tconst['run_file_0_name'])

    def testRunSamplesById(self):
        rs = self.api.getRunSamplesById(tconst['run_id'])        
        self.assertEqual(rs[0].Name, tconst['run_sample_0_name'])
        
    def testRunSamplesByIdWithQp(self):
        rs = self.api.getRunSamplesById(tconst['run_id'], qp({'Limit':1}))
        self.assertEqual(rs[0].Name, tconst['run_sample_0_name'])
        self.assertEqual(len(rs), 1)

class TestSampleMethods(unittest.TestCase):
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
        
    # not testing getReferencedAppResults() since References are deprecated
    
    def testGetFiles(self):
        files = self.sample.getFiles(self.api)        
        self.assertEqual(files[0].Id, tconst['sample_file_0_id'])

    def testGetFilesWithQp(self):
        files = self.sample.getFiles(self.api, qp({'Limit':1}))        
        self.assertEqual(files[0].Id, tconst['sample_file_0_id'])
        self.assertEqual(len(files), 1)

class TestAPISampleMethods(unittest.TestCase):
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
        self.assertEqual(props.Items[0].Items[0].Id, tconst['sample_property_0_id'])

    def testGetSamplePropertiesByIdWithQp(self):
        props = self.api.getSamplePropertiesById(tconst['sample_id'], qp({'Limit':1}))
        self.assertEqual(props.Items[0].Items[0].Id, tconst['sample_property_0_id'])
        self.assertEqual(len(props.Items), 1)

class TestProjectMethods(unittest.TestCase):
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
        self.assertEqual(appresults[0].Id, tconst['project_appresult_0_id'])
            
    def testGetAppResultsWithOptionalArgs(self):
        appresults = self.project.getAppResults(self.api, qp({'Limit':1}), statuses=['complete'])
        self.assertEqual(appresults[0].Id, tconst['project_appresult_0_id'])
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
        url = urlparse.urlparse(self.api.apiServer)
        newApiServer = url.scheme + "://" + url.netloc
        new_api = BaseSpaceAPI(self.api.key, self.api.secret, newApiServer, 
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
        
class TestAPIProjectMethods(unittest.TestCase):
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
        self.assertEqual(props.TotalCount, tconst['project_property_count'])               

    def testGetProjectPropertiesByIdWithQp(self):
        props = self.api.getProjectPropertiesById(tconst['project_id'], qp({'Limit':1}))         
        self.assertEqual(props.TotalCount, tconst['project_property_count'])      
        # test project has no properties, so can't test Limit

    def testGetProjectByUser(self):
        projects = self.api.getProjectByUser()        
        self.assertTrue(hasattr(projects[0], 'Id'))
        
    def testGetProjectByUserWithQp(self):
        projects = self.api.getProjectByUser(qp({'Limit':1}))        
        self.assertTrue(hasattr(projects[0], 'Id'))        

class TestAPICredentialsMethods(unittest.TestCase):
    '''
    Tests API object credentials methods
    '''        
    def setUp(self):        
        self.profile = 'unit_tests'
        self.api = BaseSpaceAPI(profile=self.profile)

    def test__set_credentials_all_from_profile(self):                                                            
        creds = self.api._set_credentials(clientKey=None, clientSecret=None,
            apiServer=None, apiVersion=None, appSessionId='', accessToken='',
            profile=self.profile)
        self.assertEqual(creds['clientKey'], self.api.key)
        self.assertEqual('profile' in creds, True)
        self.assertEqual(creds['clientSecret'], self.api.secret)
        self.assertEqual(urlparse.urljoin(creds['apiServer'], creds['apiVersion']), self.api.apiServer)
        self.assertEqual(creds['apiVersion'], self.api.version)
        self.assertEqual(creds['appSessionId'], self.api.appSessionId)
        self.assertEqual(creds['accessToken'], self.api.getAccessToken())

    def test__set_credentials_all_from_constructor(self):                                                            
        creds = self.api._set_credentials(clientKey='test_key', clientSecret='test_secret',
            apiServer='https://www.test.server.com', apiVersion='test_version', appSessionId='test_ssn',
            accessToken='test_token', profile=self.profile)
        self.assertNotEqual(creds['clientKey'], self.api.key)
        self.assertNotEqual('profile' in creds, True)
        self.assertNotEqual(creds['clientSecret'], self.api.secret)
        self.assertNotEqual(urlparse.urljoin(creds['apiServer'], creds['apiVersion']), self.api.apiServer)
        self.assertNotEqual(creds['apiVersion'], self.api.version)
        self.assertNotEqual(creds['appSessionId'], self.api.appSessionId)
        self.assertNotEqual(creds['accessToken'], self.api.getAccessToken())

    def test__set_credentials_missing_config_creds_exception(self):
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
            creds = self.api._set_credentials(clientKey=None, clientSecret=None,
                apiServer=None, apiVersion=None, appSessionId='', accessToken='',
                profile=self.profile)
        os.remove(cfg)
        shutil.move(tmp_cfg, cfg)

    def test__set_credentials_defaults_for_optional_args(self):
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
        creds = self.api._set_credentials(clientKey=None, clientSecret=None,
                apiServer=None, apiVersion=None, appSessionId='', accessToken='',
                profile=self.profile)
        self.assertEqual(creds['appSessionId'], '')
        self.assertEqual(creds['accessToken'], '')
        os.remove(cfg)
        shutil.move(tmp_cfg, cfg)        

    def test__get_local_credentials(self):                                                            
        creds = self.api._get_local_credentials(profile='unit_tests')
        self.assertEqual('name' in creds, True)
        self.assertEqual('clientKey' in creds, True)
        self.assertEqual('clientSecret' in creds, True)
        self.assertEqual('apiServer' in creds, True)
        self.assertEqual('apiVersion' in creds, True)
        self.assertEqual('appSessionId' in creds, True)
        self.assertEqual('accessToken' in creds, True)

    def test__get_local_credentials_default_profile(self):
        creds = self.api._get_local_credentials(profile=self.profile)
        self.assertEqual('name' in creds, True)
        self.assertEqual('clientKey' in creds, True)
        self.assertEqual('clientSecret' in creds, True)
        self.assertEqual('apiServer' in creds, True)
        self.assertEqual('apiVersion' in creds, True)
        self.assertEqual('appSessionId' in creds, True)
        self.assertEqual('accessToken' in creds, True)

    def test__get_local_credentials_missing_profile(self):                                                        
        with self.assertRaises(CredentialsException):
            creds = self.api._get_local_credentials(profile="SuperCallaFragaListic AppTastic")                

class TestAPIGenomeMethods(unittest.TestCase):
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

class TestAPIUtilityMethods(unittest.TestCase):
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

#if __name__ == '__main__':   
#    unittest.main()

suite1 = unittest.TestLoader().loadTestsFromTestCase(TestFileDownloadMethods)
suite2 = unittest.TestLoader().loadTestsFromTestCase(TestAPIUploadMethods)
suite3 = unittest.TestLoader().loadTestsFromTestCase(TestAPIDownloadMethods)
# non-file-transfer tests
suite4 = unittest.TestLoader().loadTestsFromTestCase(TestAppResultMethods)
suite5 = unittest.TestLoader().loadTestsFromTestCase(TestAPIAppResultMethods)
suite6 = unittest.TestLoader().loadTestsFromTestCase(TestRunMethods)
suite7 = unittest.TestLoader().loadTestsFromTestCase(TestAPIRunMethods)
suite8 = unittest.TestLoader().loadTestsFromTestCase(TestSampleMethods)
suite9 = unittest.TestLoader().loadTestsFromTestCase(TestAPISampleMethods)
suite10 = unittest.TestLoader().loadTestsFromTestCase(TestProjectMethods)
suite11 = unittest.TestLoader().loadTestsFromTestCase(TestAPIProjectMethods)

suite12 = unittest.TestLoader().loadTestsFromTestCase(TestAPICredentialsMethods)
suite13 = unittest.TestLoader().loadTestsFromTestCase(TestAPIGenomeMethods)
suite14 = unittest.TestLoader().loadTestsFromTestCase(TestAPIUtilityMethods)

#alltests = unittest.TestSuite([suite10, suite11])
alltests = unittest.TestSuite([suite1, suite2, suite3, suite4, suite5, suite6, suite7, suite8, suite9, suite10, suite11, suite12])
unittest.TextTestRunner(verbosity=2).run(alltests)
