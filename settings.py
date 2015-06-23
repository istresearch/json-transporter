JSON_SETTINGS = {

}

ES_SETTINGS = {
	'host': 'localhost:9200',
    'ssl': 'false'
}

S3_SETTINGS = {
	'access_key': 'use_localsettings',
	'secret_key': 'use_localsettings'
}

MONGO_SETTINGS = {

}

HBASE_SETTINGS = {
	
}

KAFKA_SETTINGS = {
	'host': 'localhost:9092',
	'prefix': 'dingo'
}

# Local Overrides
# ~~~~~~~~~~~~~~~

try:
    from localsettings import *
except ImportError:
    pass
