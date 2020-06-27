from config import *
from peewee import *
import random,string
db = SqliteDatabase(DB_PATH) if not ISMYSQL else MySQLDatabase(host=MYSQL_HOST, database=MYSQL_DATABASE,
                                                                user=MYSQL_USERNAME, password=MYSQL_PASSWORD, port=MYSQL_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class RssList(BaseModel):
    ID = PrimaryKeyField()
    Title = CharField(null=False)
    Rss = CharField(null=False, unique=True)


class Follows(BaseModel):
    ID = PrimaryKeyField()
    Telegram_id = IntegerField(null=False,unique=True)
    IsAdmin = BooleanField(null=False)
    PassWD = CharField(null=True)


class DataBase(BaseModel):
    ID = PrimaryKeyField()
    Form = CharField(null=False)
    Title = CharField(null=False)
    Url = CharField(null=False,unique=True)
    Summary = TextField(null=True)


def create_table():
    db.connect()
    db.create_tables([RssList,Follows,DataBase])


def random_password():
    return  ''.join(random.sample(string.ascii_letters + string.digits, 8))


if __name__ == '__main__':

    create_table()
    passwd = random_password()
    Follows.create(
        Telegram_id=YOUR_CHAT_ID_FOR_ADMIN,
        IsAdmin=True,
        PassWD=passwd
    )

    print("Your web control account: \tusername:{}\n\tpassword is {}".format(YOUR_CHAT_ID_FOR_ADMIN,passwd))
    import rss
    rss.main(first_run=True)
    print("Your web control account: \tusername:{}\n\tpassword is {}".format(YOUR_CHAT_ID_FOR_ADMIN, passwd))
