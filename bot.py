import re

import telegram

import models
from config import *

bot = telegram.Bot(token=TELEGRAM_KEYS)


class Bot:

    def __init__(self, update):
        self.update = update
        self.chat_id = update.message.chat_id
        self.data = update.message.to_dict()
        self.command = self.data["text"].split[0]
        self.param = self.data["text"].split

    def __grant(self, param_number):
        if len(self.param) < param_number:
            bot.send_message(chat_id=self.chat_id, text="Parameter error.")
            return
        if not models.Follows.select().where(
                models.Follows.Telegram_id == self.chat_id
        ).exists():
            models.Follows.create(
                Telegram_id=self.chat_id
            )

    def __is_channel_exists(self, id):
        if not models.RssChannel.select().where(
                models.RssChannel.Customize == id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="channel not found.")
            return False
        return True

    def __create(self):

        self.__grant(param_number=2)
        if models.RssChannel.select().where(
                Master=models.Follows.get(Telegram_id=self.chat_id)
        ).count() >= 3:
            bot.send_message(chat_id=self.chat_id, text="You have exceeded th"
                                                        "e limit for creating channels, up to three")
            return
        new_channel = models.RssChannel.create(
            Customize=self.param[1],
            Master=models.Follows.get(Telegram_id=self.chat_id)
        )
        models.RssAdmin.create(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChannel=new_channel
        )

        bot.send_message(chat_id=self.chat_id, text="Success, your channel id is{},"
                                                    " other users can join your"
                                                    " rss channel by this id".format(self.param[1]))

    def __join(self):
        self.__grant(param_number=2)
        id = self.param[1]
        if not models.RssChannel.select().where(
                models.RssChannel.Customize == id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="channel not found.")
            return
        models.RssMember.create(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChannel=models.RssChannel.get(Customize=id)
        )
        bot.send_message(chat_id=self.chat_id, text="Successful.")

    def __leave(self):
        self.__grant(param_number=2)
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return
        if not models.RssMember.select().where(
                Follows=models.Follows.get(Telegram_id=self.chat_id),
                RssChhannel=models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="you are not join this channel.")
            return
        models.RssMember.delete().where(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChhannel=models.RssChannel.get(Customize=id)
        ).execute()
        bot.send_message(chat_id=self.chat_id, text="Successful!")

    def __list(self):
        self.__grant(param_number=2)
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return
        results = ""
        rsslists = models.RssList.select().where(
            Form=models.RssChannel().get(Customize=id)
        )
        for i in rsslists:
            results += "Rss id: {}\n\tTitle:{}\n\tRss:{}\n\t".format(i.Form.Customize, i.Title, i.Rss)
        if results == "":
            bot.send_message(chat_id=self.chat_id, text="you are not join any channel.")
        else:
            bot.send_message(chat_id=self.chat_id, text=results)

    def __myself(self):
        pass

    def __add(self):
        self.__grant(param_number=3)
        id = self.param[1]
        title = self.param[2]
        link = self.param[3]
        if not self.__is_channel_exists(id):
            return
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        if len(re.findall(pattern, link)) == 0:
            bot.send_message(chat_id=self.chat_id, text="please input the true http link.")
            return
        else:
            models.RssList.create(
                Title=title,
                Rss=link,
                Form=models.RssChannel.get(Customize=id)
            )
            bot.send_message(chat_id=self.chat_id, text="Successful!")

    def __delete(self):
        self.__grant(param_number=2)
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return
        rss_id = self.param[2]
        if not models.RssList.select().where(ID=rss_id).exists():
            bot.send_message(chat_id=self.chat_id, text="target rss link not found.")
            return
        models.RssList.delete().where(
            models.RssList.Form == models.RssChannel.get(Customize=id),
            ID=int(rss_id)
        ).execute()
        bot.send_message(chat_id=self.chat_id, text="Successful!")

    def __privilege(self):
        self.__grant(param_number=2)
        id = self.param[1]
        telegram_id = self.param[2]
        if not self.__is_channel_exists(id):
            return
        if models.RssChannel.get(Customize=id).Master != models.Follows.get(Telegram_id=self.chat_id):
            bot.send_message(chat_id=self.chat_id, text="sorry, you are not master for this channel.")
            return
        if not models.Follows.select().where(
                Telegram_id=telegram_id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="sorry,target telegram user not follow bot")
            return
        models.RssAdmin.create(
            Follows=models.Follows.get(Telegram_id=telegram_id),
            RssChannel=models.RssChannel.get(Customize=id)
        )
        return "Successful!"

    def __change_pwd(self):
        pass

    def __update(self):
        bot.send_message(chat_id=self.chat_id, text="mei xie.")

    def handle(self):
        try:
            if self.command == "/help":
                bot.send_message(chat_id=self.chat_id,
                                 text="[] is is param,<> is return"
                                      "User:\n"
                                      "\t/create <id> create rss subscription source,and return the subscription id"
                                      "\t/join [id] join the source and recv the rss push\n"
                                      "\t/leave [id] cancel recv the rss push.\n"
                                      "\t/list [id] <rss_id_list> view the subscription source sub list\n"
                                      "\t/myself <joined list,web account>get yourself\n"
                                      "\t/help you see now\n"
                                      "Admin:\n"
                                      "\t/add [id] [title] [rss link] add the rss link\n"
                                      "\t/delete [id] [rss_id] delete the rss target.id from /list\n"
                                      "\t/privilege [id] [telegram_id] set ont follows to admin.(you must channel master)\n"
                                      "\t/change_pwd [new pwd]change you password!\n"
                                      "\t/update update now and do not push to follows\n"
                                 )
                return

            elif self.command == "/about":
                bot.send_message(chat_id=self.chat_id,
                                 text="Made By 9bie's gongdi english and jiushi."
                                      "\nWeb:{}\nGithub: https://github.com/9bie/rsspusher".format(URL))
                return
            elif self.command == "/create":
                self.__create()
            else:
                bot.send_message(chat_id=self.chat_id,
                                 text="I don't know what you say,you can send /help for me.")
                return
        except Exception as e:
            if DEBUG:
                e = "*" * 20
            bot.send_message(chat_id=self.chat_id, text="RssPusher Exception:\n\t{}".format(e))


def send_all_follows(rss_channel,msg):
    try:
        follows = models.RssMember.select().where(
            models.RssMember.RssChannel == models.RssChannel.get(ID=rss_channel)
        )
        for f in follows:
            bot.send_message(chat_id=f.Follows.Telegram_id, text=msg, parse_mode="html")
    except Exception as e:
        print("Have some errors:{}".format(e))
