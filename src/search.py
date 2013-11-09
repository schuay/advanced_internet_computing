import getopt
import json
import signal
import sys

from datetime import datetime
from twython import Twython

CREDENTIALS_FILE = 'credentials.txt'

if __name__ == '__main__':
    search_args = { "q": "The Beatles"
                  , "until": datetime.today().strftime("%Y-%m-%d")
                  , "lang": 'en'
                  , "result_type": 'recent'
                  , "count": 100
                  }

    opts, args = getopt.getopt(sys.argv[1:], "hm:c:q:u:")
    for o, a in opts:
        if o == "-c":
            search_args["count"] = int(a)
        elif o == "-m":
            search_args["max_id"] = int(a)
        elif o == "-q":
            search_args["q"] = a
        elif o == "-u":
            search_args["until"] = a
        else:
            print "You're on your own..."
            sys.exit(0)

    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.loads(f.read())

    twitter = Twython(
        credentials['APP_KEY'],
        credentials['APP_SECRET'],
        credentials['TOKEN_KEY'],
        credentials['TOKEN_SECRET'])

    # https://dev.twitter.com/docs/api/1.1/get/search/tweets
    tweets = twitter.search(**search_args)

    for tweet in tweets["statuses"]:
        print tweet["text"], tweet["created_at"], tweet["id"]
    print tweets["search_metadata"]
