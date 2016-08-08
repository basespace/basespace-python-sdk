
import json
from io import StringIO

class ListResponse(object):

    def __init__(self):
        self.swaggerTypes = {
            'ResponseStatus': 'ResponseStatus',
            'Response': 'ResourceList',
            'Notifications': 'list<Str>'
        }

    def _convertToObjectList(self):
        '''
        Converts items in server response from list of strings to list of python objects (though not BaseSpacePy models)                
        '''
        l = []
        for m in self.Response.Items:
            io = eval(m)
            s = json.dumps(io)
            mj = json.loads(s)
            l.append(mj)
        return l
