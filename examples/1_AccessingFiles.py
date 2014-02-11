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
This script demonstrates how to access Samples and AppResults from a projects and how to work with the available 
file data for such instances. 
"""

"""
NOTE: The coverage and variants API calls below require access to a public 
dataset. Before running the example, first go to cloud-hoth.illumina.com,
login, click on Public Data, select the dataset named 'MiSeq B. cereus demo 
data', and click the Import button for the Project named 'BaseSpaceDemo'.
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
myBam = myAPI.getFileById('9895890')
print myBam
cov     = myBam.getIntervalCoverage(myAPI,'chr','1','100')
print cov 
try:
   covMeta = myBam.getCoverageMeta(myAPI,'chr')
except Exception as e:
    print "Coverage metadata may not be available for this BAM file: %s" % str(e)
else:
    print covMeta
#
## and a vcf file
myVCF = myAPI.getFileById('9895892')
varMeta = myVCF.getVariantMeta(myAPI)
print varMeta
var     = myVCF.filterVariant(myAPI,'chr','1', '25000') 
print var
