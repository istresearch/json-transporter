#!/usr/bin/env python

import sys
import fileinput
import json
import logging
import urllib3

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.helpers import streaming_bulk
import boto
from boto.s3.key import Key
from pymongo import MongoClient
import happybase
from pykafka import KafkaClient
from docopt import docopt
from addict import Dict

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
        for idx, i in enumerate(self.jsonlist):
            try:
                yield json.loads(i)
            except ValueError as ve:
                logging.warning('line {0}:  {1}'.format(idx, ve))
                logging.debug('line {0}:  {1}'.format(idx, i))
                yield {}

    def inspect(self):
        for i in self.parse():
            print json.dumps(i, indent=2)
            try:
                raw_input('\n--Press any key to continue--\n')
            except EOFError:
                sys.exit(0)


class ElasticPort(object):
    """Class to handle Elastic Search actions.

    index:  Data input is a JSON generator.  If using the command-line tool,
            this is handled via the JsonPort method which creates a
            JSON generator from lines read in from files.
    """

    def __str__(self):
        return 'ElasticPort'

    def __init__(self, host, ssl, logger=None):
        self.es = Elasticsearch(host, set_ssl=ssl)

        self.logger = logging.getLogger(__name__)
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)
        # self.logger.addHandler(ch)
        # self.logger.setLevel(logging.INFO)

    def query(self):
        pass

    def index(self, jsonit, iname, dtype):
        self.es.indices.create(iname, ignore=400)

        # Create a generator of JSON objects for bulk indexing
        def bulkgen(jsongen):
            for jobj in jsongen:
                bulkr = dict()
                bulkr['_index'] = iname
                bulkr['_type'] = dtype
                bulkr['_source'] = jobj
                if 'id' in jobj:
                    bulkr['_id'] = jobj['id']
                self.logger.debug('done with %s' % jobj['id'])
                yield bulkr
                

        r = bulk(client=self.es, actions=bulkgen(jsonit), stats_only=True)
        self.logger.info('INDEX: successful: %s; failed: %s' % (r[0], r[1]))

    def map(self):
        return None
        self.es.indices.put_mapping(index=ES_SETTINGS['index'],
                                    doc_type=ES_SETTINGS['dtype'],
                                    body=ES_SETTINGS['mapping']
                                    )


class S3Port(object):

    def __init__(self, access_key, secret_key):
        self.conn = boto.connect_s3(access_key, secret_key)

    def __str__(self):
        return "Connected to: {0}".format(S3_SETTINGS['s3_access_key'])

    def compress(self):
        pass

    def upload(self, bucket_name, keylist):
        # Create new bucket if it doesn't exist.  Otherwise, use existing.
        new_bucket = self.conn.create_bucket(bucket_name)
        for i in keylist:
            k = Key(new_bucket)
            k.key = i
            k.set_contents_from_filename(i)
            logging.info('{0} file uploaded to: {1}'.format(i, bucket_name))

    def download(self):
        pass

    def destroy(self, bucket_name):
        full_bucket = self.conn.get_bucket(bucket_name)
        for key in full_bucket.list():
            key.delete()
        self.conn.delete_bucket(bucket_name)
        logging.info('{0} bucket was destroyed'.format(bucket_name))

    def list(self):
        rs = self.conn.get_all_buckets()
        print 'Available buckets:\n'
        for b in rs:
            print b


class MongoPort(object):

    def __init__(self, host, db):
        self.client = MongoClient(host)
        self.db = self.client[db]

    def preview(self, collection):
        self.collection = self.db[collection]
        for doc in self.collection.find():
            print doc
            try:
                raw_input('\n--Press any key to continue--\n')
            except EOFError:
                sys.exit(0)

    def add(self, collection):
        self.collection = self.db.collection

    def export(self, collection, f=''):
        """ export not working yet
        """
        self.collection = self.db[collection]
        for doc in self.collection.find():
            if f:
                with open(f, 'w') as newfile:
                    newfile.write()

        # d = JsonPort(self.collection.find())
        # for item in d.parse():
        #     print item
        #     raw_input('\Continue?\n')
        # for doc in self.collection.find():

    def list(self):
        for c in self.db.collection_names():
            print c



class HbasePort(object):

    def connect(self):
        pass


