import sys
sys.path.append('/home/mkallberg/workspace/BaseSpacePy_v0.1/src/')
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI #@UnresolvedImport
import helper #@UnresolvedImport
import time
import os

"""
This script demonstrates how to handle multi-part file upload using multiple threads
to speed up the transfer process, further it demonstrates the ability to pause the upload
and query the state of the upload as it is in progresses. 
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
    

# First, create a client for making calls for this user session 
myAPI   = BaseSpaceAPI(AccessToken=access_token,apiServer= server + version)

# we'll get an analysis object that we know we have access to
a = myAPI.getAnalysisById('77077')
print a

# Now initialize a multi-part upload object
myMpu = a.uploadMultipartFile(myAPI,'/home/mkallberg/Desktop/multi/chr21_test.bam','chr21_test.bam','','application/zip',tempDir='',partSize=25,cpuCount=1,verbose=1)
print "Status is " + myMpu.Status


# Unlike a single part upload, we need to explicitly start the transfer
# returnOnFinish=1
myMpu.startUpload(returnOnFinish=1)

# alter
#myMpu = a.uploadMultipartFile(myAPI,'/home/mkallberg/Desktop/multi/chr21_test.bam','chr21_test.bam','','application/zip',tempDir='',partSize=5,cpuCount=8,verbose=1)
#print "Status is " + myMpu.Status
#myMpu.startUpload()

#i=0
#while not myMpu.hasFinished():
#    print myMpu
##    if i==10:
##        myMpu.pauseUpload()
##    if i==20:
##        myMpu.startUpload()
#    i +=1
#    time.sleep(1)



#a.uploadMultipartFile(myAPI,'/home/mkallberg/Desktop/multi/chr21_test.bam','chr21_test.bam','','application/bam',verbose=1)
