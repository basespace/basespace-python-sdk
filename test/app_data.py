"""
Contains app credentials for a developer's apps
"""
from App import App

my_app = App(
        name = "my new app",
        client_key = "",    # fill in value from BaseSpace developer portal
        client_secret = "", # fill in value from BaseSpace developer portal
        access_token = "",  # fill in value from BaseSpace developer portal
        appsession_id = "test",
        basespace_url = "https://api.basespace.illumina.com/", 
                            # change this url if working in test environments
        version = "v1pre3")
