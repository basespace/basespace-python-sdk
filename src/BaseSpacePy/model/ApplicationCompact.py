
class ApplicationCompact(object):
    """
    Application data returned by GET purchase
    """
    def __init__(self):
        self.swaggerTypes = {
            'Id': 'str',
            "Name":"str",
            "CompanyName":"str"
        }

    def __str__(self):
        return str(self.Name)

    def __repr__(self):
        return str(self)

        

