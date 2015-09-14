import os
import unittest

from BaseSpacePy.api.BaseMountInterface import BaseMountInterface, BaseMountInterfaceException

def get_basemount_root():
    import getpass
    username = getpass.getuser()
    config_name = "hoth"
    basemount_root = "/basespace"
    basemount_target = "%s.%s" % (username, config_name)
    return os.path.join(basemount_root, basemount_target)

basemount_root = get_basemount_root()
project_path = os.path.join(basemount_root, "Projects", "BaseSpaceDemo")
project_id = '596596'
sample_path = os.path.join(project_path, "Samples", "BC_1")
sample_id = '855855'

class TestBaseMountInterace(unittest.TestCase):
    def setUp(self):
        pass

    def test_fail_on_invalid_path(self):
        with self.assertRaises(BaseMountInterfaceException):
            BaseMountInterface("/tmp")

    def test_extract_project_details(self):
        bmi = BaseMountInterface(project_path)
        self.assertEqual(bmi.type, "project")
        self.assertEqual(bmi.id, project_id)

    def test_extract_sample_details(self):
        bmi = BaseMountInterface(sample_path)
        self.assertEqual(bmi.type, "sample")
        self.assertEqual(bmi.id, sample_id)

if __name__ == "__main__":
    unittest.main()