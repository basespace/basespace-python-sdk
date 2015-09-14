import json
import os
import unittest

from BaseSpacePy.api.AppLaunchHelpers import AppSessionMetaDataRaw, AppSessionMetaDataSDK, LaunchSpecification, \
    LaunchPayload
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from BaseSpacePy.model.AppSessionResponse import AppSessionResponse

api = BaseSpaceAPI()

mydir = os.path.dirname(os.path.abspath(__file__))
app_session_path = os.path.join(mydir, "appsession.json")
app_name = "BWA Whole Genome Sequencing v1.0"
app_id = "279279"
app_properties = [
    {'Type': 'string', 'Name': 'Input.AnnotationSource'},
    {'Type': 'string[]', 'Name': 'Input.FlagPCRDuplicates-id'},
    {'Type': 'string', 'Name': 'Input.genome-id'},
    {'Type': 'string', 'Name': 'Input.GQX-id'},
    {'Type': 'project', 'Name': 'Input.project-id'},
    {'Type': 'sample', 'Name': 'Input.sample-id'},
    {'Type': 'string', 'Name': 'Input.StrandBias-id'}
]
app_property_names = [
    'AnnotationSource',
    'FlagPCRDuplicates-id',
    'genome-id',
    'GQX-id',
    'project-id',
    'sample-id',
    'StrandBias-id'
]
app_minimum_properties = [
    'project-id',
    'sample-id',
]
app_defaults = {
    'AnnotationSource': u'RefSeq',
    'genome-id': u'Human',
    'GQX-id': u'30',
    'StrandBias-id': u'10',
    'FlagPCRDuplicates-id': []
}


def get_basemount_root():
    import getpass

    username = getpass.getuser()
    config_name = "hoth"
    basemount_root = "/basespace"
    basemount_target = username
    if config_name:
        basemount_target = "%s.%s" % (basemount_target, config_name)
    return os.path.join(basemount_root, basemount_target)


basemount_root = get_basemount_root()
project_path = os.path.join(basemount_root, "Projects", "BaseSpaceDemo")
project_id = '596596'
sample_path = os.path.join(project_path, "Samples", "BC_1")
sample_id = '855855'

app_args = [project_path, sample_path]
app_args_derived = [project_id, sample_id]

app_launch_args = {
    "project-id": project_id,
    "sample-id": sample_id
}

launch_name = "BWA Whole Genome Sequencing v1.0 : BC_1"

launch_json = """{"Properties": [{"Content": "RefSeq", "Type": "string", "Name": "Input.AnnotationSource"}, {"items": [], "Type": "string[]", "Name": "Input.FlagPCRDuplicates-id"}, {"Content": "Human", "Type": "string", "Name": "Input.genome-id"}, {"Content": "30", "Type": "string", "Name": "Input.GQX-id"}, {"Content": "v1pre3/projects/596596", "Type": "project", "Name": "Input.project-id"}, {"Content": "v1pre3/samples/855855", "Type": "sample", "Name": "Input.sample-id"}, {"Content": "10", "Type": "string", "Name": "Input.StrandBias-id"}], "Name": "BWA Whole Genome Sequencing v1.0 : BC_1", "AutoStart": true, "StatusSummary": "AutoLaunch"}"""

app_session_raw = json.load(open(app_session_path))
app_session_sdk = api.apiClient.deserialize(app_session_raw, AppSessionResponse).Response


class TestAppSessionMetaData(unittest.TestCase):
    def setUp(self):
        pass

    def test_process_raw_appsession(self):
        asm = AppSessionMetaDataRaw(app_session_raw)
        properties, defaults = asm.get_refined_appsession_properties()
        self.assertEqual(properties, app_properties)
        self.assertEqual(defaults, app_defaults)
        self.assertEqual(asm.get_app_name(), app_name)
        self.assertEqual(asm.get_app_id(), app_id)

    def test_process_sdk_appsession(self):
        asm = AppSessionMetaDataSDK(app_session_sdk)
        properties, defaults = asm.get_refined_appsession_properties()
        self.assertEqual(properties, app_properties)
        self.assertEqual(defaults, app_defaults)
        self.assertEqual(asm.get_app_name(), app_name)
        self.assertEqual(asm.get_app_id(), app_id)


class TestLaunchSpecification(unittest.TestCase):
    def setUp(self):
        self.launchspec = LaunchSpecification(app_properties, app_defaults)

    def test_all_properties(self):
        self.assertEqual(self.launchspec.get_variable_requirements(), set(app_property_names))

    def test_get_minimum_requirements(self):
        self.assertEqual(self.launchspec.get_minimum_requirements(), app_minimum_properties)

    def test_get_list_properties(self):
        self.assertEqual(self.launchspec.count_list_properties(), 0)
        self.assertTrue(self.launchspec.is_list_property("FlagPCRDuplicates-id"))
        self.assertFalse(self.launchspec.is_list_property("sample-id"))


class TestLaunchPayload(unittest.TestCase):
    def setUp(self):
        self.launchspec = LaunchSpecification(app_properties, app_defaults)
        self.payload = LaunchPayload(self.launchspec, app_args, {})

    def test_deriving_name(self):
        self.assertEqual(self.payload.derive_launch_name(app_name), launch_name)

    def test_deriving_args(self):
        self.assertEqual(self.payload.get_args(), app_launch_args)
        # if we pass in literal BaseSpace IDs, they should come out the same
        alt_payload = LaunchPayload(self.launchspec, app_args_derived, {})
        self.assertEqual(alt_payload.get_args(), app_launch_args)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.launchspec = LaunchSpecification(app_properties, app_defaults)
        self.payload = LaunchPayload(self.launchspec, app_args, {})

    def test_launch_json_generation(self):
        args = self.payload.get_args()
        launch_name = self.payload.derive_launch_name(app_name)
        app_launch_json = self.launchspec.make_launch_json(args, launch_name)
        self.assertEqual(app_launch_json, launch_json)

if __name__ == "__main__":
    unittest.main()
