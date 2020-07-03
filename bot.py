import re

import telegram

import models
from config import *
# from rss import check
bot = telegram.Bot(token=TELEGRAM_KEYS)


class Bot:

    def __init__(self, update):
        self.update = update
        self.chat_id = update.message.chat_id
        self.data = update.message.to_dict()
        self.command = self.data["text"].split()[0]
        self.param = self.data["text"].split()

    def __grant(self, param_number):
        if len(self.param) < param_number:
            bot.send_message(chat_id=self.chat_id, text="Parameter error.")
            return False
        if not models.Follows.select().where(
                models.Follows.Telegram_id == self.chat_id
        ).exists():
            models.Follows.create(
                Telegram_id=self.chat_id
            )
        return True

    def __is_channel_exists(self, id):
        if not models.RssChannel.select().where(
                models.RssChannel.Customize == id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="channel not found.")
            return False
        return True

    def __are_you_admin(self, channel_customize):
        if not models.RssAdmin.select().where(
                models.RssAdmin.RssChannel == models.RssChannel.get(Customize=channel_customize),
                models.RssAdmin.Follows == models.Follows.get(Telegram_id=self.chat_id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="you are not admin for this channel.")
            return False
        return True

    def __create(self):

        if not self.__grant(param_number=2):
            return
        if models.RssChannel.select().where(
                models.RssChannel.Master == models.Follows.get(Telegram_id=self.chat_id)
        ).count() >= 3:
            bot.send_message(chat_id=self.chat_id, text="You have exceeded th"
                                                        "e limit for creating channels, up to three")
            return
        if models.RssChannel.select().where(
            models.RssChannel.Customize==self.param[1]
        ).exists():
            bot.send_message(chat_id=self.chat_id,text="channel id is exists.")
            return
        new_channel = models.RssChannel.create(
            Customize=self.param[1],
            Master=models.Follows.get(Telegram_id=self.chat_id)
        )
        models.RssAdmin.create(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChannel=new_channel
        )
        models.RssMember.create(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChannel=new_channel
        )

        bot.send_message(chat_id=self.chat_id, text="Success, your channel id is {},"
                                                    " other users can join your"
                                                    " rss channel by this id".format(self.param[1]))

    def __join(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        if not models.RssChannel.select().where(
                models.RssChannel.Customize == id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="channel not found.")
            return
        if models.RssMember.select().where(
            models.RssMember.Follows==models.Follows.get(Telegram_id=self.chat_id),
            models.RssMember.RssChannel==models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id,text="you are joined this channel.")
            return
        models.RssMember.create(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChannel=models.RssChannel.get(Customize=id)
        )
        bot.send_message(chat_id=self.chat_id, text="Successful.")

    def __leave(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return

        if not models.RssMember.select().where(
                models.RssMember.Follows == models.Follows.get(Telegram_id=self.chat_id),
                models.RssMember.RssChannel == models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="you are not join this channel.")
            return

        models.RssMember.delete().where(
            models.RssMember.Follows == models.Follows.get(Telegram_id=self.chat_id),
            models.RssMember.RssChannel == models.RssChannel.get(Customize=id)
        ).execute()
        if models.RssChannel.get(Customize=id).Master == models.Follows.get(Telegram_id=self.chat_id):
            models.RssAdmin.delete().where(models.RssAdmin.RssChannel == models.RssChannel.get(Customize=id)).execute()
            models.RssChannel.delete().where(models.RssChannel.Customize == id).execute()
        bot.send_message(chat_id=self.chat_id, text="Successful!")

    def __list(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return
        results = ""
        rsslists = models.RssListFriendShip.select().where(
            models.RssListFriendShip.RssChannel == models.RssChannel().get(Customize=id)
        )
        for i in rsslists:
            results += "Rss Form: {}\n\tRss id: {}\n\tTitle:{}\n\tRss:{}\n\t".format(i.RssChannel.Customize,
                                                                                     i.RssList.ID, i.CustomizeTitle,
                                                                                     i.RssList.Rss)
        if results == "":
            bot.send_message(chat_id=self.chat_id, text="you are not add any for channel.")
        else:
            bot.send_message(chat_id=self.chat_id, text=results)

    def __myself(self):
        if not self.__grant(param_number=1):
            return
        master = "\nYou are master for:"
        rss_master = models.RssChannel.select().where(
            models.RssChannel.Master == models.Follows.get(Telegram_id=self.chat_id)
        )

        for i in rss_master:
            master += "\n\tRss Channel ID: {}\n".format(i.Customize)
        rss_admin = models.RssAdmin.select().where(
            models.RssAdmin.Follows == models.Follows.get(Telegram_id=self.chat_id)
        )
        admin = "\nYou are Admin for:"
        for j in rss_admin:
            admin += "\n\tRss Channel ID: {}\n".format(j.RssChannel.Customize)
        rss_member = models.RssMember.select().where(
            models.RssMember.Follows == models.Follows.get(Telegram_id=self.chat_id)
        )
        member = "\nYou are joined:"
        for k in rss_member:
            member += "\n\tRss Channel ID: {}\n".format(k.RssChannel.Customize)
        bot.send_message(chat_id=self.chat_id, text=master + admin + member)

    def __add(self):
        if not self.__grant(param_number=3):
            return
        id = self.param[1]
        title = self.param[2]
        link = self.param[3]
        if not self.__is_channel_exists(id):
            return
        if not self.__are_you_admin(id):
            return
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        if len(re.findall(pattern, link)) == 0:
            bot.send_message(chat_id=self.chat_id, text="please input the true http link.")
            return
        else:

            if not models.RssList.select().where(
                    models.RssList.Rss == link
            ).exists():
                models.RssList.create(
                    # title = check(link)
                    Rss=link,
                )
            if models.RssListFriendShip.select().where(
                models.RssListFriendShip.RssList == models.RssList.get(Rss=link),
                models.RssListFriendShip.RssChannel == models.RssChannel.get(Customize=id)
            ).exists():
                bot.send_message(chat_id=self.chat_id,text="you are add this.")
                return
            models.RssListFriendShip.create(
                RssList=models.RssList.get(Rss=link),
                RssChannel=models.RssChannel.get(Customize=id),
                CustomizeTitle=title
            )
            bot.send_message(chat_id=self.chat_id, text="Successful!")

    def __delete(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return
        if not self.__are_you_admin(id):
            return

        rss_id = self.param[2]
        if not models.RssList.select().where(
            models.RssList.ID == rss_id
        ).exists():
            bot.send_message(chat_id=self.chat_id,text="rss id not found.")
            return
        if not models.RssListFriendShip.select().where(
                models.RssListFriendShip.RssList == models.RssList.get(ID=rss_id),
                models.RssListFriendShip.RssChannel == models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="target rss link not found.")
            return
        models.RssListFriendShip.delete().where(
            models.RssListFriendShip.RssChannel == models.RssChannel.get(Customize=id),
            models.RssListFriendShip.RssList == models.RssList.get(ID=rss_id)
        ).execute()
        if not models.RssListFriendShip.select().where(
                models.RssListFriendShip.RssList == models.RssList.get(ID=rss_id)
        ).exists():
            models.DataBase.delete().where(
                models.DataBase.Form == models.RssList.get(ID=int(rss_id))
            ).execute()
            models.RssList.delete().where(
                models.RssList.ID == int(rss_id)
            ).execute()

        bot.send_message(chat_id=self.chat_id, text="Successful!")

    def __privilege(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        telegram_id = self.param[2]
        if not self.__is_channel_exists(id):
            return
        if models.RssChannel.get(Customize=id).Master != models.Follows.get(Telegram_id=self.chat_id):
            bot.send_message(chat_id=self.chat_id, text="sorry, you are not master for this channel.")
            return
        if not models.Follows.select().where(
                models.Follows.Telegram_id == telegram_id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="sorry,target telegram user not follow bot")
            return
        if models.RssAdmin.select().where(
            models.RssAdmin.Follows==models.Follows.get(Telegram_id=telegram_id),
            models.RssAdmin.RssChannel==models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id,text="target user is admin.")
            return
        models.RssAdmin.create(
            Follows=models.Follows.get(Telegram_id=telegram_id),
            RssChannel=models.RssChannel.get(Customize=id)
        )
        bot.send_message(chat_id=self.chat_id, text="Successful!")
        return

    def __change_pwd(self):
        pass

    def __update(self):
        bot.send_message(chat_id=self.chat_id, text="mei xie.")
        return

    def handle(self):
        # try:
        if self.command == "/help":
            self.__grant(1)
            bot.send_message(chat_id=self.chat_id,
                             text="Rss Pusher Usage:"
                                  "User:\n"
                                  "\t/create [id] Create a channel, other users can join your channel based on id"
                                  "\t/join [id] join the source and recv the rss push\n"
                                  "\t/leave [id] cancel recv the rss push.if you are master for this channel,"
                                  "this channel will delete\n"
                                  "\t/list [id] View the rss subscription link in the channel\n"
                                  "\t/myself View your own information, includi"
                                  "ng channels created/administrated/joined\n"
                                  "\t/help you see now\n"
                                  "Admin:\n"
                                  "\t/add [id] [title] [rss link] add the rss link\n"
                                  "\t/delete [id] [rss_id] delete the rss target.id from /list\n"
                                  "\t/privilege [id] [telegram_id] set ont follows to admin.(you must channel master)\n"
                                  "\t/update Only for developers.Update rss subscription now\n"
                             )
            return

        elif self.command == "/about":
            bot.send_message(chat_id=self.chat_id,
                             text="Made By 9bie's gongdi english and jiushi."
                                  "\nWeb:{}\nGithub: https://github.com/9bie/rsspusher".format(URL))
            return
        elif self.command == "/create":
            self.__create()
        elif self.command == "/join":
            self.__join()
        elif self.command == "/add":
            self.__add()
        elif self.command == "/delete":
            self.__delete()
        elif self.command == "/leave":
            self.__leave()
        elif self.command == "/list":
            self.__list()
        elif self.command == "/myself":
            self.__myself()
        elif self.command == "/privilege":
            self.__privilege()
        elif self.command == "/change_pwd":
            self.__change_pwd()
        elif self.command == "/update":
            self.__update()

        else:
            bot.send_message(chat_id=self.chat_id,
                             text="I don't know what you say,you can send /help for me.")
            return
        '''except Exception as e:
            if DEBUG is False:
                e = "*" * 20
            bot.send_message(chat_id=self.chat_id, text="RssPusher Exception:\n\t{}".format(e))'''


def send_all_follows(rss_channel, msg):
    try:
        channels = models.RssListFriendShip.select().where(
            models.RssListFriendShip.RssList==rss_channel
        )
        for c in channels:
            follows = models.RssMember.select().where(
                models.RssMember.RssChannel == c
            )
            for f in follows:
                bot.send_message(chat_id=f.Follows.Telegram_id, text=msg, parse_mode="html")
    except Exception as e:
        print("Have some errors:{}".format(e))
