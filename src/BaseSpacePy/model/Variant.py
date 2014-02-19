
class Variant(object):

    def __init__(self):
        self.swaggerTypes = {
            'CHROM': 'str',                 
            'ALT': 'str',
            'ID': 'list<Str>',
            'SampleFormat': 'dict',
            'FILTER': 'str',
            'INFO': 'dict',
            'POS':'int',
            'QUAL':'int',
            'REF':'str'
        }
        
    def __str__(self):
        return "Variant - " + self.CHROM + ": " + str(self.POS) + " id=" + str(self.ID)

    def __repr__(self):
        return str(self)
