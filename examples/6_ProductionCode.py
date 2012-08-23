from BaseSpacePy.api.BaseSpaceAuth import BaseSpaceAuth
import helper

"""
In this script we are putting it all together. We demonstrate a full work-flow using BaseSpacePy, including all of the following steps:
    1. Handle initial app-triggering event
    2. Requesting access to browse
    3. Requesting access to write to a specific project
    4. Reading some data from a VCF file that we wish to use in the generation of results from our App
    5. Creating an analysis
    6. Writing results files back to the analysis
    7. Marking the analysis as complete
    -------------------------------------
    8. Retrieving results from the completed analysis at a later time for the same user 
    
NOTE: You will need to fill client values for your app below and an application
"""

# initialize an authentication object using the key and secret from your app

# FILL IN WITH YOUR APP VALUES HERE!
client_key                 = ""
client_secret              = ""
ApplicationActionId        = ""


# test if the above client variables have been set correctly 
helper.checkClientVars({'client_key':client_key,'client_secret':client_secret,'ApplicationActionId':ApplicationActionId}) 

# TO-DO