# encoding:utf-8

import json
import os
import random
import linecache
import requests
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
import textwrap

@plugins.register(
    name="Keyword",
    desire_priority=900,
    hidden=True,
    desc="关键词匹配过滤",
    version="0.1",
    author="fengyege.top",
)
class Keyword(Plugin):
    def __init__(self):
        super().__init__()
        try:
            curdir = os.path.dirname(__file__)
            config_path = os.path.join(curdir, "config.json")
            conf = None
            if not os.path.exists(config_path):
                logger.debug(f"[keyword]不存在配置文件{config_path}")
                conf = {"keyword": {}}
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(conf, f, indent=4)
            else:
                logger.debug(f"[keyword]加载配置文件{config_path}")
                with open(config_path, "r", encoding="utf-8") as f:
                    conf = json.load(f)
            # 加载关键词
            self.keyword = conf["keyword"]

            logger.info("[keyword] {}".format(self.keyword))
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[keyword] inited.")
        except Exception as e:
            logger.warn("[keyword] init failed, ignore or see https://github.com/zhayujie/chatgpt-on-wechat/tree/master/plugins/keyword .")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()
        logger.debug("[keyword] on_handle_context. content: %s" % content)
        if content in self.keyword:
            logger.info(f"[keyword] 匹配到关键字【{content}】")
            reply_text = self.keyword[content]

            # 判断匹配内容的类型
            if (reply_text.startswith("http://") or reply_text.startswith("https://")) and any(reply_text.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".img"]):
            # 如果是以 http:// 或 https:// 开头，且".jpg", ".jpeg", ".png", ".gif", ".img"结尾，则认为是图片 URL。
                reply = Reply()
                reply.type = ReplyType.IMAGE_URL
                reply.content = reply_text
                
            elif (reply_text.startswith("http://") or reply_text.startswith("https://")) and any(reply_text.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".xls", "xlsx",".zip", ".rar"]):
            # 如果是以 http:// 或 https:// 开头，且".pdf", ".doc", ".docx", ".xls", "xlsx",".zip", ".rar"结尾，则下载文件到tmp目录并发送给用户
                file_path = "tmp"
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                file_name = reply_text.split("/")[-1]  # 获取文件名
                file_path = os.path.join(file_path, file_name)
                response = requests.get(reply_text)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                #channel/wechat/wechat_channel.py和channel/wechat_channel.py中缺少ReplyType.FILE类型。
                reply = Reply()
                reply.type = ReplyType.FILE
                reply.content = file_path
            
            elif (reply_text.startswith("http://") or reply_text.startswith("https://")) and any(reply_text.endswith(ext) for ext in [".mp4"]):
            # 如果是以 http:// 或 https:// 开头，且".mp4"结尾，则下载视频到tmp目录并发送给用户
                reply = Reply()
                reply.type = ReplyType.VIDEO_URL
                reply.content = reply_text
                
            else:
            # 否则认为是普通文本
                reply = Reply()
                reply.type = ReplyType.TEXT
                reply.content = reply_text
            
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
        if "介绍对象" in content:
            curdir = os.path.dirname(__file__)
            if "石家庄" in content:
                f = "kl_sjz_crawl.data"
            else:
                f = "kl_crawl.data"
            config_path = os.path.join(curdir, f)
            lines = open(config_path).readlines()
            no = random.randint(0, len(lines)-1)
            item = json.loads(lines[no])
            item["no"] = no
            if item["sign"] == "请设定":
                item["sign"] = "未知"
            item["bitrh_year"] = item["birth_data"].split(".")[0]
            item["id_reg_addr"] = "未知" if item["id_reg_addr"] == "身份证尚未到店核验" else item["id_reg_addr"]
            item["sign"] = "未知" if item["sign"] == "请设定" else item["sign"]
            item["in_come"] = "未知" if item["in_come"] == "请设定" else item["in_come"]
            item["car"] = "保密" if item["car"] == "请设定" else item["car"]
            item["house_hold"] = "保密" if item["house_hold"] == "请设定" else item["house_hold"] + "有房"
            reply_text = """【编号】{no}
【昵称】{user_name}
【性别】{sex}
【出生年份】{bitrh_year}
【户籍】{id_reg_addr}
【星座】{sign}
【身高】{height}
【学历】{edu}
【职业】{vocation}
【是否有房】{house_hold}
【是否有车】{car}
【收入】{in_come}
【自我介绍】{about_me}
            """.format(**item)
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = textwrap.dedent(reply_text)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

        if "查看照片" in content:
            curdir = os.path.dirname(__file__)
            if "石家庄" in content:
                f = "kl_sjz_crawl.data"
            else:
                f = "kl_crawl.data"
            data_path = os.path.join(curdir, f)
            no = content.split(" ")[-1]
            if no.isdigit():
                try:
                    no = int(no)
                    lines = open(data_path).readlines()
                    file_name = json.loads(lines[no])["header_pic"].split("/")[-1]
                    picc_path = os.path.join(curdir, "picc", file_name)
                    reply = Reply()
                    reply.type = ReplyType.IMAGE
                    reply.content = open(picc_path, "rb")
                except Exception as e:
                    logger.debug(e)
                    reply = Reply()
                    reply.type = ReplyType.TEXT
                    reply.content = "编号不正确"
            else:
                reply = Reply()
                reply.type = ReplyType.TEXT
                reply.content = "编号不正确"

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
        if "笑话" in content:
            no = random.randint(0, 66028)
            curdir = os.path.dirname(__file__)
            f = "xiaohua.data"
            data_path = os.path.join(curdir, f)
            data = linecache.getline(data_path, no)
            data = json.loads(data)
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = data["content"]
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑



    def get_help_text(self, **kwargs):
        help_text = "关键词过滤"
        return help_text
