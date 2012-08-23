import sys
import os
import cPickle as Pickle
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import helper

"""
It may sometimes be useful to preserve certain api objects across a series of http requests from the same user
and for the same App. Here we demonstrate how the Python pickle module may be used to achieve this end.
The example will be for an instance of BaseSpaceAPI, but the same technique may be used for BaseSpaceAuth.
In fact, a single instance of BaseSpaceAuth would be enough for a single App and could be shared by all http-requests, as the identity of 
this object is only given by the client_key and client_secret. 

(There is, of course, no problem in having multiple identical BaseSpaceAuth instances)
"""

# REST server information and user access token 
server          = 'https://api.cloud-endor.illumina.com/'
version         = 'v1pre2'
access_token    = ''                                        #set access token here


# check if access-token has been set
if not access_token:  
    access_token = helper.readToken()
    if not access_token:
        raise Exception("Access-token not set, please specify the access token in the " + os.path.realpath(__file__))

# First, create a client for making calls for this user session 
myAPI   = BaseSpaceAPI(AccessToken=access_token,apiServer= server + version)
# Get current user
user= myAPI.getUserById('current')
print user
print myAPI

#### Here some work goes on

# now we wish to store the api object for the next time we get a request in this session
# make a file to store the BaseSpaceAPi instance in, for easy identification we will name this by any id that may be used for identifying
# the session again.
mySessionId = 'id123.pickle'
f = open(mySessionId,'w')
Pickle.dump(myAPI, f)
f.close()

# Imagine the current request is done, we will simulate this by deleting the api instance  
myAPI = None
print "\nTry printing the removed API, we get: " + str(myAPI)


# Next request in the session with id = id123 comes in
# We'll check if if there already is a BaseSpaceAPI stored for the session
if os.path.exists(mySessionId):
    f = open(mySessionId)
    myAPI = Pickle.load(f)
    f.close()
    print 
    print "We got the API back!"
    print myAPI
else:
    print "Looks like we haven't stored anything for this session yet"
    # create a BaseSpaceAPI for the first time

