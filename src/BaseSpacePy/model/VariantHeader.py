
class VariantHeader(object):

    def __init__(self):
        self.swaggerTypes = {
            'Metadata': 'dict',
            'Samples': 'dict',
            'Legends': 'dict',
        }
        
    def __str__(self):
        return "VariantHeader: SampleCount=" + str(len(self.Samples))
    
    def __repr__(self):
        return str(self)
