from datetime import datetime
from pymongo import MongoClient

"""A (somewhat) generic store for tweets which can be queried by
key words and time ranges, and filled with a list of tweets."""
class TweetStore:

    """Initializes this instance with the specified database name."""
    def __init__(self, dbname):
        self._dbname = dbname

        self._client = MongoClient()
        self._collection = self._client[dbname].test_collection

    """Retrieves a list of tweets in twython's format from the database.
    Tweets are filtered by the specified keywords and time range.
    keywords is a list of strings.
    start and end are datetime objects."""
    def get(self, keywords, start, end):
        c = self._collection
        return c.find({
            "text": {"$regex": ".*Call.*"}})

    """Stores the specified tweets into the database."""
    def put(self, tweets):
        self._collection.insert(tweets)

    """Performs final cleanups such as closing the DB connection."""
    def close(self):
        self._client.close()

if __name__ == "__main__":
    ts = TweetStore("test_database")
    for t in ts.get([], datetime(2013, 1, 1), datetime(2999, 1, 1)):
        print t["text"]
        print type(t["created_at"])

