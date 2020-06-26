from config import *
from peewee import *
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


class DataBase(BaseModel):
    ID = PrimaryKeyField()
    Title = CharField(null=False)
    Url = CharField(null=False,unique=True)
    Summary = TextField()


def create_table():
    db.connect()
    db.create_tables([RssList,Follows,DataBase])


if __name__ == '__main__':
    create_table()
    import rss
    rss.main(first_run=True)
