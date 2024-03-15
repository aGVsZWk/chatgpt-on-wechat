# -*- coding: utf-8 -*-
# @Author  : HeLei
# @Time    : 2024/2/5 19:07
# @File    : weather.py
# encoding:utf-8

import json
import os
import requests
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
import jieba
from datetime import datetime, timedelta
from plugins import *


@plugins.register(
    name="Weather",
    desire_priority=900,
    desc="天气插件",
    version="0.1",
    author="luke",
)
class Weather(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            curdir = os.path.dirname(__file__)
            self.city_data = json.load(open(os.path.join(curdir, "citycode.json")))
            logger.info("[weather] inited.")
        except Exception as e:
            logger.warn(
                "[weather] init failed")
            raise e

    def find_city_code(self, seg_list):
        logger.info(seg_list)
        for seg in seg_list:
            for item in self.city_data:
                if seg.strip() in item["city_name"] or item["city_name"] in seg:
                    return item["city_code"]
        return "101090101"

    def find_day_offset(self, seg_list):
        t = "".join(seg_list)
        if "今天" in t:
            return 1
        elif "明天" in t:
            return 2
        elif "三天" in t or "3天" in t:
            return 3
        elif "一周" in "".join(t) or "一星期" in "".join(t) or "七天" in t or "7天" in t:
            return 7
        else:
            return 1

    def get_weather(self, city_code, day_offset):
        url = "http://t.weather.sojson.com/api/weather/city/" + city_code
        response = requests.get(url)

        if not (response.status_code == 200 and response.json()['status'] == 200):
            today_msg = "获取天气失败"
            return today_msg
        weather = response.json()
        # 位置
        location = weather['cityInfo']['parent'] + weather['cityInfo']['city']
        # 当前时间
        today_time = datetime.now().strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
        # 今日天气
        weathers = weather.get('data').get('forecast')[:day_offset]
        msg = ""
        for offset, today_weather in enumerate(weathers):
            day_time = (datetime.now() + timedelta(days=offset)).strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
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
            # today_msg = f'{today_time}。\n{location} {today_time}天气状况: \n{nowtemperature}, {nowshidu}, {nowpm25}\n{notice}\n{temperature}\n{wind}\n{aqi}\n'
            msg += f'{day_time}\n{location} 天气状况\n{wind}\n{temperature}\n\n'
        return msg

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()
        logger.debug("[weather] on_handle_context. content: %s" % content)
        if "天气" in content:
            logger.info(f"[weather] 匹配到天气【{content}】")
            seg_list = list(jieba.cut(content, use_paddle=True))  # 使用paddle模式
            city_code = self.find_city_code(seg_list)
            day_offset = self.find_day_offset(seg_list)
            reply_text = self.get_weather(city_code, day_offset)
            # 否则认为是普通文本
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = reply_text

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "天气插件，结巴分词cut出天气"
        return help_text
