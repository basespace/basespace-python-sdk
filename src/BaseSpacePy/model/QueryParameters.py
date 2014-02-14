
from BaseSpacePy.api.BaseSpaceException import UndefinedParameterException, UnknownParameterException, IllegalParameterException, QueryParameterException

# not very strict parameters testing
legal = {'Statuses':[],'SortBy':['Id', 'Name', 'DateCreated','Path','Position'],'Format':['txt', 'json', 'vcf'], 'Extensions':[],'Offset':[],'Limit':[],'SortDir':['Asc', 'Desc'], 'Name':[], 'StartPos':[], 'EndPos':[], 'Format':[] }

class QueryParameters(object):
    '''
    The QueryParameters class can be passed as an optional arguments
    for a specific sorting of list-responses (such as lists of sample, AppResult, or variants)    
    '''
    def __init__(self, pars = None, required = None):
        '''
        :param pars: (optional) a dictionary of query parameters, default None
        :param required: (optional) a list of required query parameter names, default None
        
        :raises QueryParameterException: when non-dictionary argument for 'pars' is passed
        '''
        if pars is None:
            pars = {}
        if required is None:
            required = [] # ['SortBy','Offset','Limit','SortDir']
        #self.passed = {'SortBy':'Id','Offset':'0','Limit':'100','SortDir':'Asc'}
        self.passed = {}
        try:
            for k in pars.keys():
                self.passed[k] = pars[k]
        except AttributeError:
            raise QueryParameterException("The 'pars' argument to QueryParameters should be a dictionary")
        self.required = required
        
    def __str__(self):
        return str(self.passed)
    
    def __repr__(self):
        return str(self)
    
    def getParameterDict(self):
        return self.passed
    
    def validate(self):
        for p in self.required:
            if not self.passed.has_key(p): raise UndefinedParameterException(p)
        for p in self.passed.keys():
            if not legal.has_key(p): raise UnknownParameterException(p)
            if len(legal[p])>0 and (not self.passed[p] in legal[p]): raise IllegalParameterException(p,legal[p])
