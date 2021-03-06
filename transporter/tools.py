#!/usr/bin/env python

import sys
import json
import logging
import gzip
import shutil

import urllib3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import boto
from boto.s3.key import Key
from pymongo import MongoClient
import happybase
from pykafka import KafkaClient
# from addict import Dict

# disable annoying SSL certificate warnings
urllib3.disable_warnings()

# set up a logger
logging.basicConfig(level=logging.INFO)


class JsonPort(object):
    """ Parses out a JSON iterator object.

        :param list jsonlist: a list or iterator of JSON objects.
    """

    def __init__(self, jsonlist, ignore_errors=False):
        self.jsonlist = jsonlist
        self.ignore_errors = ignore_errors

    def parse(self):
        """ Returns an JSON iterator object if input is valid JSON, else
            it returns an empty dictionary.
        """
        for idx, i in enumerate(self.jsonlist):
            try:
                yield json.loads(i)
            except ValueError as ve:
                logging.warning('line {0}:  {1}'.format(idx, ve))
                logging.debug('line {0}:  {1}'.format(idx, i))
                if not self.ignore_errors:
                    ans = raw_input('\nThis line is not JSON.'
                                    '  Continue to next line?  (Y/n)  ')
                    if ans.lower() == 'n':
                        sys.exit(0)

    def inspect(self):
        """ Output the serialized JSON object one line at a time.  To
            continue, press any key.  To end, Ctrl+d.
        """
        for i in self.parse():
            print json.dumps(i, indent=2)
            ans = raw_input('\n--Continue to next line?  (Y/n)--\n')
            if ans.lower() == 'n':
                sys.exit(0)


