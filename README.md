INTRODUCTION	
=========================================

BaseSpacePy is a Python based SDK to be used in the development of Apps and scripts for working with Illumina's BaseSpace cloud-computing solution for next-gen sequencing data analysis. 

The primary purpose of the SDK is to provide an easy-to-use Python environment enabling developers to authenticate a user, retrieve data, and upload data/results from their own analysis to BaseSpace.

If you haven't already done so, you may wish to familiarize yourself with the general BaseSpace developers documentation (https://developer.basespace.illumina.com/) and create a new BaseSpace App to be used when working through the examples provided in 'examples' folder.


AUTHORS
=========================================

Morten Kallberg


REQUIREMENTS
=========================================

Python 2.6 with the packages 'urllib2', 'pycurl', and 'shutil' available.


INSTALL
=========================================

Version 0.1 of BaseSpacePy can be checked out here:

	git clone git@github.com:basespace/basespace-python-sdk.git

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


CHANGELOG
=========================================

v0.1
-----------------------------------------
 
Initial release of BaseSpacePy

COPYING / LICENSE
=========================================
 -

BUGS
=========================================
 - 
