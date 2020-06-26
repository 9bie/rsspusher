# Rss Pusher
推送指定站点RSS消息到web和tg列表

## how to use
修改 `config.py` ，填写好`telegram_bot_keys`，再填写好url，确保tg服务器能访问到你的URL/tg_keys，之后找到你的bot发送help即可

之后运行`models.py`创建数据库

之后把`rss.py`加入定时任务


## todo

    - <del>tg交互</del>已完成
    - web交互