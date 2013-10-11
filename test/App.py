
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI

class App(object):
    """
    A Basespace App -- with credentials
    """
    def __init__(self, name, client_key, client_secret, access_token, appsession_id,
                 basespace_url = 'https://api.cloud-hoth.illumina.com/', 
                 version = 'v1pre3'):
        self.name = name
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token 
        self.appsession_id = appsession_id        
        self.basespace_url = basespace_url
        self.version = version
        
    def bs_api(self):
        """
        Returns a BaseSpace API object
        """
        return BaseSpaceAPI(self.client_key, self.client_secret, 
            self.basespace_url, self.version, self.appsession_id, self.access_token)


