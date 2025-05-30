from .base import *

DEBUG = True
ALLOWED_HOSTS = config('ALLOWED_HOSTS_DEV', default='localhost,127.0.0.1', cast=Csv())