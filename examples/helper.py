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
    