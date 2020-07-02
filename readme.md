# Rss Pusher
推送指定站点RSS消息到web和tg列表

请使用python3运行，当然理论上python2也是可以的

## how to build
修改 `config.py` 

填写好`TELEGRAM_KEYS`，为你的bot keys

填写好`URL`，确保tg服务器能访问到你的`URL/tg_keys`

填写好`YOUR_CHAT_ID_FOR_ADMIN`为管理员的id，可以通过`@get_id`这个bot来获取

修改`TIMER`为获取rss的间隔，单位秒，默认五分钟

之后运行`models.py`创建数据库

访问`URL/start`启动bot。

最后直接运行`python manager.py`可以用debug模式运行，然后用nginx反代。

或者使用正规方式`gunicorn -w 2 -b 127.0.0.1:5000 manage:app`启动服务

之后用nginx反代本地5000端口即可。 

访问 `URL/start` 启动bot。（web面板还没写）

之后找到你的bot发送`/help`，bot正确运行

## todo

    - tg交互 √
    - web交互 x
    
## 用到的模块

    - python-telegram-bot
    - peewee
    - feedparser