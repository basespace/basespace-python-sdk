"""
Copyright 2012 Illumina

    Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import time
import helper
import webbrowser 
import cPickle as Pickle
import os

"""
Demonstrates the basic BaseSpace authentication process The work-flow is as follows: 
scope-request -> user grants access -> browsing data. The scenario is demonstrated both for device and web-based apps.

Further we demonstrate how a BaseSpaceAPI instance may be preserved across multiple http-request for the same app session using 
python's pickle module.

NOTE: You will need to fill client values for your app below
"""


# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = ""
client_secret              = ""
AppSessionId               = ""
# test if client variables have been set
helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'AppSessionId':AppSessionId}) 

BaseSpaceUrl               = 'https://api.basespace.illumina.com/'
version                    = 'v1pre3'


BSapi = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl, version, AppSessionId)

# First, get the verification code and uri for scope 'browse global'
deviceInfo = BSapi.getVerificationCode('browse global')
print "\n URL for user to visit and grant access: "
print deviceInfo['verification_with_code_uri']

## PAUSE HERE
# Have the user visit the verification uri to grant us access
print "\nPlease visit the uri within 15 seconds and grant access"
print deviceInfo['verification_with_code_uri']
webbrowser.open_new(deviceInfo['verification_with_code_uri'])
time.sleep(15)
## PAUSE HERE

# Once the user has granted us access to objects we requested, we can
# get the basespace access token and start browsing simply by calling updatePriviliges
# on the baseSpaceApi instance.
code = deviceInfo['device_code']
BSapi.updatePrivileges(code)

# As a reference the provided access-token can be obtained from the BaseSpaceApi object
print "\nMy Access-token:"
print BSapi.getAccessToken()


# Let's try and grab all available genomes with our new api! 
allGenomes  = BSapi.getAvailableGenomes()
print "\nGenomes \n" + str(allGenomes)


# If at a later stage we wish to initialize a BaseSpaceAPI object when we already have
# an access-token from a previous sessions, this may simply be done by initializing the BaseSpaceAPI
# object using the key-word AccessToken.
myToken = BSapi.getAccessToken()
BSapi = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl, version, AppSessionId, AccessToken=myToken)
print "\nA BaseSpaceAPI instance initialized with an access-token: "
print BSapi 

#################### Web-based verification #################################
# The scenario where the authentication is done through a web-browser

BSapiWeb = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl, version, AppSessionId)
userUrl= BSapiWeb.getWebVerificationCode('browse global','http://localhost',state='myState')

print "\nHave the user visit:"
print userUrl

webbrowser.open_new(userUrl)

# Once the grant has been given you will be redirected to a url looking something like this
# http://localhost/?code=<MY DEVICE CODE FROM REDICRECT>&state=myState&action=oauthv2authorization
# By getting the code parameter from the above http request we can now get our access-token

myCode = '<MY DEVICE CODE FROM REDICRECT>'
#BSapiWeb.updatePrivileges(myCode)


#################### Storing BaseSpaceApi using python's pickle module #################################
"""
It may sometimes be useful to preserve certain api objects across a series of http requests from the same user-session. 
Here we demonstrate how the Python pickle module may be used to achieve this end.

The example will be for an instance of BaseSpaceAPI, but the same technique may be used for BaseSpaceAuth.
In fact, a single instance of BaseSpaceAuth would be enough for a single App and could be shared by all http-requests, as the identity of 
this object is only given by the client_key and client_secret. 

(There is, of course, no problem in having multiple identical BaseSpaceAuth instances).
"""

# Get current user
user= BSapi.getUserById('current')
print user
print BSapi

#### Here some work goes on

# now we wish to store the API object for the next time we get a request in this session
# make a file to store the BaseSpaceAPi instance in, for easy identification we will name this by any id that may be used for identifying
# the session again.
mySessionId = BSapi.appSessionId + '.pickle'
f = open(mySessionId,'w')
Pickle.dump(BSapi, f)
f.close()

# Imagine the current request is done, we will simulate this by deleting the api instance  
BSapi = None
print "\nTry printing the removed API, we get: " + str(BSapi)


# Next request in the session with id = id123 comes in
# We'll check if if there already is a BaseSpaceAPI stored for the session
if os.path.exists(mySessionId):
    f = open(mySessionId)
    BSapi = Pickle.load(f)
    f.close()
    print 
    print "We got the API back!"
    print BSapi
else:
    print "Looks like we haven't stored anything for this session yet"
    # create a BaseSpaceAPI for the first time

