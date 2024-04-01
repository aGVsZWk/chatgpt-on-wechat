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
from multiprocessing.connection import Listener
import traceback

authkey = b'peekaboo'


def recv_file_name():
    server = Listener(('', 25000), authkey=authkey)
    client = server.accept()
    while True:
        try:
            try:
                while True:
                    msg = client.recv()
                    client.close()
                    server.close()
                    return msg
            except EOFError:
                logger.error("Connection closed")
        except Exception as e:
            logger.error(e)


def send_start_command():
    from multiprocessing.connection import Client
    c = Client(('', 25001), authkey=authkey)
    c.send('start')
    c.close()


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
        threading.Thread(target=self.recv_and_send_pic, args=(e_context,)).start()


    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()
        logger.debug("[cat] on_handle_context. content: %s" % content)

        if "抓猫" in content:
            # os.system("cd plugins/cat/ && /usr/bin/python crawl_cat.py")
            self.check_task(e_context)
            send_start_command()
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = "抓猫程序已启动"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def recv_and_send_pic(self, e_context: EventContext):
        curdir = os.path.dirname(__file__)
        f = recv_file_name()
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

    def get_help_text(self, **kwargs):
        help_text = "抓猫"
        return help_text
