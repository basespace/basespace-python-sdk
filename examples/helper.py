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

# Some small helper methods for the example scripts
import os

def writeToken(token):
    path = "/".join(os.path.realpath(__file__).split('/')[:-1]) + '/'
    f = open(path + 'mytoken.txt','w')
    f.write(token)
    f.close()
    
def readToken():
    path = "/".join(os.path.realpath(__file__).split('/')[:-1]) + '/'
    try:
        token = open(path + 'mytoken.txt').read()
        return token
    except:
        return ''
    
def checkClientVars(varDict):
    for k in varDict.keys():
        if not varDict[k]: 
            print  '\n' + k + " has not been set! Please specify this variable from your BaseSpace App to run this example\n"
            raise Exception('\n\n!!' + k + " has not been set! Please specify this variable from your BaseSpace App to run this example.\n")
    return 1
    