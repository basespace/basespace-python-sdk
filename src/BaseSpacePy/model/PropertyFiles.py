
class PropertyFiles(object):

    def __init__(self):
        self.swaggerTypes = {
            'Type': 'str',
            'Href': 'str',
            'Name': 'str',
            'Description': 'str',
            'Items': 'list<File>',
            'HrefItems': 'str',
            'ItemsDisplayedCount': 'int',
            'ItemsTotalCount': 'int'
        }

    def __str__(self):
        return str(self.Name)

    def __repr__(self):
        return str(self)
    
