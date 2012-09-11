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
import helper
import os
"""
This script demonstrates how to access Samples and AppResults from a projects and how to work with the available 
file data for such instances. 
"""

# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = ""
client_secret              = ""
AppSessionId               = ""
accessToken                = ""
helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'AppSessionId':AppSessionId}) 

BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre3'

# First, create a client for making calls for this user session 
myAPI           = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl, version, AppSessionId,AccessToken=accessToken)
user            = myAPI.getUserById('current')
myProjects      = myAPI.getProjectByUser('current')


# Let's list all the AppResults and samples for these projects
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