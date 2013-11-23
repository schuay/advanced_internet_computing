import gettweets
import json
import tweet

from aggregator import MeanAggregator
from classifier import Classifier
from datetime import datetime
from tweetstore import TweetStore

ID = "id"
KEYWORDS = "keywords"
START = "start"
END = "end"
SUBMITTED_AT = "submitted_at"
COMPLETED_AT = "completed_at"
RATING = "rating"
SAMPLE = "sample"

SAMPLE_SIZE = 10

"""Runs all steps needed to take a task to completion. In particular, these should be:
   retrieval of tweets matching the specified keywords and time range from the twitter API,
   followed by retrieval of matching tweets from our db cache, classifying said tweets,
   aggregating classifications, and finally updating the DB with our results."""
def run(task, db_name, classifier, aggregator):
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

    store = TweetStore(db_name)
    try:
        tweets = store.get(task[KEYWORDS],
                           task[START],
                           task[END])

        # Classify them.

        rated = []
        for t in tweets:
            s = classifier.classify(t)
            print ("%s -- sentiment: %s" % (t[tweet.TEXT],
                "positive" if (s == 1) else "negative"))
            aggregator.add(t, s)
            rated.append((t[tweet.TEXT], s))

        # Sample the most positive and most negative tweets.

        rated.sort(key = lambda t: t[1])

        if len(rated) <= 2 * SAMPLE_SIZE:
            sample = rated
        else:
            sample = rated[:SAMPLE_SIZE] + rated[-SAMPLE_SIZE:]
        rated = None

        # Fill in task details.

        task[SAMPLE] = sample
        task[RATING] = aggregator.get_sentiment()
        task[COMPLETED_AT] = datetime.utcnow()

        print task
        store.task_put(task)

    finally:
        store.close()
        store = None

def _get_credentials(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())
