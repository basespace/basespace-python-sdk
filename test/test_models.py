"""
"""
import os
import argparse
import copy
from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

class TestSDK(object):
    '''
    Compares objects from BaseSpace REST API to SDK objects, including pickled objects
    '''
    def __init__(self):                                        
        
        self.qp = {}
        self.rest_method = 'GET'
        self.postData = None
        self.headerParams=None
        self.list_request = False
        
        # TODO change to unit_tests, but need to add projects/run to account?
        self.myAPI = BaseSpaceAPI(profile="ps_native_hoth")        
        self.api = APIClient(self.myAPI.getAccessToken(), self.myAPI.apiServer)        

    def compare_dict_to_obj(self, rest_dict, p_obj):
        """ 
        Compare a dictionary from a REST API response and a SDK object for identity.
        """
        for r_key, r_val in rest_dict.iteritems():
            # confirm that the key from REST api exists in stored object
            try:
                p_val = getattr(p_obj, r_key)                                      
            except AttributeError:
                print "REST API attribute '" + r_key + "' doesn't exist in object"                            
            else:
                self.classify_rest_item(r_val, p_val, r_key)                    

    def compare_list_to_obj(self, rest_list, p_obj, r_key):
        """ 
        Compare a list from a REST API response and an SDK object for identity.
        """                   
        if type(p_obj) != list:
            print "Attribute '" + r_key + "' is a list in the REST API but not in the object"
        elif len(p_obj) != len(rest_list):
            print "Attribute '" + r_key + "' has different list length between REST API and object"
        else:
            for r_val, p_val in map(None, rest_list, p_obj):
                self.classify_rest_item(r_val, p_val, r_key)
                                                                        
    def compare_builtin_to_obj(self, rest_val, p_obj, r_key):
        """ 
        Compare a built-in type from a REST API response and an SDK object for identity.
        """                   
        # convert unicode to ascii for comparisons
        if isinstance(rest_val, unicode):
            rest_val = rest_val.encode('ascii','ignore')
        # don't compare values for datetimes
        if r_key in ['DateCreated', 'DateModified', 'DateUploadCompleted', 'DateUploadStarted']:
            pass
        elif rest_val != p_obj:                                
            print "REST API attribute '" + r_key + "' has value '" + str(rest_val) + "' doesn't match object value '" + str(p_obj) + "'"                            

    def classify_rest_item(self, r_val, p_val, r_key):
        """
        Determine the input REST item's type and call method to compare to input object
        """                                        
        if type(r_val) in [ int, str, bool, float, unicode]:                            
            self.compare_builtin_to_obj(r_val, p_val, r_key)
        elif type(r_val) == dict:            
            self.compare_dict_to_obj(r_val, p_val)
        elif type(r_val) == list:                                    
            self.compare_list_to_obj(r_val, p_val, r_key)
        else:
            print "REST API attribute'" + r_key + "' has an unrecognized attribute type"                            
        
    def test_rest_vs_sdk(self):
        """
        Compares REST API response and python SDK object for identify, for an API method
        """        
        sdk_obj = self.call_sdk()
        rest_obj = self.call_rest_api()                                                        
        # TODO passing Response here, SDK doesn't currently capture other items at this level (e.g. Notifications)
        if self.list_request:
            self.compare_list_to_obj(rest_obj['Response']['Items'], sdk_obj, "BASE")
        else:
            self.compare_dict_to_obj(rest_obj['Response'], sdk_obj)

    def call_rest_api(self):
        """
        Call the REST API for this object
        """
        return self.api.callAPI(self.rest_path, self.rest_method, queryParams=self.qp, postData=self.postData, headerParams=self.headerParams)

    def create_pickle_from_sdk(self, pickle_path):
        """
        Stores a pickled object in the provided path (include file name) for the object returned for this SDK method
        """
        sdk_obj = self.call_sdk()        
        with open(pickle_path, 'w') as f:
            Pickle.dump(sdk_obj, f)
            
    def get_pickle(self, pickle_path):
        """
        Retrieves a pickled object from the provided path (include file name), for this API test
        """        
        with open(pickle_path, 'r') as f:
            sdk_obj = Pickle.load(f)
        return sdk_obj        
        
    def test_rest_vs_pickle(self, pickle_path):
        """
        Compares REST API response and a stored object for identify, for an API method
        """
        p_obj = self.get_pickle(pickle_path)
        rest_obj = self.call_rest_api()
        self.compare_dict_to_obj(rest_obj['Response'], p_obj)

