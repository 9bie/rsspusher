# coding:utf-8
import os
TIMER = 10*60 # second
TIMEOUT = 30
DEBUG = True
if DEBUG:
    import logging
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

# Bot
TELEGRAM_KEYS = "1386497203:AAGYMq8Hmj7YTfgbIs74PgDrJMT8LpN3zVY"
IS_WEBHOOK = False
URL = "https://i.9bie.org"
WEBHOOKING = URL + "/"+TELEGRAM_KEYS


# DataBase
ISMYSQL = False
DB_PATH = "rss.db"
MYSQL_HOST = "localhost"
MYSQL_DATABASE = "rss"
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "root"
MYSQL_PORT = 3306

