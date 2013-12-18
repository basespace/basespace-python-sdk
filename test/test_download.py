import unittest
import os
import sys
from tempfile import mkdtemp
import shutil
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import ByteRangeSizeException
import app_data

# on cloud-hoth (your BaseSpace account must have access to this data)
tconst = { 'file_id_small': '9895886', # 4 KB,     public data B. cereus
           'file_id_large': '9896135', # 55.31 MB  public data B. cereus                    
          }

class TestDownloadMethods(unittest.TestCase):
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

    def test_byte_range_download_exception(self):
        with self.assertRaises(ByteRangeSizeException):
            self.api.fileDownload(
                tconst['file_id_large'],                    
                localDir = self.temp_dir,
                byteRange = [1,10000001]            
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
suite = unittest.TestLoader().loadTestsFromTestCase(TestDownloadMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