class GetAppSessionById(TestSDK):

    def __init__(self, bsid):        
        super(GetAppSessionById, self).__init__()
        self.rest_path = '/appsessions/' + bsid
        
        self.appsession_id = bsid

    def call_sdk(self):
        return self.myAPI.getAppSessionById(self.appsession_id)

class GetAppSessionPropertiesById(TestSDK):
    
    def __init__(self, ssn_id, query_p={}):
        super(GetAppSessionPropertiesById, self).__init__()
        self.rest_path = '/appsessions/' + ssn_id + '/properties'
        
        self.appsession_id = ssn_id
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getAppSessionPropertiesById(self.appsession_id, qp(self.qp))        

class GetAppSessionPropertyByName(TestSDK):

    def __init__(self, ssn_id, prop_name, query_p={}):
        super(GetAppSessionPropertyByName, self).__init__()
        self.rest_path = '/appsessions/' + ssn_id + '/properties/' + prop_name + '/items'
        
        self.appsession_id = ssn_id
        self.property_name = prop_name
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getAppSessionPropertyByName(self.appsession_id, qp(self.qp), self.property_name)        

class GetRunById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetRunById, self).__init__()
        self.rest_path = '/runs/' + bsid
        
        self.run_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getRunById(self.run_id, qp(self.qp))

class GetRunPropertiesById(TestSDK):

    def __init__(self, ssn_id, query_p={}):        
        super(GetRunPropertiesById, self).__init__()
        self.rest_path = '/runs/' + ssn_id + '/properties'
        
        self.run_id = ssn_id
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getRunPropertiesById(self.run_id, qp(self.qp))

class GetProjectById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetProjectById, self).__init__()
        self.rest_path = '/projects/' + bsid
        
        self.project_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getProjectById(self.project_id, qp(self.qp))

class GetProjectPropertiesById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetProjectPropertiesById, self).__init__()
        self.rest_path = '/projects/' + bsid + '/properties'
        
        self.project_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getProjectPropertiesById(self.project_id, qp(self.qp))

class GetSampleById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetSampleById, self).__init__()
        self.rest_path = '/samples/' + bsid
        
        self.sample_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getSampleById(self.sample_id, qp(self.qp))

class GetSamplePropertiesById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetSamplePropertiesById, self).__init__()
        self.rest_path = '/samples/' + bsid + '/properties'
        
        self.sample_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getSamplePropertiesById(self.sample_id, qp(self.qp))

class GetAppResultById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetAppResultById, self).__init__()
        self.rest_path = '/appresults/' + bsid
        
        self.appresult_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getAppResultById(self.appresult_id, qp(self.qp))

class GetAppResultPropertiesById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetAppResultPropertiesById, self).__init__()
        self.rest_path = '/appresults/' + bsid + '/properties'
        
        self.appresult_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getAppResultPropertiesById(self.appresult_id, qp(self.qp))

class GetFileById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetFileById, self).__init__()
        self.rest_path = '/files/' + bsid
        
        self.file_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getFileById(self.file_id, qp(self.qp))

class GetFilePropertiesById(TestSDK):

    def __init__(self, bsid, query_p={}):        
        super(GetFilePropertiesById, self).__init__()
        self.rest_path = '/files/' + bsid + '/properties'
        
        self.file_id = bsid
        self.qp = query_p

    def call_sdk(self):
        return self.myAPI.getFilePropertiesById(self.file_id, qp(self.qp))

class FilterVariantSet(TestSDK):
    
    def __init__(self, bsid, chrom, start_pos, end_pos, format ,query_p=None):        
        super(FilterVariantSet, self).__init__()
        self.rest_path = '/variantset/' + bsid + '/variants/' + chrom        
        if query_p is None:
            query_p = {}
            
        self.file_id = bsid
        self.chrom = chrom
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.format = format        
        self.qp = copy.deepcopy(query_p)
        self.qp['StartPos'] = start_pos
        self.qp['EndPos'] = end_pos
        self.qp['Format'] = format
        self.list_request = True
    
    def call_sdk(self):
        return self.myAPI.filterVariantSet(self.file_id, self.chrom, self.start_pos, self.end_pos, self.format, qp(self.qp))    


