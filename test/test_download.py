import unittest
import os
import sys
from tempfile import mkdtemp
import shutil
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import ByteRangeException
from BaseSpacePy.model.MultipartDownload import Utils
import app_data

# on cloud-hoth (your BaseSpace account must have access to this public data)
tconst = { # download
           'file_id_small': '9895886', # 4 KB,     public data B. cereus
           'file_id_large': '9896135', # 55.31 MB  public data B. cereus
           'file_small_md5': 'e8b5a1d82b659763df69783ef57e0180', # file id 9895886           
           'file_large_md5': '9267236a2d870da1d4cb73868bb51b35', # file id 9896135 
           # upload
           'file_small_upload': 'data/test.small.upload.txt',
           'file_large_upload': 'data/BC-12_S12_L001_R2_001.fastq.gz',
           'file_small_upload_size': 11,
           'file_large_upload_size': 57995799,
           'test_upload_project_name': 'Python SDK Unit Test Data',
          }

class TestFileMethods(unittest.TestCase):
    '''
    Tests methods of File objects
    '''
    def setUp(self):
        try:
            unit_test_app = app_data.unit_test_app
        except Exception as e:
            raise Exception("You must first enter your app's credentials to run tests")                
        self.api = unit_test_app.bs_api()
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
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertTrue(Utils.md5_for_file(fp) == tconst['file_small_md5'])
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
        self.assertTrue(1001 == os.stat(file_path).st_size)
        os.remove(file_path)        

class TestAPIUploadMethods(unittest.TestCase):
    '''
    Tests single and multi-part upload methods
    '''
    def setUp(self):
        '''
        Create a new 'unit test' project, or get it if exists, to upload to data to.
        Then create a new app result in this project, getting a new app session id
        '''
        try:
            unit_test_app = app_data.unit_test_app
        except Exception as e:
            raise Exception("You must first enter your app's credentials to run tests")                
        self.api = unit_test_app.bs_api()        
        self.proj = self.api.createProject(tconst['test_upload_project_name'])                        
        self.ar = self.proj.createAppResult(self.api, "test small upload", "test small upload", appSessionId="")

    def test_small_upload(self):            
        myFile = self.api.appResultFileUpload(
            Id=self.ar.Id, 
            localPath=tconst['file_small_upload'], 
            fileName=os.path.basename(tconst['file_small_upload']), 
            directory="", 
            contentType='text/plain') # TODO test other content types?
        self.assertTrue(myFile.Size == tconst['file_small_upload_size'])

#    @unittest.skip('speeding up tests but skipping multi-part upload :(')
    def test_multipart_upload(self):
        myFile = self.api.multipartFileUpload(
            Id=self.ar.Id,
            localDir=tconst['file_large_upload'], 
            fileName=os.path.basename(tconst['file_large_upload']), 
            directory="",                          
            contentType='application/octet-stream',
            tempDir=None, 
            cpuCount = 4, # processors
            partSize= 10, # MB, chunk size
            verbose = False,
            #tempDir = args.temp_dir
            )            
        self.assertTrue(myFile.Size == tconst['file_large_upload_size'])
        
#        ar.uploadFile(self.api, tconst['file_small_upload'], 
#            args.file_path, 
#            os.path.basename(args.file_path), 
#            os.path.dirname(args.file_path), 
#            'text/plain')
 


class TestAPIDownloadMethods(unittest.TestCase):
    '''
    Tests single and multi-part download methods
    '''
    def setUp(self):
        try:
            unit_test_app = app_data.unit_test_app
        except Exception as e:
            raise Exception("You must first enter your app's credentials to run tests")                
        self.api = unit_test_app.bs_api()
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
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertTrue(Utils.md5_for_file(fp) == tconst['file_small_md5'])
        os.remove(file_path)

#    @unittest.skip('speeding up tests but skipping multi-part download :(')
    def test_large_download(self):
        new_file = self.api.fileDownload(
            tconst['file_id_large'],                    
            localDir = self.temp_dir,            
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size is correct
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertTrue(Utils.md5_for_file(fp) == tconst['file_large_md5'])
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
        self.assertTrue(1001 == os.stat(file_path).st_size)
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

    def test_multipartDownload(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,
            processCount = 10,
            partSize = 12000000
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertTrue(Utils.md5_for_file(fp) == tconst['file_small_md5'])
        os.remove(file_path)

    def test_multipartDownload_via_temp_file(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,            
            debug = True
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size and md5 are correct        
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        fp = open(file_path, "r+b")
        self.assertTrue(Utils.md5_for_file(fp) == tconst['file_small_md5'])
        os.remove(file_path)

#if __name__ == '__main__':   
#    unittest.main()
suite1 = unittest.TestLoader().loadTestsFromTestCase(TestFileMethods)
suite2 = unittest.TestLoader().loadTestsFromTestCase(TestAPIUploadMethods)
suite3 = unittest.TestLoader().loadTestsFromTestCase(TestAPIDownloadMethods)
alltests = unittest.TestSuite([suite2])
#alltests = unittest.TestSuite([suite1, suite2, suite3])
unittest.TextTestRunner(verbosity=2).run(alltests)
