# -*- coding: utf-8 -*-
# @Time        : 2024/3/17
# @Author      : helei
# @File        : cat.py
# @Description :
# encoding:utf-8
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import *
import threading
import time


@plugins.register(
    name="Cat",
    desire_priority=900,
    hidden=True,
    desc="抓猫插件",
    version="0.1",
    author="luke",
)
class Cat(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[cat] init success")
        except Exception as e:
            logger.warn(
                "[cat] init failed")
            raise e

    def check_task_sync(self, e_context: EventContext):
        curdir = os.path.dirname(__file__)
        f = "cat.jpg"
        cat_path = os.path.join(curdir, f)
        while True:
            if os.path.exists(cat_path):
                reply = Reply()
                reply.type = ReplyType.IMAGE
                reply.content = open(cat_path, "rb")
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                channel = e_context["channel"]
                self._send(channel, reply, e_context["context"])
                time.sleep(5)
                os.remove(cat_path)
                break

    @staticmethod
    def _send(channel, reply: Reply, context, retry_cnt=0):
        try:
            channel.send(reply, context)
        except Exception as e:
            logger.error("[WX] sendMsg error: {}".format(str(e)))
            if isinstance(e, NotImplementedError):
                return
            logger.exception(e)
            if retry_cnt < 2:
                time.sleep(3 + 3 * retry_cnt)
                channel.send(reply, context, retry_cnt + 1)

    def check_task(self, e_context):
        threading.Thread(target=self.check_task_sync, args=(e_context,)).start()

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()
        logger.debug("[cat] on_handle_context. content: %s" % content)

        if "抓猫" in content:
            os.system("cd plugins/cat/ && /usr/bin/python crawl_cat.py")
            self.check_task(e_context)
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = "抓猫程序已启动"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "抓猫"
        return help_text
