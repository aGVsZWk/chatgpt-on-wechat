# -*- coding: utf-8 -*-
# @Time        : 2023/12/24
# @Author      : helei
# @File        : y3i3_helper.py
# @Description :
from channel.wechat.wechat_message import *
FILEHELPER_MARK = ['文件传输助手', 'filehelper']  # 文件传输助手标识
FILEHELPER = 'filehelper'


def set_system_notice(text):
    """
    给文件传输助手发送系统日志。
    :param text:str 日志内容
    """
    if text:
        text = '系统通知：' + text
        itchat.send(text, toUserName=FILEHELPER)


def get_group(group_name, update=False):
    """
    根据群组名获取群组数据
    :param group_name:str, 群组名
    :param update: bool 强制更新群组数据
    :return: obj 单个群组信息
    """
    if update: itchat.get_chatrooms(update=True)
    if not group_name: return None
    groups = itchat.search_chatrooms(name=group_name)
    if not groups: return None
    return groups[0]


def get_friend(wechat_name=None, remark_name=None, update=False):
    """
    根据用户名获取用户数据
    :param wechat_name: str 用户名
    :param wechat_name: str 备注
    :param update: bool 强制更新用户数据
    :return: obj 单个好友信息
    """
    if update:
        itchat.get_friends(update=True)
    if not wechat_name and not remark_name:
        return None
    friends = itchat.search_friends(name=wechat_name, remark_name=remark_name)
    if not friends:
        return None
    return friends[0]


def get_mps(mp_name, update=False):
    """
    根据公众号的名称获取用户数据
    :param mp_name: str 用户名
    :param update: bool 强制更新用户数据
    :return: obj 单个公众号信息
    """
    if update: itchat.get_mps(update=True)
    if not mp_name: return None
    mps = itchat.search_mps(name=mp_name)
    if not mps: return None
    # mpuuid = mps[0]['UserName'] 公众号的uuid
    return mps[0]