class KafkaPort(object):

    def __init__(self, kafkabroker, logger=None):
        self.client = KafkaClient(hosts=kafkabroker)
        self.logger = logger or logging.getLogger(__name__)

    def produce(self, topic_name, jsonit):
        topic = self.client.topics[topic_name]
        self.producer = topic.get_producer()
        self.logger.info('producing messages to %s' % topic_name)
        self.producer.produce((json.dumps(s) for s in jsonit))
        self.logger.info('all messages sent to %s' % topic_name)

    def consume(self, topic_name):
        topic = self.client.topics[topic_name]
        self.consumer = topic.get_simple_consumer()
        for message in self.consumer:
            if message is not None:
                print message.offset, message.value

    def topics(self):
        topics = [t for t in self.client.topics]
        for s in sorted(topics):
            print s


def main():
    """ transporter: Transport JSON data to different outputs.

    Usage:
        tport inspect FILE ...
        tport es (<index> | <map> | <query>) --indexname=<indexname> --doctype=<doctype> FILE ...
        tport s3 list
        tport s3 (upload | download) <bucket> FILE ...
        tport s3 destroy <bucket>
        tport mongo list [--host=<host>] [--db=<db>]
        tport mongo preview [--host=<host>] [--db=<db>] --collection=<collection>
        tport mongo export [--host=<host>] [--db=<db>] --collection=<collection> [FILE ...]
        tport mongo add [--host=<host>] [--db=<db>] --collection=<collection> FILE ...
        tport hbase FILE ...
        tport kafka topics [--broker=<broker>]
        tport kafka produce --topic=<topic> [--broker=<broker>] FILE ...
        tport kafka consume --topic=<topic> [--broker=<broker>]

    Examples:
        Upload files (preferably serialized JSON ) to S3
        tport s3 upload --bucket=<bucket> FILE ...

    Settings:
        Some settings that don't change often (S3 keys, ES hosts, Kafka brokers)
        can be set in the "localsettings.py" file so that they do not need
        to be passed in at the command line.  However, it is still possible
        to pass these values at the command line to override the settings.


    Options:
        -t --topic <topic>
        -b --broker <broker>
        -i --indexname <indexname>
        -d --doctype <doctype>
        -c --collection <collection>

    Notes:
        Might want to pass in the SETTINGS file in the command line rather
        than having it in the import process.

    """
    args = docopt(main.__doc__)

    f = args['FILE']

    logging.debug(args)

    cli_jsonit = JsonPort(fileinput.input(f)) if f else None

    if args['inspect']:
        cli_jsonit.inspect()

    if args['es']:
        # Connect to elastic search
        esi = ElasticPort(ES_SETTINGS['host'], ES_SETTINGS['ssl'])
        if args['<index>']:
            cli_iname = args['--indexname']
            cli_dtype = args['--doctype']
            esi.index(cli_jsonit.parse(), cli_iname, cli_dtype)

    if args['s3']:
        s3u = S3Port(S3_SETTINGS['access_key'], S3_SETTINGS['secret_key'])
        if args['list']:
            s3u.list()
        if args['upload']:
            logging.info('upload starting...')
            s3u.upload(args['<bucket>'], f)
            logging.info('upload complete')
        if args['download']:
            pass
        if args['destroy']:
            print 'You are about to DESTROY the entire {0} bucket!!!\n'.format(
                                                            args['<bucket>'])
            response = raw_input('Are you sure? [Y/n] ')
            if response == 'Y':
                s3u.destroy(args['<bucket>'])
            else:
                print """
                                               (@<
                 Chickening out....           (< )
                                               ^^
                      """

    if args['mongo']:
        # Connect to mongo database
        mg_host = MONGO_SETTINGS['host'] or args['--host']
        mg_db = MONGO_SETTINGS['db'] or args['--db']
        mgi = MongoPort(mg_host, mg_db)
        if args['list']:
            mgi.list()
        if args['preview']:
            mg_collection = args['--collection']
            mgi.preview(mg_collection)
        if args['export']:
            mg_collection = args['--collection']
            mgi.export(mg_collection, f)   # generator object

    if args['hbase']:
        pass

    if args['kafka']:
        ka_broker = args['--broker'] or KAFKA_SETTINGS['broker']
        kai = KafkaPort(ka_broker)
        if args['topics']:
            kai.topics()
        if args['produce']:
            cli_topic = args['--topic']
            kai.produce(cli_topic, cli_jsonit.parse())
        if args['consume']:
            cli_topic = args['--topic']
            kai.consume(cli_topic)

if __name__ == '__main__':
    sys.exit(main())
