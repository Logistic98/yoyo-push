## yoyo-push

一个用于推送好友生日及好友纪念日的 Telegram Bot。详见我的博客：[Telegram及Telegram-bot使用指南.html](https://www.eula.club/blogs/Telegram及Telegram-bot使用指南.html)

### 1. 申请自己的 Telegram Bot

#### 1.1 申请 Telegram Bot

 找 BotFather 官方机器人申请自己的 Telegram Bot，需要记录下：BotName、TOKEN、CHATID等信息。

- Step1：在Telegram中添加`BotFather`这个账号，然后依次发送`/start`，`/newbot`，按照提示即可创建一个新的机器人。记下来给你生成的token。
- Step2：搜索刚刚创建的机器人的名字，并给它发送一条消息。（注意：需要先与机器人之间创建会话，机器人才能下发消息，否则机器人无法主动发送消息）
- Step3：在Telegram中搜索`userinfobot`，并给它发送一条消息，它会返回给你`chatid`，将它也记下来。

#### 1.2 修改 Telegram Bot 头像

还是找 BotFather 官方机器人，先发送`/setuserpic`，它会让你选择为哪个Bot修改，选择完之后发送头像图片给它即可。

注：头像以图片的形式发送，不要以文件的形式发送（发送时点上那个压缩图片即为图片的形式发送）

### 2. 运行及部署

#### 2.1 项目结构

项目结构如下：

```
.
├── Dockerfile
├── README.md
├── build.sh
├── config.ini.example
├── log.py
├── requirements.txt
├── sql
│   └── push_content_structure.sql
└── yoyo-push.py
```

#### 2.2 本地运行

Step1：安装项目依赖

```
$ pip install -r requirements.txt
```

Step2：创建mysql数据库并导入数据

创建数据库及数据表，自行插入数据。

```sql
CREATE DATABASE push_content DEFAULT CHARSET=utf8 DEFAULT COLLATE utf8_unicode_ci;

CREATE TABLE `push_content` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `type` varchar(255) NOT NULL COMMENT '类型',
  `person` varchar(255) DEFAULT NULL COMMENT '有关的人',
  `day` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '实际日期',
  `identity` varchar(255) DEFAULT NULL COMMENT '身份',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `is_deleted` int(11) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=190 DEFAULT CHARSET=utf8mb4;
```

Step3：修改配置文件

将 config.ini.example 重命名为 config.ini，并修改其中的配置项，本地开发测试需要设置代理

Step4：运行程序进行测试

运行 yoyo-push.py 程序，在你的Telegram Bot中输入 /list 、/data 命令查看结果。

#### 2.3 境外服务器部署

step1：准备docker环境。

step2：将项目整个上传到服务器，赋予可执行权限并运行build.sh脚本。