
class Purchase(object):
    '''
    Represents a BaseSpace Purchase object.
    '''
    def __init__(self):
        self.swaggerTypes = {
            'Id': 'str',
            'Status': 'str',       # PENDING, CANCELLED, ERRORED, COMPLETED
            'RefundStatus': 'str', # NOTREFUNDED, REFUNDED
            'DateCreated': 'datetime',
            'DateUpdated': 'datetime',
            'InvoiceNumber': 'str',
            'Amount': 'str',
            'AmountOfTax': 'str',
            'AmountTotal': 'str',
            'Products': 'list<Product>',
            'PurchaseType': 'str',
            'AppSession': 'AppSessionCompact',
            'User': 'UserCompact',
            'Application': 'ApplicationCompact',
            'HrefPurchaseDialog': 'str',    # new purchases only
            'RefundSecret': 'str',          # new purchases only
            'ExceptionMessage': 'str',      # errors only
            'ExceptionStackTrace': 'str',   # errors only
            'DateRefunded': 'datetime',     # refunds only
            'UserRefundedBy': 'str',        # refunds only
            'RefundComment': 'str',         # refunds only
        }
    
    def __str__(self):
        return str(self.Id)
    
    def __repr__(self):
        return str(self)
