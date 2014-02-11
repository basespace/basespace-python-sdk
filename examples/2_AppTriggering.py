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

from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import webbrowser
import time

"""
This script demonstrates how to retrieve the AppSession object produced 
when a user initiates an app. Further it's demonstrated how to automatically
generate the scope strings to request access to the data object (a project or a sample)
that the app was triggered to analyze.
"""

"""
NOTE: this example requires that you provide an appSessionId that was generated
from launching your app. If you don't provide this, you will get the following
exception message: 'Forbidden: App credentials do not match AppSession application'.
"""

"""
NOTE: You will need to provide the credentials for your app (available in the developer portal).
You can do this with a master config file (preferred), or by filling in values below.
"""
# If you're not using a config file, fill in you app's credentials here:
clientKey                 = ""
clientSecret              = ""
appSessionId              = ""
apiServer                 = 'https://api.basespace.illumina.com/' # or 'https://api.cloud-hoth.illumina.com/'
apiVersion                = 'v1pre3'



# First we will initialize a BaseSpace API object using our app information and the appSessionId
if clientKey:
    myAPI = BaseSpaceAPI(clientKey, clientSecret, apiServer, apiVersion, appSessionId)
else:
    myAPI = BaseSpaceAPI(profile='DEFAULT')

# Using the basespaceApi we can request the appSession object corresponding to the AppSession id supplied
myAppSession = myAPI.getAppSession()
print myAppSession

# An app session contains a referal to one or more appLaunchObjects which reference the data module
# the user launched the app on. This can be a list of projects, samples, or a mixture of objects  
print "\nType of data the app was triggered on can be seen in 'references'"
print myAppSession.References

# We can also get a handle to the user who started the AppSession
print "\nWe can get a handle for the user who triggered the app\n" + str(myAppSession.UserCreatedBy)

# Let's have a closer look at the appSessionLaunchObject
myReference =  myAppSession.References[0]
print "\nWe can get out information such as the href to the launch object:"
print myReference.HrefContent
print "\nand the specific type of that object:"
print myReference.Type


# Now we will want to ask for more permission for the specific reference object
print "\nWe can get out the specific project objects by using 'content':" 
myReference =  myReference.Content
print myReference
print "\nThe scope string for requesting read access to the reference object is:"
print myReference.getAccessStr(scope='write')

# We can easily request write access to the reference object so our App can start contributing analysis
# by default we ask for write permission and authentication for a device
#accessMap       = myAPI.getAccess(myReference,accessType='write')
# We may limit our request to read access only if that's all that is needed
#readAccessMaps  = myAPI.getAccess(myReference,accessType='read')

#print "\nWe get the following access map for the write request"
#print accessMap

## PAUSE HERE
# Have the user visit the verification uri to grant us access
#print "\nPlease visit the uri within 15 seconds and grant access"
#print accessMap['verification_with_code_uri']
#webbrowser.open_new(accessMap['verification_with_code_uri'])
#time.sleep(15)
## PAUSE HERE

# Once the user has granted us the access to the object we requested we can
# get the basespace access token and start browsing simply by calling updatePriviliges
# on the baseSpaceApi instance    
#code = accessMap['device_code']
#myAPI.updatePrivileges(code)
#print "\nThe BaseSpaceAPI instance was update with write privileges"
#print myAPI
