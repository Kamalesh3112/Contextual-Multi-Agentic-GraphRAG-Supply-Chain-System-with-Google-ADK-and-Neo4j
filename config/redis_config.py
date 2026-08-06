import redis
from config.settings import settings

redis_client = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    password = settings.REDIS_PASSWORD,
    decode_responses = True,
    socket_timeout = 5,
    socket_connect_timeout = 5,
    socket_keepalive = True,
    health_check_interval = 30,
    retry_on_timeout = True,
    ssl = settings.REDIS_SSL,
    ssl_certfile = settings.REDIS_CERT,
    ssl_keyfile = settings.REDIS_KEY,
    ssl_ca_certs = settings.REDIS_CA
)