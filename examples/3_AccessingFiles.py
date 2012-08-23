from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import helper
import os
"""
This script demonstrates how to access samples and analysis from a projects
and how to work with the available file data for such instances. 
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
user        = myAPI.getUserById('current')
myProjects   = myAPI.getProjectByUser('current')


# Let's list all the analyses and samples for these projects
for singleProject in myProjects:
    print "# " + str(singleProject)
    analyses = singleProject.getAnalyses(myAPI)
    print "    The analysis for project " + str(singleProject) + " are \n\t" + str(analyses)
    samples = singleProject.getSamples(myAPI)
    print "    The samples for project " + str(singleProject) + " are \n\t" + str(samples)

# we'll take a further look at the files belonging to the sample and 
#analyses from the last project in the loop above 
for a in analyses:
    print "# " + a.Id
    ff = a.getFiles(myAPI)
    print ff
for s in samples:
    print "Sample " + str(s)
    ff = s.getFiles(myAPI)
    print ff


# Now let's do some work with files 
# we'll grab a BAM by id and get the coverage for an interval + accompanying meta-data 
myBam = myAPI.getFileById('2150156')
print myBam
cov     = myBam.getIntervalCoverage(myAPI,'chr2','1','20000')
print cov 
covMeta = myBam.getCoverageMeta(myAPI,'chr2')
print covMeta

# and a vcf file
myVCF = myAPI.getFileById('2150158')
#Let's get the variant meta info 
varMeta = myVCF.getVariantMeta(myAPI)
print varMeta
var     = myVCF.filterVariant(myAPI,'2','1', '11000') 
print var