# Rss Pusher
推送指定站点RSS消息到web和tg列表

## how to use
修改 `config.py` 

填写好`TELEGRAM_KEYS`，为你的bot keys

填写好`URL`，确保tg服务器能访问到你的`URL/tg_keys`

填写好`YOUR_CHAT_ID_FOR_ADMIN`为管理员的id，可以通过`@get_id`这个bot来获取



之后运行`models.py`创建数据库

访问`URL/start`启动bot

之后找到你的bot发送/help即可

之后把`rss.py`加入定时任务


## todo

    - <del>tg交互</del>已完成
    - web交互