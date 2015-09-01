#!/usr/bin/env python

import fileinput
import sys
import os
from docopt import docopt
import logging
# import urllib3
import json

from tools import JsonPort, S3Port, ElasticPort, MongoPort, HbasePort, KafkaPort

from settings import (ES_SETTINGS, S3_SETTINGS,
                      MONGO_SETTINGS, HBASE_SETTINGS, KAFKA_SETTINGS)

# Local Overrides
# ~~~~~~~~~~~~~~~
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read(os.path.expanduser('~/.tport'))

if parser.has_section('elasticsearch'):
    ES_SETTINGS['host'] = parser.get('elasticsearch', 'host')
    ES_SETTINGS['ssl'] = bool(parser.get('elasticsearch', 'ssl'))

if parser.has_section('kafka'):
    KAFKA_SETTINGS['broker'] = parser.get('kafka', 'broker')

if parser.has_section('s3'):
    S3_SETTINGS['access_key'] = parser.get('s3', 'access_key')
    S3_SETTINGS['secret_key'] = parser.get('s3', 'secret_key')

if parser.has_section('mongo'):
    MONGO_SETTINGS['host'] = parser.get('mongo', 'host')
    MONGO_SETTINGS['db'] = parser.get('mongo', 'db')

if parser.has_section('hbase'):
    HBASE_SETTINGS['host'] = parser.get('hbase', 'host')

# cfg_dict = [dict(parser.items(cfg)) for cfg in parser.sections()]


# disable annoying SSL certificate warnings
# urllib3.disable_warnings()

# set up a logger
logging.basicConfig(level=logging.INFO)


def main():
    """ transporter: Transport JSON data to different outputs.

    Usage:
        tport inspect FILE ...
        tport es create --indexname=<indexname>
        tport es map --indexname=<indexname> --doctype=<doctype> --mapping=<mapping>
        tport es index --indexname=<indexname> --doctype=<doctype> [--chunksize=<chunksize>] [--mapping=<mapping>] [--ignore-errors=<ignore-errors>] FILE ...
        tport kafka topics [--broker=<broker>]
        tport kafka produce --topic=<topic> [--broker=<broker>] FILE ...
        tport kafka consume --topic=<topic> [--broker=<broker>]
        tport s3 list
        tport s3 upload <bucket> [--replace=<replace>] [--compress] FILE ...
        tport s3 download <bucket> FOLDER
        tport s3 destroy <bucket>
        tport mongo list [--host=<host>] [--db=<db>]
        tport mongo preview [--host=<host>] [--db=<db>] --collection=<collection>
        tport mongo export [--host=<host>] [--db=<db>] --collection=<collection> [FILE ...]
        tport mongo add [--host=<host>] [--db=<db>] --collection=<collection> FILE ...
        tport hbase scan [--host=<host>] --table=<table>

    Options:
        -h --help
        -e --ignore-errors <ignore-errors>
        -i --indexname <indexname>
        -d --doctype <doctype>
        -m --mapping <mapping>
        -c --chunksize <chunksize>
        -r --replace <replace>
        -t --topic <topic>
        -b --broker <broker>
    """

    args = docopt(main.__doc__)
    # logging.info(args)
    f = args['FILE']
    cli_ignore = True if args['--ignore-errors'] else False

    cli_jsonit = JsonPort(fileinput.input(f), cli_ignore) if f else None

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
            cli_chunksize = int(cli_chunksize)
            # Create index if not created
            esi.create(cli_iname)
            if args['--mapping']:
                with open(args['--mapping']) as fm:
                    cli_mapping = json.load(fm)
                esi.map(cli_iname, cli_dtype, cli_mapping)

            esi.index(cli_jsonit.parse(), cli_iname, cli_dtype, cli_chunksize)

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

if __name__ == '__main__':
    sys.exit(main())
