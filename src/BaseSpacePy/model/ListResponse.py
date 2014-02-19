
import json
from StringIO import StringIO

class ListResponse(object):

    def __init__(self):
        self.swaggerTypes = {
            'ResponseStatus': 'ResponseStatus',
            'Response': 'ResourceList',
            'Notifications': 'list<Str>'
        }

    def convertToObjectList(self):
        l = []
        for m in self.Response.Items:
            io = eval(m)
            s = json.dumps(io)
            mj = json.loads(s)
            l.append(mj)
        return l
