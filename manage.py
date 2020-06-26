from flask import *
from bot import *
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/" + TELEGRAM_KEYS, methods=["POST"])
def tg_event():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message is None:
        return "Show me your TOKEN please!"
    data = update.message.to_dict()
    handle(data, update)

