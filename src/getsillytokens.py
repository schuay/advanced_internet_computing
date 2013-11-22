#!/bin/python2

import json
import pprint
import sys

from twython import Twython

CREDENTIALS_FILE = 'credentials.txt'

if __name__ == '__main__':
    sys.stdout.write("Enter app key: ")
    appKey = sys.stdin.readline().strip()
    sys.stdout.write("Enter app secret: ")
    appSecret = sys.stdin.readline().strip()

    twitter = Twython(appKey, appSecret)

    auth = twitter.get_authentication_tokens()
    tokenKey = auth['oauth_token']
    tokenSecret = auth['oauth_token_secret']

    print "Visit this URL to get your PIN:"
    print auth['auth_url']

    sys.stdout.write("Enter the PIN: ")
    oauth_verifier = sys.stdin.readline().strip()

    twitter = Twython(appKey, appSecret,
                  tokenKey, tokenSecret)

    final_step = twitter.get_authorized_tokens(oauth_verifier)
    tokenKey = final_step['oauth_token']
    tokenSecret = final_step['oauth_token_secret']

    credentials = { 'APP_KEY': appKey
                  , 'APP_SECRET': appSecret
                  , 'TOKEN_KEY': tokenKey
                  , 'TOKEN_SECRET': tokenSecret
                  }

    pprint.pprint(credentials)

    with open(CREDENTIALS_FILE, 'w') as f:
        f.write(json.dumps(credentials))
    
    print "Credentials written to %s" % CREDENTIALS_FILE
