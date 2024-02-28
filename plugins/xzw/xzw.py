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
import re

@plugins.register(
    name="Xzw",
    desire_priority=900,
    desc="星座插件",
    version="0.1",
    author="luke",
)
class XZW(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.constellation_dict = {
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
                "白羊": "aries",
                "金牛": "taurus",
                "双子": "gemini",
                "巨蟹": "cancer",
                "狮子": "leo",
                "处女": "virgo",
                "天秤": "libra",
                "天蝎": "scorpio",
                "射手": "sagittarius",
                "摩羯": "capricorn",
                "水瓶": "aquarius",
                "双鱼": "pisces",
            }
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[xzw] inited.")
        except Exception as e:
            logger.warn(
                "[xzw] init failed")
            raise e

    def get_xz_name(self, seg_list):
        for seg in seg_list:
            if seg.strip() in self.constellation_dict:
                return seg
            else:
                return None

    def check_is_tomorrow(self, seg_list):
        if "今" in "".join(seg_list):
            return False
        elif "明" in "".join(seg_list):
            return True
        else:
            return False

    def get_xzw_horoscope(self, name, is_tomorrow=False):
        '''
        获取星座屋(https://www.xzw.com)的星座运势
        :param name: 星座名称
        :return:
        '''

        xzw_base_url_tomorrow = "https://www.xzw.com/fortune/{}/1.html"
        xzw_base_url_today = "https://www.xzw.com/fortune/{}"
        spider_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
                          'WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
        }
        try:
            const_code = self.constellation_dict[name]
            req_url = xzw_base_url_tomorrow.format(const_code) if is_tomorrow \
                else xzw_base_url_today.format(const_code)

            resp = requests.get(req_url, headers=spider_headers)
            if resp.status_code == 200:
                html = resp.text
                lucky_num = re.findall(r'<label>幸运数字：</label>(.*?)</li>', html)[0]
                lucky_color = re.findall(r'<label>幸运颜色：</label>(.*?)</li>', html)[0]
                detail_horoscope = \
                re.findall(r'<p><strong class="p1">.*?</strong><span>(.*?)<small>.*?</small></span></p>', html)[0]
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

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        content = e_context["context"].content.strip()
        logger.debug("[xzw] on_handle_context. content: %s" % content)
        if any([key in content for key in self.constellation_dict.keys()]) or "星座" in content:
            logger.info(f"[xzw] 匹配到星座【{content}】")
            seg_list = list(jieba.cut(content, use_paddle=True))  # 使用paddle模式
            is_tomorrow = self.check_is_tomorrow(seg_list)
            name = self.get_xz_name(seg_list)
            if name is not None:
                reply_text = self.get_xzw_horoscope(name, is_tomorrow)
            else:
                reply_text = "星座输入有误"
            # 否则认为是普通文本
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = reply_text

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "星座插件"
        return help_text
