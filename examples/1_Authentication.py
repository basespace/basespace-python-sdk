from BaseSpacePy.api.BaseSpaceAuth import BaseSpaceAuth
import time
import helper
import webbrowser 
"""
Demonstrates the basic BaseSpace authentication process
The work-flow is as follows: scope-request -> user grants access -> browsing data.

NOTE: You will need to fill client values for your app below
"""


# initialize an authentication object using the key and secret from you app
# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = ""
client_secret              = ""
BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre2/'



helper.checkClientVars({'client_key':client_key,'client_secret':client_secret}) 

BSauth = BaseSpaceAuth(client_key,client_secret,BaseSpaceUrl,version)

# First get verification code and uri for scope 'browse global'
deviceInfo = BSauth.getVerificationCode('browse global')

## PAUSE HERE
# Have the user visit the verification uri to grant us access
print "Please visit the uri within 15 seconds and grant access"
print deviceInfo['verification_with_code_uri']
webbrowser.open_new(deviceInfo['verification_with_code_uri'])
time.sleep(5)
## PAUSE HERE

# Get the access-token directly and instantiate an api yourself
#token = BSauth.getAccessToken(deviceInfo['device_code'])
#print "My token " + str(token)

# Alternatively we can generate an access-token and request a BaseSpaceApi instance 
# with the newly generated token in one step
myAPI = BSauth.getBaseSpaceApi(deviceInfo['device_code'])
print myAPI

# Let's try and grab all available genomes with our new api! 
allGenomes  = myAPI.getAvailableGenomes()
print "\nGenomes \n" + str(allGenomes)

# we'll just write out access token to the disk for use in later examples
helper.writeToken(myAPI.getAccessToken())