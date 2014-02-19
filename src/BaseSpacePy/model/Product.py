
class Product(object):

    def __init__(self):
        self.swaggerTypes = {
            'Id': 'str',
            'Name': 'str',
            'Price': 'str',
            'Quantity': 'str',
            'PersistenceStatus': 'str', # NOPERSISTENCE, ACTIVE, EXPIRED
            'Tags': 'list<str>',
        }

    def __str__(self):
        return str(self.Name)

    def __repr__(self):
        return str(self)
