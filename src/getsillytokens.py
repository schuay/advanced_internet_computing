#!/bin/python2

from twython import Twython
import sys

if __name__ == '__main__':
    sys.stdout.write("Enter app key: ")
    appKey = sys.stdin.readline().strip()
    sys.stdout.write("Enter app secret: ")
    appSecret = sys.stdin.readline().strip()

    twitter = Twython(appKey, appSecret)

    auth = twitter.get_authentication_tokens()
    tokenKey = auth['oauth_token']
    tokenSecret = auth['oauth_token_secret']

    print "Direct your user to this URL and have her/him give you the PIN:"
    print auth['auth_url']

    sys.stdout.write("Enter the PIN: ")
    oauth_verifier = sys.stdin.readline().strip()

    twitter = Twython(appKey, appSecret,
                  tokenKey, tokenSecret)

    final_step = twitter.get_authorized_tokens(oauth_verifier)
    tokenKey = final_step['oauth_token']
    tokenSecret = final_step['oauth_token_secret']

    print "APP_KEY = \"" + appKey + "\""
    print "APP_SECRET = \"" + appSecret + "\""
    print "TOKEN_KEY = \"" + tokenKey + "\""
    print "TOKEN_SECRET = \"" + tokenSecret + "\""
