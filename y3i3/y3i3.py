# -*- coding: utf-8 -*-
# @Time        : 2023/12/23
# @Author      : helei
# @File        : luke.py
# @Description :
import random
import traceback
from datetime import datetime
import redis
from bs4 import BeautifulSoup
import time
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bridge.reply import Reply, ReplyType
from channel.wechat.wechat_message import *
from y3i3 import y3i3_helper


# host = "192.168.0.103"
# port = 6379
# db = 0
# password = "1234"
#
# connection = redis.Redis(host=host, port=port, db=db, password=password)
#
# result = connection.keys()
# print(result)

# from channel.wechat.wechat_channel import WechatChannel


# WechatChannel().send(reply, content)

def get_caihongpi_info():
    """
    彩虹屁生成器
    :return: str,彩虹屁
    """
    try:
        resp = requests.get('https://api.shadiao.pro/chp')
        if resp.status_code == 200:
            return resp.json()["data"]["text"]
        return "彩虹屁获取失败"
    except Exception:
        traceback.print_exc()
        return "彩虹屁获取失败"


def get_hitokoto_info(c=None):
    """
    从『一言』获取信息。(官网：https://hitokoto.cn/)
    :return: str,一言。
    """
    try:
        if c:
            url = "https://v1.hitokoto.cn?c=%s" % c
        else:
            url = "https://v1.hitokoto.cn"
        resp = requests.get(url, params={'encode': 'text'})
        if resp.status_code == 200:
            return resp.text
        return "一言获取失败"
    except Exception:
        traceback.print_exc()
        return "一言获取失败"


