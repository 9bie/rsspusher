# coding:utf-8

TIMER = 10*60 # second
DEBUG = True
if DEBUG:
    import logging
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

# Bot
TELEGRAM_KEYS = "1334452358:AAEmQICXklw0rymRRNaQWu-nwASCIbArjrc"
IS_WEBHOOK = False
URL = ""
WEBHOOKING = URL + "/"+TELEGRAM_KEYS


# DataBase
ISMYSQL = False
DB_PATH = "rss.db"
MYSQL_HOST = "localhost"
MYSQL_DATABASE = "rss"
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "root"
MYSQL_PORT = 3306

