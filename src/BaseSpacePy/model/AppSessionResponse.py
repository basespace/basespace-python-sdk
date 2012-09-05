#!/usr/bin/env python
class AppLaunchResponse:

    def __init__(self):
        self.swaggerTypes = {
            'ResponseStatus': 'ResponseStatus',
            'Response': 'AppSession',
            'Notifications': 'list<Str>'
        }

        self.ResponseStatus = None # ResponseStatus

        self.Response = None # Coverage

        self.Notifications = None # list<Str>

