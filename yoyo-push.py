# -*- coding: utf-8 -*-

import calendar
import datetime
from datetime import date
from configparser import ConfigParser
import pymysql
import time

import schedule
import telepot
from telepot.loop import MessageLoop
from log import logger


# 读取配置
def read_config(config_path):
    cfg = ConfigParser()
    cfg.read(config_path, encoding='utf-8')
    env = cfg.get('Environment', 'env')
    proxy = cfg.get('Environment', 'proxy')
    timed_task = cfg.get('Environment', 'timed_task')
    host = cfg.get('MySQL', 'host')
    user = cfg.get('MySQL', 'user')
    password = cfg.get('MySQL', 'password')
    port = cfg.get('MySQL', 'port')
    db = cfg.get('MySQL', 'db')
    bot_name = cfg.get('TelegramBot', 'bot_name')
    token = cfg.get('TelegramBot', 'token')
    chat_id = cfg.get('TelegramBot', 'chat_id')
    config_dict = {}
    config_dict['env'] = env
    config_dict['proxy'] = proxy
    config_dict['timed_task'] = timed_task
    config_dict['host'] = host
    config_dict['user'] = user
    config_dict['password'] = password
    config_dict['port'] = port
    config_dict['db'] = db
    config_dict['bot_name'] = bot_name
    config_dict['token'] = token
    config_dict['chat_id'] = chat_id
    return config_dict


# 查询推送内容
def query_push_content(config_dict):
    db = pymysql.connect(host=str(config_dict['host']), user=str(config_dict['user']),
                            password=str(config_dict['password']), port=int(config_dict['port']),
                            db=str(config_dict['db']), charset='utf8')
    cursor = db.cursor()

    content_list = []
    try:
        sql = "select * from push_content where is_deleted = 0 order by update_time asc"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            item = {}
            item['id'] = result[0]
            item['type'] = result[1]
            item['persion'] = result[2]
            item['day'] = result[3]
            item['memorial'] = result[4]
            item['desc'] = result[5]
            content_list.append(item)
    except Exception as e:
        logger.error(e)
    cursor.close()
    return content_list


# 分类推送内容
def classify_push_content(content_list):
    birthday_list = []
    memorial_day_list = []
    birthday_id = 0
    memorial_day_id = 0
    for content in content_list:
        if content['type'] == "生日":
            birthday_id = birthday_id + 1
            content['id'] = birthday_id
            birthday_list.append(content)
        elif content['type'] == "纪念日":
            memorial_day_id = memorial_day_id + 1
            content['id'] = memorial_day_id
            memorial_day_list.append(content)
    return memorial_day_list, birthday_list


# 生成推送内容
def gene_push_content(memorial_day_list, birthday_list):

    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    curr_date = date.today()
    week = calendar.day_name[curr_date.weekday()]

    push_list = []
    push_list.append('〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓')
    push_list.append('⏳ yoyo-push')
    push_list.append("🔅 " + now + " " + week)
    push_list.append('〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓')
    push_list.append('############## 👻 纪念日 ##############')
    for memorial_day_item in memorial_day_list:
        id = memorial_day_item['id']
        persion = memorial_day_item['persion']
        desc = memorial_day_item['desc']
        day_count = (datetime.datetime.now() - memorial_day_item['day']).days + 1
        memorial = memorial_day_item['memorial']
        push_list.append("{}. 与{}{}距今已经{}天，纪念日为{}".format(id, persion, desc, day_count, memorial))
    if len(memorial_day_list) == 0:
        push_list.append("👀 暂无纪念日")

    push_list.append('############### 👻 生日 ###############')
    push_list.append('>>> 今日 ')
    today_num = 0
    for birthday_item in birthday_list:
        day_count = (birthday_item['day'].replace(year=curr_date.year) - datetime.datetime.now()).days + 1
        if day_count < 0:
            day_count = (birthday_item['day'].replace(year=curr_date.year + 1) - datetime.datetime.now()).days + 1
        if day_count == 0:
            today_num = today_num + 1
            persion = birthday_item['persion']
            memorial = birthday_item['memorial']
            push_list.append("{}. {}，生日为{}（距今{}天）".format(today_num, persion, memorial, day_count))
            birthday_list.remove(birthday_item)
    if today_num == 0:
        push_list.append("👀 暂无今日过生日的朋友")
    push_list.append('>>> 7日内 ')
    week_num = 0
    for birthday_item in birthday_list:
        day_count = (birthday_item['day'].replace(year=curr_date.year) - datetime.datetime.now()).days + 1
        if day_count < 0:
            day_count = (birthday_item['day'].replace(year=curr_date.year + 1) - datetime.datetime.now()).days + 1
        if 7 > day_count >= 0:
            week_num = week_num + 1
            persion = birthday_item['persion']
            memorial = birthday_item['memorial']
            push_list.append("{}. {}，生日为{}（距今{}天）".format(week_num, persion, memorial, day_count))
            birthday_list.remove(birthday_item)
    if week_num == 0:
        push_list.append("👀 暂无7日内过生日的朋友")
    push_list.append('>>> 30日内 ')
    mouth_num = 0
    for birthday_item in birthday_list:
        day_count = (birthday_item['day'].replace(year=curr_date.year) - datetime.datetime.now()).days + 1
        if day_count < 0:
            day_count = (birthday_item['day'].replace(year=curr_date.year + 1) - datetime.datetime.now()).days + 1
        if 30 > day_count >= 0:
            mouth_num = mouth_num + 1
            persion = birthday_item['persion']
            memorial = birthday_item['memorial']
            push_list.append("{}. {}，生日为{}（距今{}天）".format(mouth_num, persion, memorial, day_count))
            birthday_list.remove(birthday_item)
    if mouth_num == 0:
        push_list.append("👀 暂无30日内过生日的朋友")
    push_list.append('〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓')

    push_str = ""
    for push_item in push_list:
        push_str = push_str + str(push_item) + "\n\n"
    return push_str


# 消息推送的结果
def push_list():
    content_list = query_push_content(config_dict)
    memorial_day_list, birthday_list = classify_push_content(content_list)
    push_str = gene_push_content(memorial_day_list, birthday_list)
    bot.sendMessage(str(config_dict['chat_id']), push_str)
    logger.info(push_str)


# 处理 Telegram Bot 消息
def handle(msg):
    if msg['text'] == '/list':
        push_list()
    if msg['text'] == '/data':
        content_list = query_push_content(config_dict)
        push_str = ""
        for push_item in content_list:
            push_str = push_str + str(push_item) + "\n\n"
        bot.sendMessage(str(config_dict['chat_id']), push_str)


if __name__ == '__main__':
    config_path = './config.ini'
    config_dict = read_config(config_path)
    if config_dict['env'] == "dev":
        telepot.api.set_proxy(str(config_dict['proxy']))
    bot = telepot.Bot(str(config_dict['token']))
    MessageLoop(bot, handle).run_as_thread()
    logger.info('Listening ...')
    # 定时任务：每日指定时间，自动发送一次推送
    schedule.every().day.at(str(config_dict['timed_task'])).do(push_list)
    while True:
        schedule.run_pending()  # 运行所有可以运行的定时任务
        time.sleep(1)





