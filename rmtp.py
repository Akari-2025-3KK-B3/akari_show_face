#random movement take picture
#本体と外部PCとの共通コード

from akari_client import AkariClient
import depthai as dai
import cv2
import random
import time
import threading
from face2 import FACE
import numpy as np


class RMTP():

    def __init__(self, acc=None) -> None:
        # OAK-Dのパイプライン作成
        self.pipeline = dai.Pipeline()#⬇︎class
        face = FACE(self.pipeline)
        # ソースとアウトプットの設定
        cam_rgb = self.pipeline.createColorCamera()
        # preview size640x480に指定
        cam_rgb.setPreviewSize(640, 480)
        cam_rgb.setInterleaved(False)#⬇︎face_nn method
        cam_rgb.preview.link(face.face_nn().input)
        # ストリーミング名設定
        xout_rgb = self.pipeline.createXLinkOut()
        xout_rgb.setStreamName("rgb")#⬇︎ 編集
        face.face_nn().out.link(xout_rgb.input)
        # cam_rgb.preview.link(xout_rgb.input)
        # OAK-Dがあるかどうかを確認(本体や外部PCとOAK-Dを接続すればTrueになるはず)
        self.oak_available = len(dai.Device.getAllConnectedDevices()) > 0

        self.device=None
        if self.oak_available:
            self.device=dai.Device(self.pipeline)
            self.video=self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        #外部PCの場合のAkariClientのインスタンス化
        if acc != None:
            self.akari = AkariClient(acc)
            self.joints = self.akari.joints
            self.joints.set_joint_velocities(pan=6, tilt=6)
            self.joints.set_servo_enabled(pan=True, tilt=True)
        else:#本体からのインスタンス化
            self.akari = AkariClient()
            self.joints = self.akari.joints
            self.joints.set_joint_velocities(pan=6, tilt=6)
            self.joints.set_servo_enabled(pan=True, tilt=True)
            
        
    
    #ランダムに首を動かす
    def akari_random_move(self)->None:
        #ランダムなループ
        loop_num = int(random.uniform(1,10))
        for i in range(loop_num):
            rpan = random.uniform(-1,1)
            rtilt = random.uniform(-0.5,0.5)
            self.joints.move_joint_positions(pan=rpan, tilt=rtilt)
            time.sleep(0.7)
        self.akari_take_picture()
            
    #画像取得
    def akari_take_picture(self)->None:
        if not self.oak_available or self.device is None:
            print("⚠️このPCにOAK-Dが接続されていないため、撮影はスキップします。")
            return
        
        in_nn = self.video.get()
        conf = np.array(in_nn.getLayerFp16("conf")).reshape((1076, 2))
        # 顔クラス（index=1）の信頼度が0.6以上のものが1つでもあれば True
        face_found = np.any(conf[:, 1] > 0.6)
        print(bool(face_found))

        frame = self.video.get().getCvFrame()
        # _, jpg = cv2.imencode('.jpeg', frame)
        # img = Image(data=jpg.tobytes())
        # display_handle.update(img)
        cv2.imshow("debug picture", frame)
        cv2.waitKey(0)

    def close(self):
        if self.device:
            self.device.close()
