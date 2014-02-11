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
import os

"""
This script demonstrates how to create a new AppResults object, change its state
and upload result files to it and download files from it.  
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



# Now we'll do some work of our own. First get a project to work on
# we'll need write permission, for the project we are working on
# meaning we will need get a new token and instantiate a new BaseSpaceAPI  
p = myAPI.getProjectById('89')

# Assuming we have write access to the project
# we will list the current App Results for the project 
appRes = p.getAppResults(myAPI,statuses=['Running'])
print "\nThe current running AppResults are \n" + str(appRes)

# now let's do some work!
# to create an appResults for a project, simply give the name and description
appResults = p.createAppResult(myAPI,"testing","this is my results",appSessionId='')
print "\nSome info about our new app results"
print appResults
print appResults.Id
print "\nThe app results also comes with a reference to our AppSession"
myAppSession = appResults.AppSession
print myAppSession

# we can change the status of our AppSession and add a status-summary as follows
myAppSession.setStatus(myAPI,'needsattention',"We worked hard, but encountered some trouble.")
print "\nAfter a change of status of the app sessions we get\n" + str(myAppSession)
# we'll set our appSession back to running so we can do some more work
myAppSession.setStatus(myAPI,'running',"Back on track")


### Let's list all AppResults again and see if our new object shows up 
appRes = p.getAppResults(myAPI,statuses=['Running'])
print "\nThe updated app results are \n" + str(appRes)
appResult2 = myAPI.getAppResultById(appResults.Id)
print appResult2

## Now we will make another AppResult 
## and try to upload a file to it
appResults2 = p.createAppResult(myAPI,"My second AppResult","This one I will upload to")
appResults2.uploadFile(myAPI, '/home/mkallberg/Desktop/testFile2.txt', 'BaseSpaceTestFile.txt', '/mydir/', 'text/plain')
print "\nMy AppResult number 2 \n" + str(appResults2)

## let's see if our new file made it
appResultFiles = appResults2.getFiles(myAPI)
print "\nThese are the files in the appResult"
print appResultFiles
f = appResultFiles[-1]

# we can even download our newly uploaded file
f = myAPI.getFileById(f.Id)
f.downloadFile(myAPI,'/home/mkallberg/Desktop/')
