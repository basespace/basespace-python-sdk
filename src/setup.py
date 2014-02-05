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

from distutils.core import setup

setup(name='BaseSpacePy',
      summary='A Python SDK for connecting to Illumina BaseSpace data',
      author='Morten Kallberg',
      version='0.1.3',
      description="BaseSpacePy is a Python based SDK to be used in the development of Apps and scripts for working with \
       Illumina's BaseSpace cloud-computing solution for next-gen sequencing data analysis.\
      The primary purpose of the SDK is to provide an easy-to-use Python environment enabling\
       developers to authenticate a user, retrieve data, and upload data/results from their own analysis to BaseSpace.",
      author_email='',
      packages=['BaseSpacePy.api','BaseSpacePy.model','BaseSpacePy'],
)

# Warn use if dependent packages aren't installed
try:
    import pycurl
except:
    print "WARNING - please install required package 'pycurl'"
try:
    import dateutil
except:
    print "WARNING - please install required package 'python-dateutil'"

