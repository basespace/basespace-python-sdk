from distutils.core import setup

setup(name='BaseSpacePy',
      summary='A Python SDK for connecting to Illumina BaseSpace data',
      author='Morten Kallberg',
      version='0.1.1',
      description="BaseSpacePy is a Python based SDK to be used in the development of Apps and scripts for working with \
       Illumina's BaseSpace cloud-computing solution for next-gen sequencing data analysis.\
      The primary purpose of the SDK is to provide an easy-to-use Python environment enabling\
       developers to authenticate a user, retrieve data, and upload data/results from their own analysis to BaseSpace.",
      author_email='',
      packages=['BaseSpacePy.api','BaseSpacePy.model','BaseSpacePy'],
)
