from flask import *
#from flask_login import login_user, logout_user, login_required,current_user
from models import DataBase
from bot import *
app = Flask(__name__)


@app.route("/start")
def start():
    bot.setWebhook(webhook_url=WEBHOOKING)
    return "Bot starting...",404


@app.route("/admin")
def admin():
    user=request.form['user']
    passwd=request.form['passwd']
    pass# gugugugu


@app.route('/')
@app.route("/<int:page>")
def index(page=1):
    try:
        lists = []
        items = DataBase.select().paginate(page, 50)
        for i in items:
            print(i.ID,i.Form,i.Url,i.Summary)
            lists.append(
                {
                    "Form":i.Form,
                    "Title":i.Title,
                    "Url":i.Url,
                    "Summary": i.Summary if i.Summary is not None else ""
                 }
            )

        return render_template('index.html',items=lists )
    except Exception as e:
        return "Have some error:{}\nPlease link @bakabie".format(e),500


@app.route("/" + TELEGRAM_KEYS, methods=["POST"])
def tg_event():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message is None:
        return "Show me your TOKEN please!"
    data = update.message.to_dict()
    handle(data, update)
    return "ok"


if __name__ == '__main__':
    app.run()
