
from BaseSpacePy.api.BaseSpaceException import UndefinedParameterException, UnknownParameterException, IllegalParameterException, QueryParameterException

legal = {'Statuses': [],
         'SortBy': ['Id', 'Name', 'DateCreated', 'Path', 'Position'],
         'Extensions': [],
         #'Extensions': ['bam', 'vcf'],
         'Offset': [],
         'Limit': [],
         'SortDir': ['Asc', 'Desc'], 
         'Name': [], 
         'StartPos':[], 
         'EndPos':[], 
         'Format':[]
         #'Format': ['txt', 'json', 'vcf'], 
         }

class QueryParameters(object):
    '''
    The QueryParameters class can be passed as an optional argument
    for sorting/filtering of list-responses (such as lists of samples, AppResults, variants, etc.)    
    '''
    def __init__(self, pars=None, required=None):
        '''
        :param pars: (optional) a dictionary of query parameters, default None
        :param required: (optional) a list of required query parameter names, default None
        
        :raises QueryParameterException: when non-dictionary argument for 'pars' is passed
        '''
        if pars is None:
            pars = {}
        if required is None:
            required = []         
        self.passed = {}
        try:
            for k in pars.keys():
                self.passed[k] = pars[k]
        except AttributeError:
            raise QueryParameterException("The 'pars' argument to QueryParameters must be a dictionary")
        self.required = required
        
    def __str__(self):
        return str(self.passed)
    
    def __repr__(self):
        return str(self)
    
    def getParameterDict(self):
        return self.passed
    
    def validate(self):
        '''
        Validates that query parameter keys and values are properly formed:
        required keys are present, and keys and values are within the set of 
        known acceptable keys/values.
        
        :raises UndefinedParameterException: when a required parameter is not present
        :raises UnknownParameterException: when a parameter name is not present in the list of acceptable parameters names
        :raises IllegalParameterException: when a parameter value (with a valid name) is not present in the list of acceptable parameters values
        :returns: None
        '''
        for p in self.required:
            if not self.passed.has_key(p): 
                raise UndefinedParameterException(p)
        for p in self.passed.keys():
            if not legal.has_key(p): 
                raise UnknownParameterException(p)
            if len(legal[p])>0 and (not self.passed[p] in legal[p]): 
                raise IllegalParameterException(p,legal[p])
