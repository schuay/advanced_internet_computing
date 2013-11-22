import gettweets
import json
import tweet

from aggregator import MeanAggregator
from classifier import Classifier
from tweetstore import TweetStore

ID = "id"
KEYWORDS = "keywords"
START = "start"
END = "end"
SUBMITTED_AT = "submitted_at"
COMPLETED_AT = "completed_at"
RATING = "rating"
SAMPLE = "sample"

DBNAME = "tweets"

"""Runs all steps needed to take a task to completion. In particular, these should be:
   retrieval of tweets matching the specified keywords and time range from the twitter API,
   followed by retrieval of matching tweets from our db cache, classifying said tweets,
   aggregating classifications, and finally updating the DB with our results."""
def run(task, classifier, aggregator):
    credentials = _get_credentials("credentials.txt")

    # Fetch tweets from twitter.

    fetcher = gettweets.TweetFetcher(
                        credentials,
                        task[KEYWORDS],
                        task[START],
                        task[END])
    fetcher.run()
    fetcher = None

    # Retrieve tweets from db.

    store = TweetStore(DBNAME)
    try:
        tweets = store.get(task[KEYWORDS],
                           task[START],
                           task[END])
    finally:
        store.close()
        store = None

    # Classify them.

    for t in tweets:
        s = classifier.classify(t)
        print ("%s -- sentiment: %s" % (t[tweet.TEXT],
            "positive" if (s == 1) else "negative"))
        aggregator.add(t, s)

    # aggregator.get_sentiment()
    # TODO: Store result and intermediate stati in DB.
    # TODO: Sample some tweets randomly.

def _get_credentials(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())
