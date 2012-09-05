import sys
sys.path.append('/home/mkallberg/workspace/BaseSpacePy_v0.1/src/')
from BaseSpacePy.api.BaseSpaceAuth import BaseSpaceAuth
import helper
import webbrowser 
"""
This example script demonstrates a work-flow for web-based authentication.

NOTE: You will need to fill in client values for your app below
"""


# Initialize an authentication object using the key and secret from you app
# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = ""
client_secret              = ""
BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre2/'

#helper.checkClientVars({'client_key':client_key,'client_secret':client_secret}) 

BSauth = BaseSpaceAuth(client_key,client_secret,BaseSpaceUrl,version)
userUrl= BSauth.getWebVerificationCode('browse global','http://localhost',state='myState')

print "Have the user visit:"
print userUrl

webbrowser.open_new(userUrl)

# Once the grant has been given you will be redirected to a url looking something like this
# http://localhost/?code=<MY DEVICE CODE FROM REDICRECT>&state=myState&action=oauthv2authorization
# By getting the code parameter from the above http request we can now get our access-token

myCode = '<MY DEVICE CODE FROM REDICRECT>'

# Specifically, we can generate an access-token and request a BaseSpaceApi instance 
# with the newly generated token in one step
myAPI = BSauth.getBaseSpaceApi(myCode)
print myAPI

# Let's try and grab all available genomes with our new api!
allGenomes  = myAPI.getAvailableGenomes()
print "\nGenomes \n" + str(allGenomes)

# let's have a look at the access token
print "My access-token:"
print myAPI.getAccessToken()