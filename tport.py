#!/usr/bin/env python

import fileinput
import sys
from docopt import docopt
import logging
import urllib3
import json

from tools import JsonPort
from tools import S3Port
from tools import ElasticPort
from tools import MongoPort
from tools import HbasePort
from tools import KafkaPort

from settings import (JSON_SETTINGS, ES_SETTINGS, S3_SETTINGS,
                      MONGO_SETTINGS, HBASE_SETTINGS, KAFKA_SETTINGS)

# disable annoying SSL certificate warnings
urllib3.disable_warnings()

# set up a logger
logging.basicConfig(level=logging.INFO)


def main():
    """ transporter: Transport JSON data to different outputs.

    Usage:
        tport inspect FILE ...
        tport es create --indexname=<indexname>
        tport es map --indexname=<indexname> --doctype=<doctype> --mapping=<mapping>
        tport es index --indexname=<indexname> --doctype=<doctype> [--chunksize=<chunksize>] [--mapping=<mapping>] [FILE ...]
        tport s3 list
        tport s3 upload <bucket> [--replace=<replace>] [--compress] FILE ...
        tport s3 download <bucket> FOLDER
        tport s3 destroy <bucket>
        tport mongo list [--host=<host>] [--db=<db>]
        tport mongo preview [--host=<host>] [--db=<db>] --collection=<collection>
        tport mongo export [--host=<host>] [--db=<db>] --collection=<collection> [FILE ...]
        tport mongo add [--host=<host>] [--db=<db>] --collection=<collection> FILE ...
        tport hbase scan [--host=<host>] --table=<table>
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
        cli_iname = args['--indexname']
        cli_dtype = args['--doctype']
        if args['create']:
            esi.create(cli_iname)
        if args['map']:
            with open(args['--mapping']) as fm:
                cli_mapping = json.load(fm)
            esi.map(cli_iname, cli_dtype, cli_mapping)
        if args['index']:
            cli_chunksize = args['--chunksize'] or 500
            int(cli_chunksize)
            # Create index if not created
            esi.create(cli_iname)
            if args['--mapping']:
                with open(args['--mapping']) as fm:
                    cli_mapping = json.load(fm)
                esi.map(cli_iname, cli_dtype, cli_mapping)

            esi.index(cli_jsonit.parse(), cli_iname, cli_dtype, cli_chunksize)

    if args['s3']:
        s3u = S3Port(S3_SETTINGS['access_key'], S3_SETTINGS['secret_key'])
        if args['list']:
            s3u.list()
        if args['upload']:
            cli_replace = args['--replace']
            cli_bucket = args['<bucket>']
            cli_compress = True if args['--compress'] else False
#            logging.info('upload starting...')
            s3u.upload(cli_bucket, f, cli_compress, cli_replace)
#            logging.info('upload complete')
        if args['download']:
            cli_folder = args['FOLDER']
            cli_bucket = args['<bucket>']
            s3u.download(cli_bucket, cli_folder)
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
        hb_host = HBASE_SETTINGS['host'] or args['--host']
        hbi = HbasePort(hb_host)
        if args['scan']:
            hbi_table = args['--table']
            hbi.scan(hbi_table)

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
