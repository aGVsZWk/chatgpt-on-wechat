# -*- coding: utf-8 -*-
# @Time        : 2024/3/9
# @Author      : helei
# @File        : cat.py
# @Description :
import cv2
import numpy as np
# from picamera2 import Picamera2, Preview
import time
from PIL import Image
import json
import uuid
# from y3i3.helper import y3i3_helper
import io
import os
# os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from ultralytics import YOLO


model = YOLO(os.path.join(os.path.dirname(__file__), './yolov8n.pt'))
print("aaaa")


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
        if succ:
            return array_frame
        else:
            raise Exception("cv 读取摄像头错误")

    def stop(self):
        self.cap.release()
        cv2.destroyAllWindows()


def cat_monitor():
    camera = CameraCV2()
    try:
        while camera.is_open:
            array = camera.photo_for_array_frame()
            results = model(array)
            # 在帧上可视化结果
            for result in results:
                annotated_frame = result.plot()
                items = json.loads(result.tojson())
                for item in items:
                    if item["name"] == "cat":
                        # 显示带注释的帧
                        # cv2.imshow("YOLOv8推理", annotated_frame)
                        # img = Image.fromarray(np.uint8(annotated_frame / imgs))
                        name = str(uuid.uuid4())
                        img = Image.fromarray(np.uint8(annotated_frame))
                        # img.save(name + ".tif")
                        cat_notify(img)
    except Exception as e:
        logger.warning("Exception when counting tokens precisely for prompt: {}".format(str(e)))
    finally:
        camera.stop()


def cat_notify(img):
    user = y3i3_helper.get_friend(remark_name="臭茹茹")
    image_storage = io.BytesIO()
    img.save(image_storage, format="TIF")
    img_bytes = image_storage.getvalue()
    print(img_bytes)
    # itchat.send_image(img_bytes, toUserName=user.UserName)


if __name__ == '__main__':
    cat_monitor()