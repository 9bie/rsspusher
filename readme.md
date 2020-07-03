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


# how to use
## en
###Rss Pusher Usage

#### User
 - **/create** [id] Create a channel, other users can join your channel based on id
 - **/join** [id] join the source and recv the rss push
 - **/leave** [id] cancel recv the rss push.if you are master for this channel,this channel will delete
 - **/list** [id] View the rss subscription link in the channel
 - **/myself**  View your own information, including channels created/administrated/joined
 - **/help** you see now
#### Admin
 - **/add** [id] [title] [rss link] add the rss link
 - **/delete** [id] [rss_id] delete the rss target.id from **/list**
 - **/privilege** [id] [telegram_id] set ont follows to admin.(you must channel master)
 - **/update** Only for developers.Update rss subscription now
 ## zh
 #### User
 - **/create** [id] 创建个rss订阅频道，其他用户可以根据这个id加入你的频道
 - **/join** [id] 加入一个频道，之后你将会收到这个频道的更新推送
 - **/leave** [id] 离开某个频道，如果你是这个频道的创建者，频道将会删除
 - **/list** [id] 查看该频道的rss订阅列表
 - **/myself** 查看你创建/管理/加入的频道
 - **/help** 你现在正在看到的
#### Admin
 - **/add** [id] [title] [rss link] 给频道添加一个rss订阅链接
 - **/delete** [id] [rss_id] 删除频道内一个rss订阅链接，rss_id可以从 **/list** 里查看
 - **/privilege** [id] [telegram_id] 设置一个telegram用户为管理员，该成员必须再本频道发送过 **/help** 或以外的参数（你必须为频道创建者从才能使用本命令）
 - **/update** 仅对开发者开放，立刻更新所有rss推送
 
## todo

### web主页
定制不同的rsschannel的不同独立rss主页页面
    
## 用到的模块

    - python-telegram-bot
    - peewee
    - feedparser