class ElasticPort(object):
    """ Class to handle Elastic Search actions.

        :param str host: elasticsearch host
        :param bool ssl: ssl enable
        :param str logger: name of logger
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
        """ Query Elastic Search """
        pass

    def index(self, jsonit, iname, dtype, chunksize=500):
        """ Data input is a JSON generator.  If using the command-line tool,
            this is handled via the JsonPort method which creates a
            JSON generator from lines read in from files.

            :param list jsonit: JSON list or iterator
            :param str iname: elasticsearch index name
            :param str dtype: document type
            :param int chunksize: number of docs to send at one time
        """

        def bulkgen(jsongen):
            """ Create a generator of JSON objects for bulk indexing.

                :param list jsongen: A JSON list or iterator
            """
            for idx, jobj in enumerate(jsongen):
                bulkr = dict()
                bulkr['_index'] = iname
                bulkr['_type'] = dtype
                bulkr['_source'] = jobj
                if 'id' in jobj:
                    bulkr['_id'] = jobj['id'].split(':')[2]
                self.logger.debug('done with index %s' % idx)
                yield bulkr

        r = bulk(client=self.es, actions=bulkgen(jsonit),
                 chunk_size=chunksize, stats_only=True)
        print 'INDEX: successful: %s; failed: %s' % (r[0], r[1])

    def map(self, iname, dtype, mapping):
        """ After creating a new index, specify a mapping.

            :param str iname: Index name
            :param str dtype: Document type
            :param dict mapping: Elastic Search mapping
        """
        self.logger.info('MAPPING: mapping is %s' % mapping)
        self.es.indices.put_mapping(index=iname,
                                    doc_type=dtype,
                                    body=mapping
                                    )

    def create(self, iname):
        """ Create a new Elastic Search index.

            :param str iname: Index name
        """
        self.es.indices.create(iname, ignore=400)


class KafkaPort(object):
    """ Class to interface with Kafka.

        :param str kafkabroker: Kafka broker and port, eg ``localhost:9092``
        :param str logger: Logger to use for Kafka.
    """

    def __init__(self, kafkabroker, logger=None):
        self.client = KafkaClient(hosts=kafkabroker)
        self.logger = logger or logging.getLogger(__name__)

    def produce(self, topic_name, jsonit):
        """ Send data to a Kafka topic.

            :param str topic_name: Kafka topic name
            :param list jsonlist: List or iterator of JSON objects
        """
        topic = self.client.topics[topic_name]
        self.producer = topic.get_producer()
        self.logger.info('producing messages to %s' % topic_name)
        self.producer.produce((json.dumps(s) for s in jsonit))
        self.logger.info('all messages sent to %s' % topic_name)

    def consume(self, topic_name):
        """ Receive data from a Kafka topic.

            :param str topic_name: Kafka topic name
        """
        topic = self.client.topics[topic_name]
        self.consumer = topic.get_simple_consumer()
        for message in self.consumer:
            if message is not None:
                print message.offset, message.value

    def topics(self):
        """ List Kafka topics. """
        topics = [t for t in self.client.topics]
        for s in sorted(topics):
            print s


class S3Port(object):
    """ Class to handle uploading and donwloading data to and from S3.  There
        is also an option to compress the files with gzip before uploading.

        :param str access_key: S3 access key
        :param str secret_key: S3 secret key
    """

    def __init__(self, access_key, secret_key):
        self.conn = boto.connect_s3(access_key, secret_key)

    def upload(self, bucket_name, filelist, compress=False, replace_key=False):
        """ Given a S3 bucket and a fileglob, upload data to S3. Using the
            --compress option is recommended to save on S3 costs.

            :param str bucket_name: S3 bucket name
            :param list filelist: List of files to upload to S3
            :param bool compress: Compress the data before uploading
            :param bool replace_key: Replace existing data
        """
        # Create new bucket if it doesn't exist.  Otherwise, use existing.
        new_bucket = self.conn.create_bucket(bucket_name)
        for fname in filelist:
            if compress:
                cfname = ''.join(['/tmp/', fname.split('/')[-1], '.gz'])
                with open(fname, 'rb') as f_in, gzip.open(cfname, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                fname = cfname
            k = Key(new_bucket)
            k.key = fname.split('/')[-1]
            t = k.set_contents_from_filename(fname, replace=replace_key)
            if t:
                logging.info('{0} file uploaded to: {1}'.format(fname,
                             bucket_name))
            if not t:
                logging.info('{0} file already exists in {1}!'.format(fname,
                             bucket_name))

    def download(self, bucket_name, folder):
        """ Download all data in an S3 bucket.

            :param str bucket_name: Name of S3 bucket
            :param str folder: Folder to store S3 data
        """
        a_bucket = self.conn.create_bucket(bucket_name)
        for key in a_bucket.list():
            path = '/'.join([folder, key.name])
            key.get_contents_to_filename(path)
            logging.info('{0} downloaded'.format(path))

    def destroy(self, bucket_name):
        """ Destroy an S3 bucket and all data inside it.

            :param str bucket_name: S3 bucket to destroy
        """
        full_bucket = self.conn.get_bucket(bucket_name)
        for key in full_bucket.list():
            key.delete()
        self.conn.delete_bucket(bucket_name)
        logging.info('{0} bucket was destroyed'.format(bucket_name))

    def list(self):
        """ List all S3 buckets. """
        rs = self.conn.get_all_buckets()
        print 'Available buckets:\n'
        for b in rs:
            print b


class MongoPort(object):
    """ Class to handle interfacing with MongoDB.

        :param str host: Mongo hostname
        :param str db: Mongo database
    """

    def __init__(self, host, db):
        self.client = MongoClient(host)
        self.db = self.client[db]

    def preview(self, collection):
        """ View a collection line by line.  Ctrl+d to stop.

            :param str collection: Name of Mongo collection or table
        """
        self.collection = self.db[collection]
        for doc in self.collection.find():
            print doc
            try:
                raw_input('\n--Press any key to continue--\n')
            except EOFError:
                sys.exit(0)

    def add(self, collection):
        """ Add data to a MongoDB collection.

            :param str collection: Name of Mongo collection or table
        """
        self.collection = self.db.collection

    def export(self, collection, f=''):
        """ Export serailized JSON data from a MongoDB colllection.
            Not working yet.

            :param str collection: Name of Mongo collection or table
            :param str f: File to write to
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
        """ List all collections in the Mongo database. """
        for c in self.db.collection_names():
            print c


class HbasePort(object):
    """ Class to interface with HBase.

        :param str hostname: Hbase hostname
    """

    def __init__(self, hostname):
        self.connection = happybase.Connection(hostname)

    def scan(self, tablename):
        """ Print HBase rows one row at a time.  Ctrl+d to stop.

            :param str tablename: Hbase table name
        """
        table = self.connection.table(tablename)
        for key, data in table.scan():
            print key, data
            try:
                raw_input('\n--Press any key to continue--\n')
            except EOFError:
                sys.exit(0)
