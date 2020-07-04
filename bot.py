# coding:utf-8
import re

import telegram

import models
from config import *
from time import sleep
# from rss import check
bot = telegram.Bot(token=TELEGRAM_KEYS)


class Bot:

    def __init__(self, update):
        self.update = update
        if update.message is None:
            self.command = ""
            self.param = []
            return
        self.chat_id = update.message.chat_id
        self.data = update.message.to_dict()
        if "text" not in self.data:
            self.command = ""
            self.param = []
        else:
            self.command = self.data["text"].split()[0]
            self.param = self.data["text"].split()

    def __grant(self, param_number):
        if len(self.param) < param_number:
            bot.send_message(chat_id=self.chat_id, text="参数错误.可以发送/help查询如何使用")
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
            bot.send_message(chat_id=self.chat_id, text="找不到频道.")
            return False
        return True

    def __are_you_admin(self, channel_customize):
        if not models.RssAdmin.select().where(
                models.RssAdmin.RssChannel == models.RssChannel.get(Customize=channel_customize),
                models.RssAdmin.Follows == models.Follows.get(Telegram_id=self.chat_id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="你不是该频道的管理员.")
            return False
        return True

    def __create(self):

        if not self.__grant(param_number=2):
            return
        if models.RssChannel.select().where(
                models.RssChannel.Master == models.Follows.get(Telegram_id=self.chat_id)
        ).count() >= 3:
            bot.send_message(chat_id=self.chat_id, text="你已经超出最大频道限制（数量为3条，请联系管理员 @bakabie）")
            return
        is_match = re.match("^[_a-zA-Z0-9]+$",self.param[1])
        if not is_match:
            bot.send_message(chat_id=self.chat_id,text="仅限字母数字下划线且不超过8位")
            return
        if len(self.param[1])> 8:
            bot.send_message("仅限字母数字下划线且不超过8位")
            return
        if models.RssChannel.select().where(
                models.RssChannel.Customize == self.param[1]
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="频道已经存在，请换个id.")
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

        bot.send_message(chat_id=self.chat_id, text="成功, 你创建的频道id为:\n\t - {}\n"
                                                    " 其他用户可以根据这个id加入你的频道接受推送.\n你的主页为:\n\t - {}".format(self.param[1],URL+"/"+self.param[1]),)

    def __join(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        if not models.RssChannel.select().where(
                models.RssChannel.Customize == id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="找不到频道.")
            return
        if models.RssMember.select().where(
                models.RssMember.Follows == models.Follows.get(Telegram_id=self.chat_id),
                models.RssMember.RssChannel == models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="你已经加入了这个频道.")
            return
        models.RssMember.create(
            Follows=models.Follows.get(Telegram_id=self.chat_id),
            RssChannel=models.RssChannel.get(Customize=id)
        )
        bot.send_message(chat_id=self.chat_id, text="成功.")

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
            bot.send_message(chat_id=self.chat_id, text="你已经加入了这个频道.")
            return
        models.RssMember.delete().where(
            models.RssMember.Follows == models.Follows.get(Telegram_id=self.chat_id),
            models.RssMember.RssChannel == models.RssChannel.get(Customize=id)
        ).execute()
        if models.RssChannel.get(Customize=id).Master == models.Follows.get(Telegram_id=self.chat_id):
            check = []
            for i in models.RssListFriendShip.select().where(
                    models.RssListFriendShip.RssChannel == models.RssChannel.get(Customize=id)):
                check.append(i.RssList)
            models.RssListFriendShip.delete().where(
                models.RssListFriendShip.RssChannel == models.RssChannel.get(Customize=id)).execute()
            for rss in check:
                if not models.RssListFriendShip.select().where(
                        models.RssListFriendShip.RssList == rss
                ).exists():
                    models.RssList.delete().where(models.RssList.ID == rss.ID).execute()
                    models.DataBase.delete().where(models.DataBase.Form == rss).execute()
            models.RssList.delete().where(models.RssList.ID)
            models.RssMember.delete().where(
                models.RssMember.RssChannel == models.RssChannel.get(Customize=id)).execute()
            models.RssAdmin.delete().where(models.RssAdmin.RssChannel == models.RssChannel.get(Customize=id)).execute()
            models.RssChannel.delete().where(models.RssChannel.Customize == id).execute()
        bot.send_message(chat_id=self.chat_id, text="成功!")

    def __list(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        if not self.__is_channel_exists(id):
            return
        results = "<b>Channel ID </b>:{}".format(i.RssChannel.Customize)
        rsslists = models.RssListFriendShip.select().where(
            models.RssListFriendShip.RssChannel == models.RssChannel().get(Customize=id)
        )
        for i in rsslists:
            results += "Rss id: {}\n\t - Title:{}\n\t - Rss:{}\n\t".format(
                                                                                                i.RssList.ID,
                                                                                                i.CustomizeTitle,
                                                                                                i.RssList.Rss)
        if results == "":
            bot.send_message(chat_id=self.chat_id, text="没有任何东西在频道里.")
        else:
            bot.send_message(chat_id=self.chat_id, text=results, parse_mode="html")

    def __myself(self):
        if not self.__grant(param_number=1):
            return
        master = "\n*You are master for*:"
        rss_master = models.RssChannel.select().where(
            models.RssChannel.Master == models.Follows.get(Telegram_id=self.chat_id)
        )

        for i in rss_master:
            master += "\n\t - Rss Channel ID: {}\n".format(i.Customize)
        rss_admin = models.RssAdmin.select().where(
            models.RssAdmin.Follows == models.Follows.get(Telegram_id=self.chat_id)
        )
        admin = "\n*You are Admin for*:"
        for j in rss_admin:
            admin += "\n\t - Rss Channel ID: {}\n".format(j.RssChannel.Customize)
        rss_member = models.RssMember.select().where(
            models.RssMember.Follows == models.Follows.get(Telegram_id=self.chat_id)
        )
        member = "\n*You are joined*:"
        for k in rss_member:
            member += "\n\t - Rss Channel ID: {}\n".format(k.RssChannel.Customize)
        bot.send_message(chat_id=self.chat_id, text=master + admin + member, parse_mode="markdown")

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
            bot.send_message(chat_id=self.chat_id, text="请输入正确的rss连接")
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
                bot.send_message(chat_id=self.chat_id, text="您已经加入了")
                return
            models.RssListFriendShip.create(
                RssList=models.RssList.get(Rss=link),
                RssChannel=models.RssChannel.get(Customize=id),
                CustomizeTitle=title
            )
            bot.send_message(chat_id=self.chat_id, text="成功!")

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
            bot.send_message(chat_id=self.chat_id, text="找不到rss id.")
            return
        if not models.RssListFriendShip.select().where(
                models.RssListFriendShip.RssList == models.RssList.get(ID=rss_id),
                models.RssListFriendShip.RssChannel == models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="该频道为添加这个rss.")
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

        bot.send_message(chat_id=self.chat_id, text="成功!")

    def __privilege(self):
        if not self.__grant(param_number=2):
            return
        id = self.param[1]
        telegram_id = self.param[2]
        if not self.__is_channel_exists(id):
            return
        if models.RssChannel.get(Customize=id).Master != models.Follows.get(Telegram_id=self.chat_id):
            bot.send_message(chat_id=self.chat_id, text="抱歉,你不是该频道的管理员.")
            return
        if not models.Follows.select().where(
                models.Follows.Telegram_id == telegram_id
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="抱歉,目标并未加入我们这个bot，目标至少要在我们这发送一条以上正确指令(/help)就行")
            return
        if models.RssAdmin.select().where(
                models.RssAdmin.Follows == models.Follows.get(Telegram_id=telegram_id),
                models.RssAdmin.RssChannel == models.RssChannel.get(Customize=id)
        ).exists():
            bot.send_message(chat_id=self.chat_id, text="目标用户已经是管理员了")
            return
        models.RssAdmin.create(
            Follows=models.Follows.get(Telegram_id=telegram_id),
            RssChannel=models.RssChannel.get(Customize=id)
        )
        bot.send_message(chat_id=self.chat_id, text="成功!")
        return

    def __change_pwd(self):
        pass

    def __update(self):
        bot.send_message(chat_id=self.chat_id, text="mei xie.")
        return

    def handle(self):
        try:
            if self.command == "/help":
                self.__grant(1)
                if len(self.param) >= 2:
                    if self.param[1] == "en":
                        bot.send_message(chat_id=self.chat_id,
                                         text="*Rss Pusher Usage:*\n"
                                              "*User:*\n"
                                              "\t - /create [id] Create a channel, other users can join your channel based on id"
                                              "\t - /join [id] join the source and recv the rss push\n"
                                              "\t - /leave [id] cancel recv the rss push.if you are master for this channel,"
                                              "this channel will delete\n"
                                              "\t - /list [id] View the rss subscription link in the channel\n"
                                              "\t - /myself View your own information, includi"
                                              "ng channels created/administrated/joined\n"
                                              "\t - /help you see now\n"
                                              "*Admin:*\n"
                                              "\t - /add [id] [title] [rss link] add the rss link\n"
                                              "\t - /delete [id] [rss_id] delete the rss target.id from /list\n"
                                              "\t - /privilege [id] [telegram_id] set ont follows to admin.(you must channel master)\n"
                                              "\t - /update Only for developers.Update rss subscription now\n"
                                         , parse_mode="markdown")
                        return
                else:
                    bot.send_message(chat_id=self.chat_id,
                                     text="*Rss Pusher Usage:*\n*"
                                          "User:*\n"
                                          "\t- /create [id] 创建个rss订阅频道，其他用户可以根据这个id加入你的频道\n"
                                          "\t- /join [id] 加入一个频道，之后你将会收到这个频道的更新推送\n"
                                          "\t- /leave** [id] 离开某个频道，如果你是这个频道的创建者，频道将会删除\n"
                                          "\t- /list [id] 查看该频道的rss订阅列表\n"
                                          "\t- /myself 查看你创建/管理/加入的频道\n"
                                          "\t- /help 你现在正在看到的\n"
                                          "*Admin:*\n"
                                          "\t- /add [id] [title] [rss link] 给频道添加一个rss订阅链接\n"
                                          "\t- /delete [id] [rss_id] 删除频道内一个rss订阅链接，rss_id可以从 **/list** 里查看\n"
                                          "\t- /privilege [id] [telegram_id] 设置一个telegram用户为管理员，该成员必须再本频道发送过 /help 或以外的参数（你必须为频道创建者从才能使用本命令）\n"
                                          "\t- /update 仅对开发者开放，立刻更新所有rss推送\n"
                                     , parse_mode="markdown"
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
            elif self.command == "":
                return
            else:
                if self.chat_id >= 0:
                    bot.send_message(chat_id=self.chat_id,
                                     text="我不知道你在说啥,你可以发送/help给我查询.")
                return
        except Exception as e:
            if DEBUG is False:
                e = "*" * 20
            bot.send_message(chat_id=self.chat_id, text="*RssPusher Exception*:\n\t - {}".format(e),
                             parse_mode="markdown")


def send_all_follows(rsslist, msg):
    try:

        rssfriendship = models.RssListFriendShip.select().where(
            models.RssListFriendShip.RssList == rsslist
        )
        for c in rssfriendship:
            follows = models.RssMember.select().where(
                models.RssMember.RssChannel == c.RssChannel
            )
            for f in follows:

                bot.send_message(chat_id=f.Follows.Telegram_id, text=msg, parse_mode="html")
    except Exception as e:
        print("Have some errors:{}".format(e))
