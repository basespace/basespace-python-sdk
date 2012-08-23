from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import os
import helper 

"""
This script demonstrates basic browsing of BaseSpace objects once an access-token
for global browsing has been obtained. 
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

# First, let's grab the genome with id=4
myGenome    = myAPI.getGenomeById('4')
print "\nThe Genome is " + str(myGenome)
print "We can get more information from the genome object"
print 'Id: ' + myGenome.Id
print 'Href: ' + myGenome.Href
print 'DisplayName: ' + myGenome.DisplayName

# Get a list of all genomes
allGenomes  = myAPI.getAvailableGenomes()
print "\nGenomes \n" + str(allGenomes)

# Let's have a look at the current user
user        = myAPI.getUserById('current')
print "\nThe current user is \n" + str(user)

# Now list the projects for this user
myProjects   = myAPI.getProjectByUser('current')
print "\nThe projects for this user are \n" + str(myProjects)

# We can also achieve this by making a call using the 'user instance'
myProjects2 = user.getProjects(myAPI)
print "\nProjects retrieved from the user instance \n" + str(myProjects2)

# List the runs available for the current user
runs = user.getRuns(myAPI)
print "\nThe runs for this user are \n" + str(runs)

# In the same manner we can get a list of accessible user runs
runs = user.getRuns(myAPI)
print "\nRuns retrieved from user instance \n" + str(runs)