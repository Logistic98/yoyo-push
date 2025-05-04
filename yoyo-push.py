# -*- coding: utf-8 -*-

import datetime
from configparser import ConfigParser
import pymysql
import time
import schedule
import telepot
from telepot.loop import MessageLoop
from log import logger
from borax.calendars.lunardate import LunarDate


def read_config(config_path):
    cfg = ConfigParser()
    cfg.read(config_path, encoding='utf-8')
    config_dict = {k: v for section in cfg.sections() for k, v in cfg.items(section)}
    return config_dict


def query_push_content(config):
    with pymysql.connect(**config, cursorclass=pymysql.cursors.DictCursor) as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM push_content WHERE is_deleted = 0 ORDER BY update_time ASC")
            results = cursor.fetchall()
    content_list = [
        {
            'id': row['id'],
            'type': row['type'],
            'person': row['person'],
            'day': row['day'],
            'memorial': row['day'].strftime('%m月%d日'),
            'desc': row['desc']
        }
        for row in results
    ]
    return content_list


def classify_push_content(content_list):
    return [
        [x for x in content_list if x['type'] == type_]
        for type_ in ['纪念日', '生日']
    ]


def calculate_days_until_next_lunar_birthday(month, day, today):
    current_year = today.year
    try:
        this_year_lunar_birthday = LunarDate(current_year, month, day).to_solar_date()
        if this_year_lunar_birthday >= today:
            return (this_year_lunar_birthday - today).days
    except ValueError:
        pass
    for next_year in range(current_year + 1, current_year + 3):
        try:
            next_year_lunar_birthday = LunarDate(next_year, month, day).to_solar_date()
            return (next_year_lunar_birthday - today).days
        except ValueError:
            continue
    return None


def generate_push_content(memorial_day_list, birthday_list):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    week = datetime.datetime.now().strftime("%A")
    curr_date = datetime.datetime.now().date()

    time_frames = [(">>> 今日 ", 0, 0), (">>> 7日内 ", 1, 7), (">>> 30日内 ", 8, 30)]

    sections = [
        '〓' * 18,
        '⏳ yoyo-push',
        f"🔅 {now} {week}",
        '〓' * 18,
    ]

    sections += ['########## 👻 纪念日 ##########']
    for item in memorial_day_list:
        days_diff = (datetime.datetime.now() - item['day']).days + 1
        desc = item.get('desc', '')
        sections.append(f"与{item['person']}{desc}距今已经{days_diff}天，纪念日为{item['memorial']}")

    if not memorial_day_list:
        sections.append("👀 暂无纪念日")

    sections += ['########### 👻 生日 ###########']
    birthday_data = []
    for item in birthday_list:
        try:
            solar_date = item['day'].date()
            lunar_date = LunarDate.from_solar_date(solar_date.year, solar_date.month, solar_date.day)
            lunar_month, lunar_day = lunar_date.month, lunar_date.day
            lunar_day_count = calculate_days_until_next_lunar_birthday(lunar_month, lunar_day, curr_date)
            day_count = (solar_date.replace(year=curr_date.year) - curr_date).days
            if day_count < 0:
                day_count = (solar_date.replace(year=curr_date.year + 1) - curr_date).days

            lunar_birthday_str = f"{lunar_month}月{lunar_day}日"
            birthday_data.append((item, day_count, lunar_day_count, lunar_birthday_str))
        except Exception as e:
            logger.error(f"Error converting date for {item['person']}: {e}")

    for title, min_days, max_days in time_frames:
        frame_items = [(data[0], data[1], data[2], data[3])
                       for data in birthday_data
                       if max_days >= data[1] >= min_days or max_days >= data[2] >= min_days]
        sections.append(title)
        if frame_items:
            for idx, (item, day_count, lunar_day_count, lunar_birthday_str) in enumerate(frame_items, start=1):
                sections.append(
                    f"{idx}. {item['person']}，阳历生日为{item['memorial']}（距今{day_count}天），农历生日为{lunar_birthday_str}（距今{lunar_day_count}天）")
        else:
            sections.append(f"👀 暂无{title.strip().replace('>>> ', '')}过生日的朋友")

    sections.append('〓' * 18)
    return '\n\n'.join(sections) + '\n\n'


def push_list():
    config = read_config('./config.ini')
    content_list = query_push_content({
        'host': config['host'],
        'user': config['user'],
        'password': config['password'],
        'port': int(config['port']),
        'db': config['db'],
        'charset': 'utf8'
    })
    memorial_day_list, birthday_list = classify_push_content(content_list)
    push_str = generate_push_content(memorial_day_list, birthday_list)
    bot.sendMessage(str(config['chat_id']), push_str)
    logger.info(push_str)


def handle(msg):
    if msg['text'] == '/list':
        push_list()
    elif msg['text'] == '/data':
        content_list = query_push_content({
            'host': config['host'],
            'user': config['user'],
            'password': config['password'],
            'port': int(config['port']),
            'db': config['db'],
            'charset': 'utf8'
        })
        push_str = '\n\n'.join(map(str, content_list))
        bot.sendMessage(str(config['chat_id']), push_str)


if __name__ == '__main__':
    config = read_config('./config.ini')
    if config['env'] in ["dev"]:
        telepot.api.set_proxy(config['proxy'])
    bot = telepot.Bot(config['token'])
    MessageLoop(bot, handle).run_as_thread()
    push_list()
    if config['env'] in ["prod"]:
        logger.info('Listening ...')
        schedule.every().day.at(config['timed_task']).do(push_list)
        while True:
            schedule.run_pending()
            time.sleep(1)
