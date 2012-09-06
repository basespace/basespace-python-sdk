from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import helper
import os
"""
This script demonstrates how to access samples and analysis from a projects
and how to work with the available file data for such instances. 
"""

# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = "16497134b4a84b9bb86df6c00087ba5b"
client_secret              = "907b6800ae4f4020807baf9eef0d5164"
appSessionId               = "fc4e7338c4ed4a809ecb813d951c4b50"
accessToken                = "31af080b256e4433bbf3e75a26a4aa12"
# test if client variables have been set
#helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'AppSessionId':ApplicationActionId}) 

BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre3'

# First, create a client for making calls for this user session 
myAPI   = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl, version, appSessionId,AccessToken=accessToken)
user        = myAPI.getUserById('current')
myProjects   = myAPI.getProjectByUser('current')


# Let's list all the analyses and samples for these projects
for singleProject in myProjects:
    print "# " + str(singleProject)
    appResults = singleProject.getAppResults(myAPI)
    print "    The App results for project " + str(singleProject) + " are \n\t" + str(appResults)
    samples = singleProject.getSamples(myAPI)
    print "    The samples for project " + str(singleProject) + " are \n\t" + str(samples)
#
## we'll take a further look at the files belonging to the sample and 
##analyses from the last project in the loop above 
for a in appResults:
    print "# " + a.Id
    ff = a.getFiles(myAPI)
    print ff
for s in samples:
    print "Sample " + str(s)
    ff = s.getFiles(myAPI)
    print ff


## Now let's do some work with files 
## we'll grab a BAM by id and get the coverage for an interval + accompanying meta-data 
myBam = myAPI.getFileById('2150156')
print myBam
cov     = myBam.getIntervalCoverage(myAPI,'chr2','1','20000')
print cov 
covMeta = myBam.getCoverageMeta(myAPI,'chr2')
print covMeta
#
## and a vcf file
myVCF = myAPI.getFileById('2150158')
##Let's get the variant meta info 
varMeta = myVCF.getVariantMeta(myAPI)
print varMeta
var     = myVCF.filterVariant(myAPI,'2','1', '11000') 
print var