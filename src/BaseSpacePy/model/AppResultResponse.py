class AppResultResponse:

    def __init__(self):
        self.swaggerTypes = {
            'ResponseStatus': 'ResponseStatus',
            'Response': 'AppResult',
            'Notifications': 'list<Str>'
        }

        self.ResponseStatus = None # ResponseStatus
        self.Response = None # Analysis
        self.Notifications = None # list<Str>

