from BaseSpacePy.api.BaseSpaceException import UndefinedParameterException,UnknownParameterException,IllegalParameterException

# not very strict parameters testing
legal    = {'SortBy':['Id', 'Name', 'DateCreated','Path','Position'],'Format':['txt'], 'Extensions':[],'Offset':[],'Limit':[],'SortDir':['Asc', 'Desc']}

class QueryParameters:
    '''
    The QueryParameters class can be passed as an optional arguments for a specific sorting of list-responses (such as lists of sample, analysis, or variants)
    '''
    def __init__(self,pars={}, required = ['SortBy','Offset','Limit','SortDir']):
        self.passed = {'SortBy':'Id','Offset':'0','Limit':'100','SortDir':'Asc'}
        for k in pars.keys():
            self.passed[k] = pars[k]
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