import json
import random
import string

from peewee import *

from config import *

db = SqliteDatabase(DB_PATH) if not ISMYSQL else MySQLDatabase(host=MYSQL_HOST, database=MYSQL_DATABASE,
                                                               user=MYSQL_USERNAME, password=MYSQL_PASSWORD,
                                                               port=MYSQL_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class Follows(BaseModel):
    ID = PrimaryKeyField()
    Telegram_id = IntegerField(null=False, unique=True)
    PassWD = CharField(null=True)


class RssChannel(BaseModel):
    ID = PrimaryKeyField()
    Customize = CharField(null=False, unique=True)
    Master = ForeignKeyField(Follows, related_name="master")


class RssList(BaseModel):
    ID = PrimaryKeyField()
    Title = CharField(null=False)
    Rss = CharField(null=False, unique=True)
    Form = ForeignKeyField(RssChannel, related_name="form")


class RssMember(BaseModel):
    Follows = ForeignKeyField(Follows, related_name="follows")
    RssChannel = ForeignKeyField(RssChannel, related_name="rss_channel")


class RssAdmin(BaseModel):
    Follows = ForeignKeyField(Follows, related_name="follows")
    RssChannel = ForeignKeyField(RssChannel, related_name="rss_channel")


class DataBase(BaseModel):
    ID = PrimaryKeyField()
    Form = CharField(null=False)
    Title = CharField(null=False)
    Url = CharField(null=False, unique=True)
    Summary = TextField(null=True)


def create_table():
    db.connect()
    db.create_tables([Follows, RssChannel, RssList, RssMember, RssAdmin, DataBase])


def random_password():
    return ''.join(random.sample(string.ascii_letters + string.digits, 8))


## 字符串转字典
def str_to_dict(dict_str):
    if isinstance(dict_str, str) and dict_str != '':
        new_dict = json.loads(dict_str)
    else:
        new_dict = ""
    return new_dict


# 字典转对象
def dict_to_obj(dict, obj, exclude=None):
    for key in dict:
        if exclude:
            if key in exclude:
                continue
        setattr(obj, key, dict[key])
    return obj


# peewee转dict
def obj_to_dict(obj, exclude=None):
    print(obj.__dict__)
    dict = obj.__dict__['__data__']
    if exclude:
        for key in exclude:
            if key in dict: dict.pop(key)
    return dict


# peewee转list
def query_to_list(query, exclude=None):
    list = []
    for obj in query:
        dict = obj_to_dict(obj, exclude)
        list.append(dict)
    return list


if __name__ == '__main__':
    create_table()

    a = Follows.create(
        Telegram_id=1,
    )
    b = Follows.create(
        Telegram_id=2,
    )
    c = RssChannel.create(
        Customize='aaa" and 1=2',
        Master=a
    )
    RssAdmin.create(
        Follows=a,
        RssChannel=c
    )
    res = Follows.select().where(Follows.Telegram_id == 2).count()
    print(res)
