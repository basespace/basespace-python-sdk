from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
import helper

"""
This script demonstrates how to retrieve the app launch object produced 
when a user initiates an app. Further it's demonstrated how to automatically
generate the scope strings to request access to the data object (be it a project, sample, or analysis)
that the app was triggered to analyse. 

NOTE: You will need to fill client values for your app below
"""

# initialize an authentication object using the key and secret from your app

# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = "16497134b4a84b9bb86df6c00087ba5b"
client_secret              = "907b6800ae4f4020807baf9eef0d5164"
AppSessionId               = "fc4e7338c4ed4a809ecb813d951c4b50"

# test if client variables have been set
#helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'AppSessionId':ApplicationActionId}) 

BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre3/'

# First we will initialize a BaseSpace API object using our app information and the appSessionId
BSapi = BaseSpaceAPI(client_key, client_secret, BaseSpaceUrl+ version, AppSessionId)

# Using the basespaceApi we can request the appSession object corresponsing to the appsession id supplied
myAppSession = BSapi.getAppSession()
print myAppSession

# An app session contains a referal to one or more appLaunchObjects which reference the data the user module
# the user launched the app on. This can be a list of projects, samples, or a mixture of objects  
print "\nType of data the app was triggered on can be seen in 'references'"
print myAppSession.References

# We can also get a handle to the user who started the appsession
print "\nWe can get a handle for the user who triggered the app\n" + str(myAppSession.UserCreatedBy)

# Let's have a closer look at the appSessionLaunchObject
myReference =  myAppSession.References[0]
print "\nWe can get out information such as the href to the launch object:"
print myReference.HrefContent
print "\nand the specific type of that object:"
print myReference.Type



# Now we will want to ask for more permission for the specific reference object

print "\nWe can get out the specific project objects by using 'content':" 
myProject =  myReference.Content
print myProject
print "\nThe scope string for requesting write access to the reference object is:"
print myProject.getAccessStr(scope='write')