class TestSuite(object):
    '''
    Assemble a collection of tests for a given app (and api data), and execute them in desired fashion (e.g. REST vs. SDK)
    '''
    def __init__(self, cfg):
        self.cfg = cfg
        self.tests = []

    def add_tests(self):
        cfg = self.cfg
        try:
            self.tests.append((FilterVariantSet(cfg['vcf_id'], cfg['vcf_chr'], cfg['vcf_start'], cfg['vcf_end'], cfg['vcf_format'], cfg['query_p']), "with query parameter"))
        except AttributeError:            
            print "Skipping test FilterVariantSet -- missing input parameter"
        try:
            self.tests.append((GetAppSessionById(cfg['ssn_id']), "test"))
        except AttributeError:
            print "Skipping test GetAppSessionById -- missing input parameter"
        try:
            self.tests.append((GetAppSessionPropertiesById(cfg['ssn_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetAppSessionPropertiesById -- missing input parameter"
        try:            
            for key, value in cfg['multivalue_property_names'].iteritems():
                self.tests.append((GetAppSessionPropertyByName(cfg['ssn_id'], value, cfg['query_p']), key))
        except AttributeError:
            print "Skipping test GetAppSessionPropertiesByName -- missing input parameter"
        try:
            self.tests.append((GetRunById(cfg['run_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetRunById -- missing input parameter"
        try:
            self.tests.append((GetRunPropertiesById(cfg['run_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetRunPropertiesById -- missing input parameter"
        try:
            self.tests.append((GetProjectById(cfg['project_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetProjectById -- missing input parameter"
        try:
            self.tests.append((GetProjectPropertiesById(cfg['project_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:            
            print "Skipping test GetProjectPropertiesById -- missing input parameter"
        try:
            self.tests.append((GetSampleById(cfg['sample_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetSampleById -- missing input parameter"
        try:
            self.tests.append((GetSamplePropertiesById(cfg['sample_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:            
            print "Skipping test GetSamplePropertiesById -- missing input parameter"            
        try:
            self.tests.append((GetAppResultById(cfg['appresult_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetAppResultById -- missing input parameter"
        try:
            self.tests.append((GetAppResultPropertiesById(cfg['appresult_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:            
            print "Skipping test GetAppResultPropertiesById -- missing input parameter"            
        try:
            self.tests.append((GetFileById(cfg['file_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:
            print "Skipping test GetFileById -- missing input parameter"
        try:
            self.tests.append((GetFilePropertiesById(cfg['file_id'], cfg['query_p']), "with query parameter"))
        except AttributeError:            
            print "Skipping test GetFilePropertiesById -- missing input parameter"          

    
    def test_rest_vs_sdk(self):
        for test in self.tests:
            print "\nTesting REST vs SDK for " + test[0].__class__.__name__ + "' with comment '" + test[1] + "'"
            try:
                test[0].test_rest_vs_sdk()
            except Exception as e:
                print "Exception: " + str(e)        

if __name__ == '__main__':
        
    # BaseSaceAPI profile (in TestSDK.__init__) must have permission to read the items in cfg
    cfg = {}
    cfg['ssn_id'] = '1300310'
    cfg['query_p'] = {'Limit':'45'}
    cfg['multivalue_property_names'] = {
        #'string': 'Input.app-session-name',
        'strings': 'Input.checkbox-1',
        #'project': 'Input.project-id',
        'projects': 'Input.project-id2',
        #'appresult': 'Input.app-result-id',
        'appresults': 'Input.app-result-id2',
        #'sample': 'Input.sample-id',
        'samples': 'Input.sample-id2',
        #'file': 'Input.file-id',
        'files': 'Input.file-id2',
        #'run': 'Input.run-id',
        'runs': 'Input.run-id2',
        #'map': None,
        'maps': 'Input.app-result-id2.attributes',
    }                       
    cfg['run_id'] = '523524' 
    cfg['project_id'] = '2'
    cfg['sample_id'] = '1021'
    cfg['appresult_id'] = '21'
    cfg['file_id'] = '8199'
    cfg['vcf_id'] = '9883918'
    cfg['vcf_chr'] = 'phix'
    cfg['vcf_start'] = '1'
    cfg['vcf_end'] = '4000'
    cfg['vcf_format'] = 'txt' # or 'vcf'
    
    
    # Run all tests in the test suite for 'test_app1'    
    #suite = TestSuite(app_data.test_app1)
    suite = TestSuite(cfg)
    suite.add_tests()
    suite.test_rest_vs_sdk()                
    
