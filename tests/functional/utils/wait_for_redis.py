import logging

import backoff
import time

from redis import Redis
from tests.functional.settings import session_settings


@backoff.on_exception(backoff.expo,
                      Exception,
                      logger=logging.getLogger('backoff').addHandler(logging.StreamHandler()))
def check_redis_availability():
    redis_client = Redis(host=session_settings.redis_host, port=session_settings.redis_port)
    if not redis_client.ping():
        time.sleep(1)
        raise Exception
    print('Redis ping is ok')


if __name__ == '__main__':
    check_redis_availability()
