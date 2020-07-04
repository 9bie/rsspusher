from threading import Timer, Thread

from time import sleep

from flask import *
import rss
from bot import *
# from flask_login import login_user, logout_user, login_required,current_user
from models import DataBase

app = Flask(__name__)

Timer(TIMER, rss.main).start()


@app.route('/')
@app.route("/<id>")
def index(id=""):
    page = request.args.get('page', '')
    if not page:
        page = 0
    else:
        page = int(page)
    try:
        if id == "":
            return render_template('index.html')
        else:
            lists = []
            if not models.RssChannel.select().where(
                    models.RssChannel.Customize == id
            ).exists():
                return "channel not found", 404
            items = DataBase.select().where(
                DataBase.Form == models.RssChannel.get(Customize=id)
            ).paginate(page, 50)
            for i in items:
                lists.append(
                    {
                        "Form": models.RssListFriendShip.get(RssList=i.Form).CustomizeTitle,
                        "Title": i.Title,
                        "Url": i.Url,
                        "Summary": i.Summary if i.Summary is not None else ""
                    }
                )
            return render_template('subindex.html', items=lists)
    except Exception as e:
        return "Have some error:{}\nPlease link @bakabie".format(e), 500


@app.route("/" + TELEGRAM_KEYS, methods=["POST"])
def tg_event():

    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message is None:
        return "Show me your TOKEN please!"
    Bot(update).handle()
    return "ok"


def update():
    update_id = 0
    while True:
        bot.deleteWebhook()
        if update_id == 0:
            updates = telegram.Bot(TELEGRAM_KEYS).get_updates()
        else:
            updates = telegram.Bot(TELEGRAM_KEYS).get_updates(offset=update_id)
        for update in updates:
            update_id = update.update_id + 1
            print(update)
            Bot(update).handle()
        sleep(3)


if not IS_WEBHOOK:
    Thread(target=update).start()

if __name__ == '__main__':
    app.run()
