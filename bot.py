from config import *
import models
import telegram
bot = telegram.Bot(token=TELEGRAM_KEYS)


def handle(data,update):
    command = data["text"].split(" ")[0]
    if command == "/join":
        try:
            if not models.Follows.select().where(
                models.Follows.Telegram_id==update.message.chat_id,
            ).exists:
                models.Follows.create(
                    Telegram_id=update.message.chat_id,
                    IsAdmin=False
                )
                bot.send_message(chat_id=update.message.chat_id,
                             text="Success")
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You are followed.")
            return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return

    elif command == "/leave":
        try:
            if models.Follows.select().where(
                    models.Follows.Telegram_id==update.message.chat_id
            ).exists:
                models.Follows.get(Telegram_id=update.message.chat_id).delete_instance()
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Success")
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You are not in our list.")
                return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return

    elif command == "/add":
        try:
            if len(data["text"].split(" ")) != 3:
                bot.send_message(chat_id=update.message.chat_id,
                         text="Param Error.")
                return
            else:

                if models.Follows.select().where(
                    models.Follows.Telegram_id == update.message.chat_id,
                    models.Follows.IsAdmin == True
                ):
                    title = data["text"].split(" ")[1]
                    url = data["text"].split(" ")[2]
                    models.RssList.create(
                        Title=title,
                        Rss=url
                    )
                    bot.send_message(chat_id=update.message.chat_id,
                                     text="Success!.")
                else:
                    bot.send_message(chat_id=update.message.chat_id,
                            text="Sorry ,You are not Admin.")
                    return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
    elif command == "/delete":
        try:
            if len(data["text"].split(" ")) != 2 and\
                    models.Follows.select().where(
                        models.Follows.Telegram_id == update.message.chat_id,
                        models.Follows.IsAdmin == True):
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Param Error or you are not admin.")
                return

            if models.RssList.select(
                models.RssList.ID == int(data["text"].split(" ")[1])
                    ).exists:
                models.RssList.get(ID=int(data["text"].split(" ")[1])).delete_instance()
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Success!.")
                return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return
    elif command == "/list":
        try:
            items = models.RssList.select()
            str_list = ""
            for i in items:
                str_list += "ID: {}\n\tTitle:{}\n\tFeed:{}".format(i.ID,i.Title,i.Rss)
            bot.send_message(chat_id=update.message.chat_id,
                             text=str_list)
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return
    elif command == "/help":
        bot.send_message(chat_id=update.message.chat_id,
                         text="User:\n"
                              "\t/join recv the rss push\n"
                              "\t/leave cancel recv the rss push.\n"
                              "\t/list printf the rss list\n"
                              "\t/help you see now\n"
                              "Admin:\n"
                              "\t/add [title] [rss link] add the rss link\n"
                              "\t/delete [id] delete the rss target.id from /list\n"
                              "\t/myself get your web control's account.\n"
                              "\t/privilege [telegram_id] set ont follows to admin.\n"
                              "\t/change_pwd change you password!\n"
                              "\t/update update now and do not push to follows\n"
                         )
        return
    elif command == "/myself":
        try:
            if models.Follows.select().where(
                models.Follows.Telegram_id == update.message.chat_id,
                models.Follows.IsAdmin is True
            ).exists:
                u = models.Follows.get(Telegram_id=update.message.chat_id)
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Your web control account:\n\tusername:{}\n\tpassword:{}".format(u.Telegram_id
                                                                                                       , u.PassWD))
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You are not follows or not admin.")
                return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return
    elif command == "/privilege":
        try:
            if len(data["text"].split(" ")) != 2 and \
                    models.Follows.select().where(
                        models.Follows.Telegram_id == update.message.chat_id,
                        models.Follows.IsAdmin is True):
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Param Error or you are not admin.")
                return
            target_user = data["text"].split(" ")[1]

            if models.Follows.select().where(
                models.Follows.Telegram_id == int(target_user)
            ).exists:
                models.Follows.update(
                    IsAdmin=True,
                    Passwd=models.random_password()
                ).where(
                    models.Follows.Telegram_id == int(target_user)
                ).execute()
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Success!")
                return
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="User Not Found.")
                return

        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return
    elif command == "/change_pwd":
        try:
            if models.Follows.select().where(
                        models.Follows.Telegram_id == update.message.chat_id,
                        models.Follows.IsAdmin is True):
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You are not admin.")
                return

            passwd = models.random_password()
            models.Follows.update(
                    IsAdmin=True,
                    Passwd=passwd
                ).where(
                    models.Follows.Telegram_id == update.message.chat_id
                ).execute()
            bot.send_message(chat_id=update.message.chat_id,
                                 text="Success! Your new password is {}".format(passwd))
            return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return
    elif command == "/update":
        try:
            if models.Follows.select().where(
                        models.Follows.Telegram_id == update.message.chat_id,
                        models.Follows.IsAdmin is True):
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You are not admin.")
                return
            import threading, rss
            t = threading.Thread(target=rss.main, args=(True,))
            t.start()

            bot.send_message(chat_id=update.message.chat_id, text="Success!")
            return
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
            return
    elif command == "/about":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Made By 9bie's gongdi english and jiushi."
                              "\nWeb:{}\nGithub: https://github.com/9bie/rsspusher".format(URL))
        return
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="I don't know what you say,you can send /help for me.")
        return


def send_all_follows(msg):
    try:
        follows = models.Follows.select()
        for f in follows:
            bot.send_message(chat_id=f.Telegram_id,text=msg,parse_mode="html")
    except Exception as e:
        print("Have some errors:{}".format(e))