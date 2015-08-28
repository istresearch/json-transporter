json-transporter
================

Transportation is a precise business.
-------------------------------------

.. figure:: transporter.jpg
   :alt: alt tag

   alt tag

**json-transporter** is a simple command line tool writen in Python for
all your JSON transporting needs. Tools currently supported:

-  Amazon S3
-  Elastic Search
-  Kafka
-  MongoDB
-  HBase

Quickstart
----------

::

    git clone git@github.com:istresearch/json-transporter.git
    cd json-transporter
    pip install -r requirements.txt

To view usage just type ``python tport.py -h``

Configuration
-------------

Basic settings can be found in the ``settings.py`` file. To use with
your servers hosted somewhere besides **localhost**, add a
``localsettings.py`` file, which will override ``settings.py``. For
example, if you are working with Elastic Search:

::

    ES_SETTINGS = {
        'host': 'http://randomescluster.com:9200',
        'ssl': 'false'
    }

**NOTE**: Do not check in ``localsettings.py`` into this repository.
That file likely contains connection and password information that
should be kept separate.

Connection settings such as the **host** and **db** can also be
specified on the command line. Anything specified on the command line
will have presedence over settings in files. Order of precedence:

1. command line
2. localsettings.py
3. settings.py
