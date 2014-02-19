
class ResponseStatus(object):

    def __init__(self):
        self.swaggerTypes = {
            'Message': 'str',
            'Errors': 'list<Str>',
            'ErrorCode': 'str',
            'StackTrace': 'str'
        }
