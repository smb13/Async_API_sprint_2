import logging

import backoff
import time

from elasticsearch import Elasticsearch

from tests.functional.settings import session_settings


@backoff.on_exception(backoff.expo,
                      Exception,
                      logger=logging.getLogger('backoff').addHandler(logging.StreamHandler()))
def check_es_availability():
    es_client = Elasticsearch(hosts=session_settings.es_host)
    if not es_client.ping():
        time.sleep(1)
        raise Exception
    print('Es ping is ok')


if __name__ == '__main__':
    check_es_availability()
