.. image:: https://travis-ci.org/istresearch/json-transporter.svg?branch=master
    :target: https://travis-ci.org/istresearch/json-transporter

Overview
---------

``tport`` is a simple command line tool written in Python for
all your JSON transporting needs. Tools currently supported:

-  Amazon S3
-  Elastic Search
-  Kafka
-  MongoDB
-  HBase

Quickstart
----------

1) ``pip install json-transporter``

2) Add your specific connections to a **.tport** file in your home directory.  For example,

::

    [elasticsearch]
    host = http://myescluster.com:9200
    ssl = false

    [kafka]
    host = http://mykafkabroker.com:9092

    [s3]
    access_key = youraccesskey
    secret_key = yoursecretkey

3) To view command line usage just type ``tport --help``

Configuration
-------------

If ``tport`` does not find the relevant settings on the command line or the **.tport** file, it will resort to the default settings for each tools.  For example,

- ``localhost:9200`` --> Elastic search
- ``localhost:9092`` --> Kafka

Connection settings such as the **host** and **db** can also be
specified on the command line. Anything specified on the command line
will have presedence over settings in files. Order of precedence:

1. command line
2. .tport
3. defaults
