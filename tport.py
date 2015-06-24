#!/usr/bin/env python

import sys
import fileinput
import json
import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import boto
from boto.s3.key import Key
import pymongo
import happybase
from docopt import docopt
from addict import Dict
import urllib3

from settings import (JSON_SETTINGS, ES_SETTINGS, S3_SETTINGS,
                      MONGO_SETTINGS, HBASE_SETTINGS, KAFKA_SETTINGS)

# disable annoying SSL certificate warnings
urllib3.disable_warnings()

# set up a logger
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
                raise


class ElasticPort(object):
    """Class to handle Elastic Search actions.

    index:  Data input is a JSON generator.  If using the command-line tool,
            this is handled via the JsonPort method which creates a
            JSON generator from lines read in from files.
    """

    def __init__(self, host, ssl, logger=None):
        self.es = Elasticsearch(host, set_ssl=ssl)
        self.logger = logger or logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def query(self):
        pass

    def index(self, jsonit, iname, dtype):
        self.es.indices.create(iname, ignore=400)
        print dir(self)

        # Create a list of JSON objects for elastic search bulk indexing
        jsonbulk = []
        for jobj in jsonit:
            jsonbulk.append({'_index': iname,
                             '_type': dtype,
                             '_id': jobj['id'],
                             '_source': jobj
                             })
            self.logger.debug('done with %s' % jobj['id'])
        self.logger.info('sending %s records to the bulk api' % len(jsonbulk))
        r = bulk(client=self.es, actions=jsonbulk, stats_only=True)
        self.logger.info('successful: %s; failed: %s' % (r[0], r[1]))

    def map(self):
        return None
        self.es.indices.put_mapping(index=ES_SETTINGS['index'],
                                    doc_type=ES_SETTINGS['dtype'],
                                    body=ES_SETTINGS['mapping']
                                    )


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
        tport es (<index> | <map> | <query>) --indexname=<indexname> --type=<type> FILE ...
        tport s3 (<upload> | <download>) --bucket=<bucket> FILE ...
        tport mongo --host=<host> --db=<db> --collection=<collection> FILE ...
        tport hbase FILE ...
        tport kafka (<produce> | <consume> ) --broker=<broker> --topic=<topic> FILE ...

    Examples:
        Upload files (preferably serialized JSON ) to S3
        tport s3 upload --bucket=<bucket> FILE ...


    Options:

    Notes:
        Might want to pass in the SETTINGS file in the command line rather
        than having it in the import process.

    """
    args = docopt(main.__doc__)

    f = args['FILE']

    if args['es']:
        # Connect to elastic search
        esi = ElasticPort(ES_SETTINGS['host'], ES_SETTINGS['ssl'])
        if args['<index>']:
            cli_iname = args['--indexname']
            cli_dtype = args['--type']
            cli_jsonit = JsonPort(fileinput.input(f))
            esi.index(cli_jsonit.parse(), cli_iname, cli_dtype)

    if args['s3']:
        if args['<upload>']:
            s3u = S3Port()
            logging.info('upload starting...')
            s3u.upload(args['--bucket'], f)
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
