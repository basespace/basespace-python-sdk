class KeyValues(object):

    def __init__(self):
        self.swaggerTypes = {
            'Key': 'str',
            'Values': 'list<str>',
        }

    def __str__(self):
        return str(self.Key)

    def __repr__(self):
        return str(self)
