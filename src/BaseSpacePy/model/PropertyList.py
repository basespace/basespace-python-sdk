
class PropertyList(object):
    
    # Values for DynamicType, keyed by 'Type' in each property Item
    _dynamicType = {'string': 'PropertyString',
                    'string[]': 'PropertyStrings',
                    'project': 'PropertyProject',
                    'project[]': 'PropertyProjects',
                    'appresult': 'PropertyAppResult',
                    'appresult[]': 'PropertyAppResults',
                    'sample': 'PropertySample',
                    'sample[]': 'PropertySamples',
                    'file': 'PropertyFile',
                    'file[]': 'PropertyFiles',
                    'run': 'PropertyRun',
                    'run[]': 'PropertyRuns',
                    'map': 'PropertyMap',
                    'map[]': 'PropertyMaps',
                   }    

    def __init__(self):
        self.swaggerTypes = {
            'Items': 'list<DynamicType>',
            'Href': 'str', #
            'DisplayedCount': 'int',
            'TotalCount': 'int',            
            'Offset': 'int',
            'Limit': 'int',
            'SortDir': 'str',
            'SortBy': 'str'
        }
