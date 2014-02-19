
class GenomeV1(object):

    def __init__(self):
        self.swaggerTypes = {
            'Source': 'str',
            'SpeciesName': 'str',
            'Build': 'str',
            'Id': 'str',
            'Href': 'str',
            'DisplayName': 'str'
        }
        
    def __str__(self):        
        return self.DisplayName
        
    def __repr__(self):
        return str(self)
