from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import os
import helper #@UnresolvedImport

"""
This script demonstrates how to create a new analysis object, change its state
and upload result files to it and download files from it.  
"""
# REST server information and user access token 
server          = 'https://api.cloud-endor.illumina.com/'
version         = 'v1pre2'
access_token    = ''    

# check if access-token has been set
if not access_token:  
    access_token = helper.readToken()
    if not access_token:
        raise Exception("Access-token not set, please specify the access token in the " + os.path.realpath(__file__))


## First, create a client for making calls for this user session 
myBaseSpaceAPI   = BaseSpaceAPI(AccessToken=access_token,apiServer= server + version)
#
## Now we'll do some work of our own. First get a project to work on
## we'll need write permission, for the project we are working on
## meaning we will need get a new token and instantiate a new BaseSpaceAPI  
p = myBaseSpaceAPI.getProjectById('89')
# A short-cut for getting a scope string if we already have a project-instance:
print p.getAccessStr(scope='write')
# or simply
p.getAccessStr()

# Assuming we now have write access for the project
# we will list the current analyses for the project 
ana = p.getAnalyses(myBaseSpaceAPI)
print "\nThe current analyses are \n" + str(ana)

# now let's do some work!
# to create an analysis for a project, simply give the name and description
analysis = p.createAnalysis(myBaseSpaceAPI,"My very first analysis!!","This is my analysis")
print "\nSome info about our new analysis"
print analysis
print analysis.Id
print analysis.Status
# we can change the status of out analysis and add a status-summary as follows
analysis.setStatus(myBaseSpaceAPI,'completed',"We worked hard.")
print "\nAfter a change of status we get\n" + str(analysis)

### Let's list the analyses again and see if our new object shows up 
ana = p.getAnalyses(myBaseSpaceAPI)
print "\nThe updated analyses are \n" + str(ana)

## Now we will make another analysis 
## and try to upload some files to it
analysis2 = p.createAnalysis(myBaseSpaceAPI,"My second analysis","This one I will upload to")
analysis2.uploadFile(myBaseSpaceAPI, '/home/mkallberg/Desktop/testFile2.txt', 'BaseSpaceTestFile.txt', '/mydir/', 'text/plain')
print "\nMy analysis number 2 \n" + str(analysis2)
#
## let's see if our new file made it
analysisFiles = analysis2.getFiles(myBaseSpaceAPI)
print "\nThese are the files in the analysis"
print analysisFiles
f = analysisFiles[-1]

# we can even download our newly uploaded file
f = myBaseSpaceAPI.getFileById('7331136')
f.downloadFile(myBaseSpaceAPI,'/home/mkallberg/Desktop/')