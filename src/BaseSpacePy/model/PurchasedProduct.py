
class PurchasedProduct(object):

    def __init__(self):
        self.swaggerTypes = {
            'PurchaseId': 'str',
            'DatePurchased': 'datetime',
            'Id': 'str',
            'Name': 'str',
            'Price': 'str',
            'Quantity': 'str',
            'PersistenceStatus': 'str',
            'Tags': 'list<str>',         # only if provided as a query parameter
            'ProductIds': 'list<str>',   # only if provided as a query parameter
        }

    def __str__(self):
        return str(self.Name)
    
    def __repr__(self):
        return str(self)
