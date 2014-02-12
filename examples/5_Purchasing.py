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
import os
import webbrowser
import time
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from BaseSpacePy.api.BillingAPI import BillingAPI
from BaseSpacePy.model.QueryParametersPurchasedProduct import QueryParametersPurchasedProduct as qpp
"""
This example demonstrates the billing methods of BaseSpace.

Below a purchase is created, requiring the user to click 'Purchase' in a web
browser. The purchase is then refunded, and the purchase is again retrieved
via the API using the purchase id and tags, which are used by developers
to help clarify exactly what was purchased.

NOTE: You will need to fill client values for your app below
"""
# cloud-hoth
client_key                 = "" # from dev portal app Credentials tab
client_secret              = "" # from dev portal app Credentials tab
AppSessionId               = "" # from launching an app
accessToken                = "" # from oauth2
BaseSpaceUrl               = "" # eg. "https://api.cloud-hoth.illumina.com/"
BaseSpaceStoreUrl          = "" # eg. "https://hoth-store.basespace.illumina.com/"
version                    = "" # eg. 'v1pre3'
product_id                 = "" # from dev portal Pricing tab

if not client_key:
    raise Exception("Please fill in client values (in the script) before running the script")

# Create a client for making calls for this user session 
billAPI   = BillingAPI(BaseSpaceStoreUrl, version, AppSessionId, AccessToken=accessToken)

# create a non-consumable purchase
#purch = billAPI.createPurchase([{'id':product_id,'quantity':4 }])

# create a consumable purchase, and associated it with an AppSession
# also add tags to provide (fake) details about the purchase
print "\nCreating purchase\n"
purch = billAPI.createPurchase({'id':product_id,'quantity':4, 'tags':["test","test_tag"] }, AppSessionId)

# record the purchase Id and RefundSecret for refunding later
purchaseId = purch.Id
refundSecret = purch.RefundSecret

print "Now complete the purchase in your web browser"
print "CLOSE the browser window/tab after you click 'Purchase' (and don't proceed into the app)"
time.sleep(3)
## PAUSE HERE
print "Opening: " + purch.HrefPurchaseDialog
webbrowser.open_new(purch.HrefPurchaseDialog)
print "Waiting 30 seconds..."
time.sleep(30)
## PAUSE HERE

print "\nConfirm the purchase"
post_purch = billAPI.getPurchaseById(purchaseId)
print "The status of the purchase is now: " + post_purch.Status

print "\nRefunding the Purchase"
# note we must use the same access token that was provided used for the purchase
refunded_purchase = billAPI.refundPurchase(purchaseId, refundSecret, comment='the product did not function well as a frisbee')

print "\nGetting all purchases for the current user with the tags we used for the purchase above"
purch_prods = billAPI.getUserProducts(Id='current', queryPars=qpp( {'Tags':'test,test_tag'} ))
if not len(purch_prods):
    print "\nHmmm, didn't find any purchases with these tags. Did everything go OK above?\n"
else:
    print "\nFor the first of these purchases:\n"
    print "Purchase Name: " + purch_prods[0].Name
    print "Purchase Price: " + purch_prods[0].Price
    print "Purchase Quantity: " + purch_prods[0].Quantity
    print "Tags: " + str(purch_prods[0].Tags)

    # Get the refund status of the purchase
    print "\nGetting the (refunded) Purchase we just made"
    get_purch = billAPI.getPurchaseById(purch_prods[0].PurchaseId)
    print "Refund Status: " + get_purch.RefundStatus + "\n"
