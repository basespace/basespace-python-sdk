
class RunCompact(object):

    def __init__(self):
        self.swaggerTypes = {
            'DateCreated': 'datetime',
            'Id': 'str',
            'Href': 'str',
            'ExperimentName': 'str'
        }

    def __str__(self):
        return self.ExperimentName

    def __repr__(self):
        return str(self)
