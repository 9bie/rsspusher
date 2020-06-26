from config import *
import models
import telegram
bot = telegram.Bot(token=TELEGRAM_KEYS)


def handle(data,update):
    command = data["text"].split(" ")[0]
    if command == "/join":
        try:
            models.Follows.create(
                Telegram_id=update.message.chat_id,
                IsAdmin=False
            )
            bot.send_message(chat_id=update.message.chat_id,
                             text="Success")
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))

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
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))

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
                                 text="Param Error.")
                return

            if models.RssList.select(
                models.RssList.ID == int(data["text"].split(" ")[1])
                    ).exists:
                models.RssList.get(ID=int(data["text"].split(" ")[1])).delete_instance()
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Success!.")
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Have some error: {}".format(str(e)))
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
    elif command == "/help":
        bot.send_message(chat_id=update.message.chat_id,
                         text="User Leave:\n"
                              "\t/join recv the rss push\n"
                              "\t/leave cancel recv the rss push.\n"
                              "\t/list printf the rss list\n"
                              "\t/help you see now\n"
                              "Admin:\n"
                              "\t/add [title] [rss link] add the rss link\n"
                              "\t/delete [id] delete the rss target.id from /list\n"
                         )
    elif command == "/about":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Made By 9bie and jiushi.\nGithub: https://github.com/9bie/rsspusher")
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="I don't know what you say,you can send /help for me.")


def send_all_follows(msg):
    try:
        follows = models.Follows.select()
        for f in follows:
            bot.send_message(chat_id=f.Telegram_id,text=msg)
    except Exception as e:
        print("Have some errors:{}".format(e))