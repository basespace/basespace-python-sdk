
class MultiValuePropertyResponse(object):

    # Values for DynamicType, keyed by 'Type' in property response
    _dynamicType = { 'appresult[]': 'MultiValuePropertyAppResultsList',
                     'file[]': 'MultiValuePropertyFilesList',
                     'map[]': 'MultiValuePropertyMapsList',
                     'run[]': 'MultiValuePropertyRunsList',
                     'project[]': 'MultiValuePropertyProjectsList',                    
                     'sample[]': 'MultiValuePropertySamplesList',
                     'string[]': 'MultiValuePropertyStringsList',
                    }  

    def __init__(self):    
        self.swaggerTypes = {
            'ResponseStatus': 'ResponseStatus',
            'Response': 'DynamicType',
            'Notifications': 'list<Str>'
        }
