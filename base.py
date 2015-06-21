#!/usr/bin/env python

import sys
import fileinput
import json
import logging

from elasticsearch import Elasticsearch
import boto
from boto.s3.key import Key
import pymongo
import happybase
from docopt import docopt
from addict import Dict

from settings import (JSON_SETTINGS, ES_SETTINGS, S3_SETTINGS,
                      MONGO_SETTINGS, HBASE_SETTINGS, KAFKA_SETTINGS)


logging.basicConfig(level=logging.INFO)


class JsonPort(object):
    """ Parses out a JSON iterator object.

    parse():  Returns an JSON iterator object.  Each iteration is a verified
              object.
    """

    def __init__(self, jsonlist):
        self.jsonlist = jsonlist

    def parse(self):
        for i in self.jsonlist:
            try:
                yield json.loads(i)
            except ValueError:
                yield None


class ElasticPort(object):
    """Class to handle Elastic Search actions.

    index:  Data input is a JSON generator.  If using the command-line tool,
            this is handled via the JsonPort method which creates a
            JSON generator from lines read in from files.
    """

    def __init__(self):
        self.es = Elasticsearch(ES_SETTINGS['host'])

    def query(self):
        pass

    def index(self, json_gen):
        self.es.indices.create(ES_SETTINGS['index'], ignore=400)
        self.es.indices.put_mapping(index=ES_SETTINGS['index'],
                                    doc_type=ES_SETTINGS['dtype'],
                                    body=ES_SETTINGS['mapping']
                                    )
        bulk_jrec = []
        for jrec in json_gen:
            bulk_jrec.append({'_index': ES_SETTINGS['index'],
                             '_type': ES_SETTINGS['dtype'],
                             # '_id': tweet_id,
                             '_source': jrec
                             })
            r = bulk(client=self.es, actions=bulk_jrec, stats_only=True)
            logger.info('%s; successful: %s; failed: %s' % 
                        (fname.split('/')[-1], r[0], r[1]))

    def map(self):
        pass


class S3Port(object):

    def __init__(self):
        self.conn = boto.connect_s3(S3_SETTINGS['s3_access_key'],
                                    S3_SETTINGS['s3_secret_key'])

    def __str__(self):
        return "Connected to: {}".format(S3_SETTINGS['s3_access_key'])

    def compress(self):
        pass

    def upload(self, bucket_name, keylist):
        self.bucket = self.conn.create_bucket(bucket_name)
        for i in keylist:
            k = Key(self.bucket)
            k.key = i
            k.set_contents_from_filename(i)
            logging.info('{} file was uploaded to: {}'.format(i, bucket_name))

    def download(self):
        pass


class MongoPort(object):

    def connect(self):
        pass

    def add(self):
        pass


class HbasePort(object):

    def connect(self):
        pass


class KafkaPort(object):

    def connect(self):
        pass

    def produce(self):
        pass

    def consume(self):
        pass


def main():
    """ transporter: Transport JSON data to different outputs.

    Usage:
        transporter es (<index> | <map> | <query>) --host=<host> [--type=<type>] FILE ...
        transporter s3 (<upload> | <download>) --bucket=<bucket> FILE ...
        transporter mongo --host=<host> --db=<db> --collection=<collection> FILE ...
        transporter hbase FILE ...
        transporter kafka (<produce> | <consume> ) --broker=<broker> --topic=<topic> FILE ...

    Examples:
        Upload files (preferably serialized JSON ) to S3
        transporter s3 upload --bucket=<bucket> FILE ...


    Options:

    Notes:
        Might want to pass in the SETTINGS file in the command line rather
        than having it in the import process.

    """
    args = docopt(main.__doc__)

    f = args['FILE']

    if args['es']:
        a = JsonPort(fileinput.input(f))
        print [i for i in a.parse()]


    if args['s3']:
        if args['<upload>']:
            s3u = S3Port()
            logging.info('upload starting...')
            s3u.upload(args['--bucket'], args['FILE'])
            logging.info('upload complete')
        if args['<download>']:
            pass

    if args['mongo']:
        pass

    if args['hbase']:
        pass

    if args['kafka']:
        pass


if __name__ == '__main__':
    sys.exit(main())
