import unittest
import os
import sys
from tempfile import mkdtemp
import shutil
import urlparse
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import ByteRangeException, UploadPartSizeException, CredentialsException
from BaseSpacePy.model.MultipartFileTransfer import Utils
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

# Dependencies:
# 1. Create a profile named 'unit_tests' in ~/.basespacepy.cfg that has the credentials for an app on https://portal-hoth.illumina.com; there should also be a 'DEFALT' profile in the config file
# 2. Import the following data from Public Data on cloud-hoth.illumina.com:
#    From Public Dataset 'B. cereus': Project name 'BaseSpaceDemo' (Id 596596), and Run name 'BacillusCereus' (Id 555555)

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
           'test_upload_project_name': 'Python SDK Unit Test Data',
           # for runs
           'run_id': '555555', # public data B. cereus Run
           'run_name': 'BacillusCereus',
           'run_property_samples_0_name': 'BC_1',        
           'run_file_0_name': 'RTAComplete.txt',
           'run_samples_len': 12,
           'run_sample_0_name': 'BC_1'
          }

class TestAppResultUploadMethods(unittest.TestCase):
    '''
    Tests upload method of AppResult objects
    '''
    @classmethod
    def setUpClass(cls):    
        '''
        For all upload unit tests (not per test):
        Create a new 'unit test' project, or get it if exists, to upload to data to.
        Then create a new app result in this project, getting a new app session id
        '''
        cls.api = BaseSpaceAPI(profile='unit_tests')
        cls.proj = cls.api.createProject(tconst['test_upload_project_name'])                        
        cls.ar = cls.proj.createAppResult(cls.api, "test appresult upload", "test appresult upload", appSessionId="")

    def test_small_upload(self):
        testDir = "testSmallUploadAppResultDirectory"
        fileName = os.path.basename(tconst['file_small_upload'])
        myFile = self.ar.uploadFile(
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
        cls.proj = cls.api.createProject(tconst['test_upload_project_name'])                        
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


class TestRunMethods(unittest.TestCase):
    '''
    Tests Run object methods
    '''        
    def setUp(self):        
        '''
        Get Run and API objects
        '''                
        self.api = BaseSpaceAPI(profile='unit_tests')
        self.run = self.api.getRunById(tconst['run_id'])                                        

    def test_run_files(self):
        rf = self.run.getFiles(self.api)
        self.assertEqual(len(rf), 10)
        self.assertEqual(rf[0].Name, tconst['run_file_0_name'])
        
    def test_run_files_with_qp_limit(self):
        rf = self.run.getFiles(self.api, qp({'Limit':200}))
        self.assertEqual(len(rf), 200)

    def test_run_samples(self):
        rs = self.run.getSamples(self.api)
        self.assertEqual(len(rs), 10)
        self.assertEqual(rs[0].Name, tconst['run_sample_0_name'])
        
    def test_run_samples_with_qp_limit(self):
        rs = self.run.getSamples(self.api, qp({'Limit':200}))
        self.assertEqual(len(rs), tconst['run_samples_len'])

class TestAPIRunMethods(unittest.TestCase):
    '''
    Tests API object Run methods
    '''        
    def setUp(self):        
        '''
        Get an API object
        '''                
        self.api = BaseSpaceAPI(profile='unit_tests')

    def test_run(self):                                                    
        rf = self.api.getRunById(tconst['run_id'])        
        self.assertEqual(rf.Name, tconst['run_name'])
        
    # not testing query parameter argument for getRunById()

    def test_run_properties(self):                                                    
        rp = self.api.getRunPropertiesById(tconst['run_id'])        
        self.assertEqual(rp.Items[0].Items[0].Name, tconst['run_property_samples_0_name'])
        
    # not testing query parameter argument for getRunPropertiesById()

    def test_run_files(self):                                                    
        rf = self.api.getRunFilesById(tconst['run_id'])
        self.assertEqual(len(rf), 10)
        self.assertEqual(rf[0].Name, tconst['run_file_0_name'])
        
    def test_run_files_with_qp_limit(self):
        rf = self.api.getRunFilesById(tconst['run_id'], qp({'Limit':200}))
        self.assertEqual(len(rf), 200)

    def test_run_samples(self):
        rs = self.api.getRunSamplesById(tconst['run_id'])
        self.assertEqual(len(rs), 10)
        self.assertEqual(rs[0].Name, tconst['run_sample_0_name'])
        
    def test_run_samples_with_qp_limit(self):
        rs = self.api.getRunSamplesById(tconst['run_id'], qp({'Limit':200}))
        self.assertEqual(len(rs), tconst['run_samples_len'])

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

#if __name__ == '__main__':   
#    unittest.main()
suite1 = unittest.TestLoader().loadTestsFromTestCase(TestAppResultUploadMethods)
suite2 = unittest.TestLoader().loadTestsFromTestCase(TestFileDownloadMethods)
suite3 = unittest.TestLoader().loadTestsFromTestCase(TestAPIUploadMethods)
suite4 = unittest.TestLoader().loadTestsFromTestCase(TestAPIDownloadMethods)
# non-file-transfer tests
suite5 = unittest.TestLoader().loadTestsFromTestCase(TestRunMethods)
suite6 = unittest.TestLoader().loadTestsFromTestCase(TestAPIRunMethods)
suite7 = unittest.TestLoader().loadTestsFromTestCase(TestAPICredentialsMethods)
#alltests = unittest.TestSuite([suite7])
alltests = unittest.TestSuite([suite1, suite2, suite3, suite4, suite5, suite6, suite7])
unittest.TextTestRunner(verbosity=2).run(alltests)
