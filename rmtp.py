#random movement take picture
#本体と外部PCとの共通コード

from akari_client import AkariClient
import depthai as dai
import cv2
import random
import time
import threading
from face import FACE
import numpy as np


class RMTP():

    def __init__(self, acc=None) -> None:
        # OAK-Dのパイプライン作成
        self.pipeline = dai.Pipeline()
        face = FACE(self.pipeline)

        # ソースとアウトプットの設定
        # --- camera settings ---
        cam_rgb = self.pipeline.createColorCamera()
        self.WIDTH = 300
        self.HEIGHT = 300
        cam_rgb.setPreviewSize(self.WIDTH, self.HEIGHT)
        cam_rgb.setInterleaved(False)
        # camera output
        xout_rgb = self.pipeline.createXLinkOut()
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)

        # --- NN settings ---
        cam_rgb.preview.link(face.get_face_nn().input)
        # NN output
        xout_nn = self.pipeline.createXLinkOut()
        xout_nn.setStreamName("nn")
        face.get_face_nn().out.link(xout_nn.input)

        # OAK-Dがあるかどうかを確認(本体や外部PCとOAK-Dを接続すればTrueになるはず)
        self.oak_available = len(dai.Device.getAllConnectedDevices()) > 0

        self.device=None
        if self.oak_available:
            self.device=dai.Device(self.pipeline)
            self.video=self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            self.nn_output = self.device.getOutputQueue(name="nn", maxSize=4, blocking=False)

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
        
        # 映像取得・表示
        frame = self.video.get().getCvFrame()
        # cv2.imwrite("captured_face.jpg", frame) # 画像の保存
        cv2.imshow("debug picture", frame)
        cv2.waitKey(0)
        # ジュピターでの表示
        # _, jpg = cv2.imencode('.jpeg', frame)
        # img = Image(data = jpg.tobytes())
        # display_handle.update(img)
        
        # NN出力取得・顔検出
        # -- 推論データの取得 --
        in_nn = self.nn_output.get()
        conf = np.array(in_nn.getLayerFp16("conf")).reshape((1076, 2))
        # loc = np.array(in_nn.getLayerFp16("loc")).reshape((1076, 14))
        iou = np.array(in_nn.getLayerFp16("iou")).reshape((1076, 1))

        # --- スコア計算 ---
        cls_scores = conf[:, 1] # 顔である確率
        iou_scores = np.clip(iou[:, 0], 0.0, 1.0) # 信頼度 飛び値は補正
        scores = np.sqrt(cls_scores * iou_scores)

        # --- 顔の有無を判定 ---
        face_found = np.any(scores > 0.6)
        print("顔あり" if face_found else "顔なし") # 平方根を取ることで，過度に小さくなるのを防ぐ


        """
        上記は簡易版
        画像を操作する際にバウンディングボックスを用いているが，
        下記は，そのボックスのサイズ等を複数準備することで，
        様々なサイズの顔などに柔軟い，かつ精度高く判定を行うイメージ
        """
        # prior_box.pyを使用する場合　(参考:face_detection)
        # pb = PriorBox(
        #     input_shape=(self.WIDTH, self.HEIGHT),
        #     output_shape=(frame.shape[1], frame.shape[0])
        # )

    def close(self):
        if self.device:
            self.device.close()
