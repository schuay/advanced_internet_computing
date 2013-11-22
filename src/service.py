#!/bin/python2
#
# This script requires python2-flask.
#
# A couple of notes:
# * Omit application name and API version from URL for testing simplicity.
# * By default, this service will be single-threaded. We can make flask
#   spawn several threads to serve requests, but a better approach is to
#   use Apache. Can we skip that for this project? See
#   http://stackoverflow.com/questions/14814201/can-i-serve-multiple-clients-using-just-flask-app-run-as-standalone
# * Base64 encoding of data?
# * Authentication?
# * Caching?
# * Content type negotiation?
# * Return endpoints on API root? http://blog.luisrei.com/articles/rest.html

import getopt
import sys

from flask import Flask, abort, json, jsonify, make_response, request, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import datetime
import uuid

from classifier import Classifier
from classifier import AllWords

classifier = "classifier.pickle"

CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404

app = Flask(__name__)

import task

DBNAME = "tweets"

from Queue import Queue
from seqworker import SeqWorker

task_queue = Queue()

db_client = MongoClient()
db_collection = db_client[DBNAME].task_collection

db_collection.ensure_index(task.ID)

# TODO: add endpoint for twitter authentication, every client supplies their own twitter account
# or user pool of twitter accounts

# TODO: Add http status code and internal error code to error headers.
@app.errorhandler(BAD_REQUEST)
def bad_request(error):
    return make_response(jsonify({ 'error': 'Bad request'}), BAD_REQUEST)

@app.errorhandler(NOT_FOUND)
def not_found(error):
    return make_response(jsonify({ 'error': 'Not found'}), NOT_FOUND)

# Returns 404 if the task does not exist, otherwise the task details as JSON data.
# curl localhost:5000/api/tasks/42
@app.route('/api/tasks/<string:task_id>', methods = ['GET'])
def api_get_task(task_id):
    t = db_collection.find_one({ task.ID: task_id });
    if not t:
        abort(NOT_FOUND)
    t.pop('_id')
    return jsonify({'tasks': t})

@app.route('/api/tasks/<string:task_id>', methods = ['DELETE'])
def api_del_task(task_id):
    db_collection.remove({ task.ID: task_id });
    return "DEL %s" % task_id

# TODO: Change to noun endpoint name.
# Takes a JSON data object with required fields [keywords, start, end].
# Returns 400 on error, 201 on success.
# curl -i -H "Content-Type: application/json" -X POST -d '{"start":"20110101", "end":"20130101", "keywords":["secret","monkey","beezkneez"]}' 'localhost:5000/api/submit'
@app.route('/api/tasks', methods = ['POST'])
def api_post_task():
    if not (request.json and 'keywords' in request.json and
            'start' in request.json and 'end' in request.json):
        abort(BAD_REQUEST)

    # TODO: Error handling.

    new_id = str(uuid.uuid4())
    new_task = { 'id': new_id
               , 'keywords': request.json['keywords']
               , 'start': request.json['start']
               , 'end': request.json['end']
               }

    try:
        db_collection.insert(new_task)
    except DuplicateKeyError:
        print ("Duplicate ID %s. WTF?" % new_id)
        raise

    task_queue.put(new_task)

    return jsonify({'id': new_id, 'uri': url_for('api_get_task',
        task_id = new_id, _external = True)}), CREATED

def usage():
    print("USAGE: %s [-c classifier]" %
            sys.argv[0])

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hc:")
    for o, a in opts:
        if o == "-c":
            classifier = a
        else:
            usage()
            sys.exit(0)

    classifier = Classifier.load(classifier)
    worker = SeqWorker(task_queue, DBNAME, classifier);
    worker.start()

    app.run(debug = True)

    worker.join()