def get_yiyan_word():
    '''
    获取一段暖话
    :return:
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }
    user_url = 'http://www.ainicr.cn/qh/t83.html'
    resp = requests.get(user_url, headers=headers)
    soup_texts = BeautifulSoup(resp.text, 'lxml')
    # 『one -个』 中的每日一句
    num = random.randint(0, 30)
    every_msg = soup_texts.find_all('div', class_='pbllists')[0].find_all('p')[num].text
    return every_msg



def get_air_quality(city):
    """
    通过城市名获取空气质量
    官网：http://aqicn.org/here/
    token 申请地址：http://aqicn.org/data-platform/token/#/
    :param city: 城市
    :return:
    """
    AQICN_TOKEN = '6382db85ef321ae81f316486de0b5b8aa6c84f62'
    AIR_STATUS_DICT = {
        50: '优',
        100: '良',
        150: '轻度污染',
        200: '中度污染',
        300: '重度污染',
        3000: '严重污染'
    }
    try:
        url = 'http://api.waqi.info/feed/{city}/?token={token}'.format(city=city, token=AQICN_TOKEN)
        resp = requests.get(url)
        if resp.status_code == 200:
            # print(resp.text)
            content_dict = resp.json()
            if content_dict.get('status') == 'ok':
                data_dict = content_dict['data']
                aqi = data_dict['aqi']
                air_status = '严重污染'
                for key in sorted(AIR_STATUS_DICT):
                    if key >= aqi:
                        air_status = AIR_STATUS_DICT[key]
                        break
                aqi_info = 'PM2.5指数: {aqi}\n空气质量: {air_status}'.format(city=city, aqi=aqi, air_status=air_status)
                # print(aqi_info)
                return aqi_info
            else:
                return None
    except Exception as exception:
        traceback.print_exc()
        return None
    return None


def get_weather(city_name="北京", name="臭茹茹"):
    city_code_config = {
        "北京": "101010200",
        "石家庄": "101090101",
        "运城": "101100801"
    }
    city_code = city_code_config[city_name]
    url = "http://t.weather.sojson.com/api/weather/city/" + city_code
    response = requests.get(url)

    if not (response.status_code == 200 and response.json()['status'] == 200):
        today_msg = "获取天气失败"
        return today_msg
    weather = response.json()
    #位置
    location = weather['cityInfo']['parent']+weather['cityInfo']['city']
    #当前时间
    today_time = datetime.now().strftime('%Y{y}%m{m}%d{d}').format(y='年',m='月',d='日')
    # 今日天气
    today_weather = weather.get('data').get('forecast')[0]
    # print(today_weather)
    # 今日天气注意事项
    notice = today_weather.get('notice')
    # 温度
    high = today_weather.get('high')
    high_c = high[high.find(' ') + 1:]
    low = today_weather.get('low')
    low_c = low[low.find(' ') + 1:]
    temperature = f"温度: {low_c} ~ {high_c}"
    # 风
    fx = today_weather.get('fx')
    fl = today_weather.get('fl')
    wind = f"{fx}: {fl}"
    # 空气指数
    aqi = get_air_quality(city_name)
    # today_msg = f'{today_time}。\n{location} {today_time}天气状况: \n{nowtemperature}, {nowshidu}, {nowpm25}\n{notice}\n{temperature}\n{wind}\n{aqi}\n'
    today_msg = f'{today_time}\n{location} 天气状况: \n{wind}\n{temperature}\n{aqi}\n{name}, {notice}'
    return today_msg



def get_constellation_name(date):
    '''
    通过日期来返回星座名，或者檢查星座名是否正確。
    :param date: 指定日期或者星座名
    :return:rtype str
    '''
    constellation_name_list = (
        "摩羯座", "水瓶座", "双鱼座", "白羊座",
        "金牛座", "双子座", "巨蟹座", "狮子座",
        "处女座", "天秤座", "天蝎座", "射手座")
    birthday_compile = re.compile(r'[\-\s]?(0?[1-9]|1[012])[\-\/\s]+(0?[1-9]|[12][0-9]|3[01])$')
    constellation_date_dict = {
        (1, 20): '摩羯座',
        (2, 19): '水瓶座',
        (3, 21): '双鱼座',
        (4, 21): '白羊座',
        (5, 21): '金牛座',
        (6, 22): '双子座',
        (7, 23): '巨蟹座',
        (8, 23): '狮子座',
        (9, 23): '处女座',
        (10, 23): '天秤座',
        (11, 23): '天蝎座',
        (12, 23): '射手座',
        (12, 32): '摩羯座',
    }
    if not date:
        return
    date = date.strip()
    if date in constellation_name_list:
        return date

    times = birthday_compile.findall(date)
    if times:
        month, day = int(times[0][0]), int(times[0][1])
        for k, v in constellation_date_dict.items():
            if k > (month, day):
                return v
    return None


def get_xzw_horoscope(name, is_tomorrow=False):
    '''
    获取星座屋(https://www.xzw.com)的星座运势
    :param name: 星座名称
    :return:
    '''
    constellation_dict = {
        "白羊座": "aries",
        "金牛座": "taurus",
        "双子座": "gemini",
        "巨蟹座": "cancer",
        "狮子座": "leo",
        "处女座": "virgo",
        "天秤座": "libra",
        "天蝎座": "scorpio",
        "射手座": "sagittarius",
        "摩羯座": "capricorn",
        "水瓶座": "aquarius",
        "双鱼座": "pisces",
    }
    xzw_base_url_tomorrow = "https://www.xzw.com/fortune/{}/1.html"
    xzw_base_url_today = "https://www.xzw.com/fortune/{}"
    spider_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
                      'WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
    }
    try:
        const_code = constellation_dict[name]

        req_url = xzw_base_url_tomorrow.format(const_code) if is_tomorrow \
            else xzw_base_url_today.format(const_code)

        resp = requests.get(req_url, headers=spider_headers)
        if resp.status_code == 200:
            html = resp.text
            lucky_num = re.findall(r'<label>幸运数字：</label>(.*?)</li>', html)[0]
            lucky_color = re.findall(r'<label>幸运颜色：</label>(.*?)</li>', html)[0]
            detail_horoscope = re.findall(r'<p><strong class="p1">.*?</strong><span>(.*?)<small>.*?</small></span></p>', html)[0]
            if is_tomorrow:
                detail_horoscope = detail_horoscope.replace('今天', '明天')

            return_text = '{name}{_date}运势\n【幸运颜色】{color}\n【幸运数字】{num}\n【综合运势】{horoscope}'.format(
                _date='明日' if is_tomorrow else '今日',
                name=name,
                color=lucky_color,
                num=lucky_num,
                horoscope=detail_horoscope
            )
            return return_text
    except Exception as exception:
        print(str(exception))


def get_constellation_info(birthday_str, is_tomorrow=False):
    """
    获取星座运势
    :param birthday_str:  "10-12" 或  "1980-01-08" 或 星座名
    :return:
    """
    if not birthday_str:
        return
    const_name = get_constellation_name(birthday_str)
    if not const_name:
        return "星座名填写错误"
    return get_xzw_horoscope(const_name, is_tomorrow)


def get_sweet_words():
    return "                  ----来自最爱你的磊磊"


def get_patpat_reply():
    """获取微信拍一拍的回复信息"""

    reply = Reply(ReplyType.TEXT, get_hitokoto_info(c=random.choice(["a", "b", "c", "d", "e", "f", "g", "h", "j", "k"])))
    return reply


def send_morning_msg():
    """
    发送天气信息
    """
    f = random.choice([get_caihongpi_info, get_hitokoto_info, get_yiyan_word])
    text = get_weather() + "\n\n" + f() + "\n" + get_sweet_words()
    user = y3i3_helper.get_friend(remark_name="臭茹茹")
    itchat.send(text, toUserName=user.UserName)

    text = get_weather("石家庄", "小伙砸")
    user = y3i3_helper.get_friend(remark_name="绿城凤鸣朝阳 朱爱裕")
    itchat.send(text, toUserName=user.UserName)

def send_constellation_today():
    """
    发送今日星座信息
    """
    text = get_constellation_info("白羊座")
    user = y3i3_helper.get_friend(remark_name="臭茹茹")
    itchat.send(text, toUserName=user.UserName)

    text = get_constellation_info("双鱼座")
    user = y3i3_helper.get_friend(remark_name="绿城凤鸣朝阳 朱爱裕")
    itchat.send(text, toUserName=user.UserName)

def send_constellation_tomorrow():
    """
    发送明日星座信息
    """
    text = get_constellation_info("白羊座", True)
    user = y3i3_helper.get_friend(remark_name="臭茹茹")
    itchat.send(text, toUserName=user.UserName)


def send_excuse_msg():
    user = y3i3_helper.get_friend(remark_name="臭茹茹")
    t = int(random.random() * 100)
    if t < 20:
        text = "臭茹茹，你今天拉屎了没"
    elif 20 <= t < 40:
        text = "臭茹茹，你今天穿秋裤了没"
    elif 40 <= t < 60:
        text = get_hitokoto_info(c=random.choice(["a", "b", "c", "d", "e", "f", "g", "h", "j", "k"]))
    elif 60 <= t < 80:
        text = get_hitokoto_info(c="k")
    elif 80 <= t:
        text = get_hitokoto_info(c="j")
    else:
        text = ""
    itchat.send(text, toUserName=user.UserName)

def send_eat_msg():
    user = y3i3_helper.get_friend(remark_name="臭茹茹")
    itchat.send("臭茹茹，你晚饭吃的啥?", toUserName=user.UserName)


def init_scheduler():
    # 定时任务
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_morning_msg, "cron", [], hour=7, minute=30, misfire_grace_time=600,
                      jitter=300)
    scheduler.add_job(send_constellation_today, "cron", [], hour=8, misfire_grace_time=600, jitter=300)
    scheduler.add_job(send_constellation_tomorrow, "cron", [], hour=19, misfire_grace_time=600, jitter=300)
    scheduler.add_job(send_excuse_msg, "cron", [], hour=8, minute=random.randint(0, 59), misfire_grace_time=600,
                      jitter=random.randint(100, 900))
    scheduler.add_job(send_excuse_msg, "cron", [], hour=10, minute=random.randint(0, 59), misfire_grace_time=600,
                      jitter=random.randint(100, 900))
    scheduler.add_job(send_excuse_msg, "cron", [], hour=11, minute=random.randint(0, 59), misfire_grace_time=600,
                      jitter=random.randint(100, 900))
    scheduler.add_job(send_excuse_msg, "cron", [], hour=14, minute=random.randint(0, 59), misfire_grace_time=600,
                      jitter=random.randint(100, 900))
    scheduler.add_job(send_excuse_msg, "cron", [], hour=16, minute=random.randint(0, 59), misfire_grace_time=600,
                      jitter=random.randint(100, 900))
    scheduler.add_job(send_excuse_msg, "cron", [], hour=17, minute=random.randint(0, 59), misfire_grace_time=600,
                      jitter=random.randint(100, 900))
    scheduler.add_job(send_eat_msg, "cron", [], hour=21, minute=24, misfire_grace_time=600,
                      jitter=random.randint(10, 30))
    scheduler.start()


if __name__ == '__main__':
    # "6点半"
    # print(get_weather("北京"))
    # print(get_weather("石家庄", "小伙砸"))
    print(get_weather("运城", "小伙砸"))
    # print()
    # print(get_yiyan_word())
    # print(get_sweet_words())
    #
    # # "7点"
    # print(get_constellation_info("白羊座"))

    # 18点
    # print(get_constellation_info("白羊座", True))
    # init_scheduler()
