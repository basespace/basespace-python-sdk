import sys
sys.path.append('/home/mkallberg/workspace/basespace-python-sdk/src/')
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import time
import helper
import webbrowser 
"""
Demonstrates the basic BaseSpace authentication process
The work-flow is as follows: scope-request -> user grants access -> browsing data.

NOTE: You will need to fill client values for your app below
"""


# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = "16497134b4a84b9bb86df6c00087ba5b"
client_secret              = "907b6800ae4f4020807baf9eef0d5164"
AppSessionId               = "fc4e7338c4ed4a809ecb813d951c4b50"

# test if client variables have been set
#helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'AppSessionId':ApplicationActionId}) 

BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre3/'


helper.checkClientVars({'client_key':client_key,'client_secret':client_secret}) 

BSapi = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl+ version, AppSessionId)

# First get verification code and uri for scope 'browse global'
deviceInfo = BSapi.getVerificationCode('browse global')
print "\n URL for user to visit and grant access: "
print deviceInfo['verification_with_code_uri']

## PAUSE HERE
# Have the user visit the verification uri to grant us access
print "\nPlease visit the uri within 15 seconds and grant access"
print deviceInfo['verification_with_code_uri']
webbrowser.open_new(deviceInfo['verification_with_code_uri'])
time.sleep(5)
## PAUSE HERE

# Once the user has granted us access to objects we requested can
# get the basespace access token and start browsing simply by calling updatePriviliges
# on the baseSpaceApi instance    
code = deviceInfo['device_code']
BSapi.updatePrivileges(code)

# As a reference the provided access-token can be obtained from the BaseSpaceApi object
print "\nMy Access-token:"
print BSapi.getAccessToken()


# Let's try and grab all available genomes with our new api! 
allGenomes  = BSapi.getAvailableGenomes()
print "\nGenomes \n" + str(allGenomes)



#################### Web-based verification #################################
# The scenario where the authentication is done through a webbrowser


# Once the grant has been given you will be redirected to a url looking something like this
# http://localhost/?code=<MY DEVICE CODE FROM REDICRECT>&state=myState&action=oauthv2authorization
# By getting the code parameter from the above http request we can now get our access-token


