
class CoverageMetadata(object):
    
    def __init__(self):                
        self.swaggerTypes = {
            'MaxCoverage': 'int',
            'CoverageGranularity': 'int'
        }
    
    def __str__(self):
        return "CoverageMeta: max=" + str(self.MaxCoverage) + " gran=" + str(self.CoverageGranularity)
    
    def __repr__(self):
        return str(self)
