# json-transporter
### Transportation is a precise business.

**json-transporter** is a simple command line tool writen in Python for all your JSON transporting needs.  Tools currently supported:

- Amazon S3
- Elastic Search
- Kafka
- MongoDB
- HBase

## Quickstart
```
git clone git@github.com:istresearch/json-transporter.git
cd json-transporter
pip install -r requirements.txt
```
To view usage just type `python tport.py`
```
    Usage:
        tport inspect FILE ...
        tport s3 list
        tport s3 (upload | download) <bucket> FILE ...
        tport s3 destroy <bucket>
        tport mongo list [--host=<host>] [--db=<db>]
        tport mongo preview [--host=<host>] [--db=<db>] --collection=<collection>
        tport mongo export [--host=<host>] [--db=<db>] --collection=<collection> [FILE ...]
        tport mongo add [--host=<host>] [--db=<db>] --collection=<collection> FILE ...
        tport kafka topics [--broker=<broker>]
        tport kafka produce --topic=<topic> [--broker=<broker>] FILE ...
        tport kafka consume --topic=<topic> [--broker=<broker>]
        tport es (<index> | <map> | <query>) --indexname=<indexname> --doctype=<doctype> FILE ...
        tport hbase scan [--host=<host>] --table=<table>
```

## Configuration
Basic settings can be found in the `settings.py` file.  To use with your servers hosted somewhere besides **localhost**, add a `localsettings.py` file, which will override `settings.py`.  For example, if you are working with MongoDB:

```
MONGO_SETTINGS = {
    'host': 'transporter',
    'db': 'dingo'
}
```

**NOTE**:  Do not check in `localsettings.py` into this repository.  That file likely contains connection and password information that should be kept separate.

Connection settings such as the **host** and **db** can also be specified on the command line.  Anything specified on the command line will have presedence over settings in files.  Order of precedence:  

1.  command line
2.  localsettings.py
3.  settings.py

