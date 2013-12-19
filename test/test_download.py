import unittest
import os
import sys
from tempfile import mkdtemp
import shutil
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import ByteRangeException
import app_data

# on cloud-hoth (your BaseSpace account must have access to this data)
tconst = { 'file_id_small': '9895886', # 4 KB,     public data B. cereus
           'file_id_large': '9896135', # 55.31 MB  public data B. cereus                    
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
        # confirm file size is correct
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
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

class TestAPIDownloadMethods(unittest.TestCase):
    '''
    Tests single download and multi-part download methods
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
        # confirm file size is correct
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
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
        # confirm file size is correct
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        os.remove(file_path)

    def test_multipartDownload_via_temp_file(self):
        new_file = self.api.multipartFileDownload(
            tconst['file_id_small'],                    
            localDir = self.temp_dir,            
            debug = True
            )
        file_path = os.path.join(self.temp_dir, new_file.Name)
        self.assertTrue(os.path.isfile(file_path))
        # confirm file size is correct        
        self.assertTrue(new_file.Size == os.stat(file_path).st_size)
        os.remove(file_path)

#if __name__ == '__main__':   
#    unittest.main()
suite1 = unittest.TestLoader().loadTestsFromTestCase(TestFileMethods)
suite2 = unittest.TestLoader().loadTestsFromTestCase(TestAPIDownloadMethods)
alltests = unittest.TestSuite([suite1, suite2])
unittest.TextTestRunner(verbosity=2).run(alltests)
