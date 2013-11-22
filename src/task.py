ID = "id"
KEYWORDS = "keywords"
START = "start"
END = "end"
SUBMITTED_AT = "submitted_at"
COMPLETED_AT = "completed_at"
RATING = "rating"
SAMPLE = "sample"

"""Runs all steps needed to take a task to completion. In particular, these should be:
   retrieval of tweets matching the specified keywords and time range from the twitter API,
   followed by retrieval of matching tweets from our db cache, classifying said tweets,
   aggregating classifications, and finally updating the DB with our results."""
def run(task):
    pass
