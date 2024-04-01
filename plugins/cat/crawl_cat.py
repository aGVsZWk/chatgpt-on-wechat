# -*- coding: utf-8 -*-
# @Time        : 2024/3/9
# @Author      : helei
# @File        : cat.py
# @Description :
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
import time
from PIL import Image
import json
import uuid
# from y3i3.helper import y3i3_helper
import io
import os
# os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from ultralytics import YOLO
# import redis
import pickle
import random
import threading
import multiprocessing
import sys
from loguru import logger
from multiprocessing.connection import Client, Listener


authkey = b'peekaboo'


model = YOLO(os.path.join(os.path.dirname(__file__), '../../y3i3/yolov8n.pt'))


class CameraMixin(object):
    @property
    def is_open(self):
        return

    def init(self):
        pass

    def stop(self):
        pass

    def photo_for_array_frame(self):
        pass


class CameraPicamera(CameraMixin):
    def __init__(self):
        self.picam2 = Picamera2()
        self.init()

    def init(self):
        capture_config = self.picam2.create_still_configuration()
        self.picam2.configure(capture_config)
        self.picam2.stop()
        self.picam2.start()
        with self.picam2.controls as ctrl:
            ctrl.AnalogueGain = 1.0
            ctrl.ExposureTime = 250000
        time.sleep(0.01)


    @property
    def is_open(self):
        return self.picam2.is_open

    def stop(self):
        self.picam2.stop()
        self.picam2.close()

    def photo_for_array_frame(self):
        array_frame = self.picam2.capture_array("main")  # 捕获一帧相机数据，输出为numpy.ndarray类型，与opencv无缝连接
        return array_frame


class CameraCV2(CameraMixin):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.init()

    def init(self):
        pass

    @property
    def is_open(self):
        return self.cap.isOpened()

    def photo_for_array_frame(self):
        succ, array_frame = self.cap.read()
        cv2.waitKey(1)
        if succ:
            return array_frame
        else:
            raise Exception("cv 读取摄像头错误")

    def stop(self):
        cv2.waitKey(1)
        self.cap.release()
        cv2.destroyAllWindows()


def cat_monitor():
    # camera = CameraCV2()
    camera = CameraPicamera()
    c = Client(('localhost', 25000), authkey=authkey)
    i = 0
    try:
        while camera.is_open:
            array = camera.photo_for_array_frame()
            results = model(array)
            # 在帧上可视化结果
            for result in results:
                annotated_frame = result.plot()
                # cv2.imshow("YOLOv8推理", annotated_frame)
                items = json.loads(result.tojson())
                for item in items:
                    print(item["name"])
                    # if item["name"] == "cat":
                    if item["name"] == "cat":
                        i += 1
                        print(i)
                        # 显示带注释的帧
                        if i > 5:
                            print(i)
                            # img = Image.fromarray(np.uint8(annotated_frame / imgs))
                            # name = str(uuid.uuid4())
                            # print(name)
                            # img = Image.fromarray(np.uint8(annotated_frame[:, :, ::-1]))
                            img = Image.fromarray(np.uint8(annotated_frame[:, :, :]))
                            photo_file_name = "cat"
                            file_name = photo_file_name + ".jpg"
                            img.save(file_name)
                            camera.stop()
                            time.sleep(0.5)
                            c.send(file_name)
                            logger.debug("send {} pic success", file_name)
                            i = 0

                            # time.sleep(1)
    except Exception as e:
        logger.warning("Exception when counting tokens precisely for prompt: {}".format(str(e)))
    finally:
        camera.stop()


# def cat_receiver():
#     data = connection.brpop(queue_name)
#     logger.debug(type(data), len(data))
#     payload = pickle.loads(data[1])
#     logger.debug(payload)
#     cat_send(payload["content"])
#
#
# def cat_send(img):
#     # user = y3i3_helper.get_friend(remark_name="臭茹茹")
#     image_storage = io.BytesIO(
#     # img.save(image_storage, mode="TIFF")
#     img_bytes = image_storage.getvalue()
#     logger.debug(img_bytes)
#     # itchat.send_image(img_bytes, toUserName=user.UserName)


def main():
    server = Listener(('', 25001), authkey=authkey)
    while True:
        client = server.accept()
        t = client.recv()
        logger.debug(t)
        if t == "start":
            cat_monitor()


if __name__ == '__main__':
    # cat_monitor()
    print("run start")
    main()
