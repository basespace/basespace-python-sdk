INTRODUCTION	
=========================================

BaseSpacePy is a Python based SDK to be used in the development of Apps and scripts for working with Illumina's BaseSpace cloud-computing solution for next-gen sequencing data analysis. 

The primary purpose of the SDK is to provide an easy-to-use Python environment enabling developers to authenticate a user, retrieve data, and upload data/results from their own analysis to BaseSpace.

If you haven't already done so, you may wish to familiarize yourself with the general BaseSpace developers documentation (https://developer.basespace.illumina.com/) and create a new BaseSpace App to be used when working through the examples provided in 'examples' folder.


AUTHORS
=========================================

Morten Kallberg
Eric Smith


REQUIREMENTS
=========================================

Python 2.6 with the packages 'pycurl', and 'python-dateutil' installed. You can install these on Ubuntu with 'apt-get install python-pycurl' and 'apt-get install python-dateutil'.


INSTALL
=========================================

BaseSpacePy can be checked out here:

	git clone https://github.com/basespace/basespace-python-sdk.git

To install 'BaseSpacePy' run the 'setup.py' script in the main directory (for a global install you will need to run this command with root privileges):

	cd basespace-python-sdk/src
	python setup.py install

If you do not have root access, you may use the --prefix to specify the install dir (make sure this dir is in your PYTHONPATH):

	python setup.py install --prefix=/folder/in/my/pythonpath

For more install options type: 

	python setup.py --help

Alternatively you may include the src directory in your PYTHONPATH by:

	export PYTHONPATH=$PYTHONPATH:/my/path/basespace-python-sdk/src

or add it to the PYTHONPATH at the top of your Python scripts using BaseSpacePy:

	import sys
	sys.path.append('/my/path/basespace-python-sdk/src')
	import BaseSpacePy

To test that everything is working as expected, launch a Python prompt and try importing 'BaseSpacePy': 

	mkallberg@ubuntu:~/$ python
	>>> import BaseSpacePy


GETTING STARTED
=========================================
For most API calls, you will need credentials from an app. To create an app, go to the [BaseSpace developer portal](https://developer.basespace.illumina.com/) and create one. Naviagate to the Credentials tab of your app in the developer portal.

You can 1) store your credentials in a config file or 2) provide them as arguments to methods. To use a config file, create a file in your home directory named '.basespacepy.cfg'. Make this file readable and writeable by only you ('chmod 600 ~/.basespacepy.cfg'). Then add the following content to the file, and add your app's credentials (appSessionId is not required for many methods):

	[DEFAULT]
	name = my new app
	clientKey =
	clientSecret =
	accessToken =
	appSessionId =
	apiServer = https://api.basespace.illumina.com/
	apiVersion = v1pre3

Now you can get started quickly with code such as:

	from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
	myAPI = BaseSpaceAPI()
	user = myAPI.getUserById('current')


CHANGELOG
=========================================

v 0.2
-----------------------------------------
- Added support for large-file (multipart) upload and download.
- Added methods to get a Run's Files or Samples
- Added support for a config file to store credentials
- Made consistent all queryParameter arguments to accept objects (not dicts)
- Added unit tests for all methods (except Billing and some MultipartFileTransfer methods)

v 0.1.2
-----------------------------------------
- Added support for getting item Properties
- Added support for purchases and refunds
- Added use of os.path.join when forming path in file-download from a Sample
- Added support for custom http-timeouts in the BaseSpaceAPI class
- Added link to Sample class in AppResult class
- Introduced method getAppSessionByID in BaseSpaceAPI
- Introduced the new fields IsPairedEnd, Read1, Read2, NumReadsRaw, and NumReadsPF to the Sample class
- Introduced new date format

v 0.1.1
-----------------------------------------
Update to support changes in BaseSpace REST specification version v1pre3. Specific changes are:
- AppLaunchResponse is now AppSessionResponse
- AppLaunch is now AppSession and has been updated to include the fields additional fields
- Analysis is now AppResult
- An Application object has been added to the data model as part of the new AppSession
- AppResults (previously Analysis) do no longer have a setStatus method, this logic has been moved to the AppSession class   


v 0.1
-----------------------------------------
 
Initial release of BaseSpacePy

COPYING / LICENSE
=========================================

See License.txt in the basespace-python-sdk directory for details on licensing and distribution.

KNOWN BUGS
=========================================
