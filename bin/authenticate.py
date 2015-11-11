import json
import time
import sys

__author__ = 'psaffrey'

"""
Script that sets up the files in .basespace to contain access tokens.

One way uses the OAuth flow for web application authentication:

https://developer.basespace.illumina.com/docs/content/documentation/authentication/obtaining-access-tokens

to get an access token and put it in the proper place.

Also supported is obtaining session tokens (cookies), although these are not currently used.

"""

import getpass
import requests
import os
import ConfigParser

SESSION_AUTH_URI = "https://accounts.illumina.com/"
DEFAULT_CONFIG_NAME = "DEFAULT"
SESSION_TOKEN_NAME = "sessionToken"
ACCESS_TOKEN_NAME = "accessToken"
DEFAULT_API_SERVER = "https://api.basespace.illumina.com/"
API_VERSION = "v1pre3"
WAIT_TIME = 5.0

# these are the details for the BaseSpaceCLI app
# shared with BaseMount
CLIENT_ID = "ca2e493333b044a18d65385afaf8eb5d"
CLIENT_SECRET = "282b0f7d4e5d48dfabc7cdfe5b3156a6"
SCOPE="CREATE GLOBAL,BROWSE GLOBAL,CREATE PROJECTS,READ GLOBAL"

def basespace_session(username, password):
    s = requests.session()
    payload = {"UserName": username,
               "Password": password,
               "ReturnUrl": "http://developer.basespace.illumina.com/dashboard"}
    r = s.post(url=SESSION_AUTH_URI,
               params={'Service': 'basespace'},
               data=payload,
               headers={'Content-Type': "application/x-www-form-urlencoded"},
               allow_redirects=False)
    return s, r


def check_session_details():
    pass


def set_session_details(config_path):
    username = raw_input("username:")
    password = getpass.getpass()
    s, r = basespace_session(username, password)
    config = parse_config(config_path)
    import pdb; pdb.set_trace()
    config.set(DEFAULT_CONFIG_NAME, SESSION_TOKEN_NAME, )
    with open(config_path, "w") as fh:
        config.write(fh)


def parse_config(config_path):
    """
    parses the config_path or creates it if it doesn't exist

    :param config_path: path to config file
    :return: ConfigParser object
    """
    if not os.path.exists(config_path):
        config = ConfigParser.SafeConfigParser()
    else:
        config = ConfigParser.SafeConfigParser()
        config.read(config_path)
    return config

def construct_default_config(config, api_server):
    config.set(DEFAULT_CONFIG_NAME, "apiServer", api_server)

def set_oauth_details(config_path, api_server):
    OAUTH_URI = "%s%s/oauthv2/deviceauthorization" % (api_server, API_VERSION)
    TOKEN_URI = "%s%s/oauthv2/token" % (api_server, API_VERSION)
    s = requests.session()
    # make the initial request
    auth_payload = {
        "response_type" : "device_code",
        "client_id"     : CLIENT_ID,
        "scope"         : SCOPE,
    }
    try:
        r = s.post(url=OAUTH_URI,
                   data=auth_payload)
    except Exception as e:
        print "problem communicate with oauth server: %s" % str(e)
        raise
    # show the URL to the user
    auth_url = r.json()["verification_with_code_uri"]
    auth_code = r.json()["device_code"]
    print "please authenticate here: %s" % auth_url
    # poll the token URL until we get the token
    token_payload = {
        "client_id"     : CLIENT_ID,
        "client_secret" : CLIENT_SECRET,
        "code"          : auth_code,
        "grant_type"    : "device"
    }
    access_token = None
    while 1:
        # put the token into the config file
        r = s.post(url=TOKEN_URI,
                   data=token_payload)
        if r.status_code == 400:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(WAIT_TIME)
        else:
            sys.stdout.write("\n")
            access_token = r.json()["access_token"]
            break
    config = parse_config(config_path)
    construct_default_config(config, api_server)
    if not access_token:
        raise Exception("problem obtaining token!")
    print "Success!"
    config.set(DEFAULT_CONFIG_NAME, ACCESS_TOKEN_NAME, access_token)
    with open(config_path, "w") as fh:
        config.write(fh)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Derive BaseSpace authentication details")

    parser.add_argument('-c', '--configname', type=str, dest="configname", default="default", help='name of config')
    parser.add_argument('-s', '--sessiontoken', default=False, action="store_true",
                        help='do session auth, instead of regular auth')
    parser.add_argument('-a', '--api-server', default=DEFAULT_API_SERVER, help="choose backend api server")

    args = parser.parse_args()

    # cross platform way to get home directory
    home = os.path.expanduser("~")
    config_path = os.path.join(home, ".basespace", "%s.cfg" % args.configname)


    if args.sessiontoken:
        set_session_details(config_path)
    else:
        try:
            if os.path.exists(config_path):
                print "config path already exists; not overwriting (%s)" % config_path
                sys.exit(1)
            set_oauth_details(config_path, args.api_server)
        except Exception as e:
            print "authentication failed!"
            raise
