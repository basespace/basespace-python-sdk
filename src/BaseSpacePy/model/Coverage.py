
class Coverage(object):

    def __init__(self):
        self.swaggerTypes = {
            'Chrom': 'str',
            'BucketSize': 'int',
            'MeanCoverage': 'list<int>',
            'EndPos': 'int',
            'StartPos': 'int'
        }
    def __str__(self):
        return 'Chr' + self.Chrom + ": " + str(self.StartPos) + "-" + str(self.EndPos) +\
             ": BucketSize=" + str(self.BucketSize)
              
    def __repr__(self):
        return str(self)
