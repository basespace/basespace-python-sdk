from BaseSpacePy.api.BaseSpaceAuth import BaseSpaceAuth
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
client_key                 = ""
client_secret              = ""
ApplicationActionId        = ""

# test if client variables have been set
helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'AppSessionId':ApplicationActionId}) 

BaseSpaceUrl               = 'https://api.cloud-endor.illumina.com/'
version                    = 'v1pre2/'

# First we will initialize a BaseSpace authentication object
BSauth = BaseSpaceAuth(client_key,client_secret,BaseSpaceUrl,version)

# By supplying the application trigger id we can get out an AppLaunch object
triggerObj = BSauth.getAppTrigger(ApplicationActionId)
print str(triggerObj)

# We can get the type of object the app was triggered on by using 
# where trigger type is a list with two item, the first a string taking the one of the values ('Projects','Samples','Analyses')
# and the second a list of the objects of that type
triggerType = triggerObj.getLaunchType()
print "\nType of data the app was triggered on"
print triggerType
print "\nWe can get a handle for the user who triggered the app\n" + str(triggerObj.User)

# Now we will want to ask for more permission for the specific trigger object
triggerObj = triggerType[1][-1]
print "\nThe scope string for requesting write access to the trigger object is:"
print triggerObj.getAccessStr(scope='write')