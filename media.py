#random movement take picture
#本体と外部PCとの共通コード

from akari_client import AkariClient
import depthai as dai
import cv2
import random
import time
import numpy as np
import mediapipe as mp

class Media():

    def __init__(self, acc=None) -> None:

         #--mediapipe settings--
        self.mp_pose=mp.solutions.pose
        mp_face=mp.solutions.face_detection
        self.pose=self.mp_pose.Pose()
        self.face_detection=mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)


        # OAK-Dのパイプライン作成
        self.pipeline = dai.Pipeline()
        # face = FACE(self.pipeline)

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

        # OAK-Dがあるかどうかを確認(本体や外部PCとOAK-Dを接続すればTrueになるはず)
        self.oak_available = len(dai.Device.getAllConnectedDevices()) > 0

        self.device=None
        if self.oak_available:
            self.device=dai.Device(self.pipeline)
            self.video=self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            # self.nn_output = self.device.getOutputQueue(name="nn", maxSize=4, blocking=False)

        #外部PCの場合のAkariClientのインスタンス化
        if acc != None:
            self.akari = AkariClient(acc)
            self.joints = self.akari.joints
            self.joints.set_joint_velocities(pan=3, tilt=3)
            self.joints.set_servo_enabled(pan=True, tilt=True)
        else:#本体からのインスタンス化
            self.akari = AkariClient()
            self.joints = self.akari.joints
            self.joints.set_joint_velocities(pan=8, tilt=8)
            self.joints.set_servo_enabled(pan=True, tilt=True)
            
        
    
    #ランダムに首を動かす
    def akari_random_move(self)->None:
        #ランダムなループ
        loop_num = int(random.uniform(1,10))
        # loop_num = 0
        for i in range(loop_num):
            rpan = random.uniform(-1,1)
            rtilt = random.uniform(-0.5,0.5)
            self.joints.move_joint_positions(pan=rpan, tilt=rtilt)
            time.sleep(0.7)
        # time.sleep(0.5)
        self.akari_take_picture()



    #画像取得
    def akari_take_picture(self)->None:
        if not self.oak_available or self.device is None:
            print("⚠️このPCにOAK-Dが接続されていないため、撮影はスキップします。")
            return
        
        # 映像取得・表示
        frame = self.video.get().getCvFrame()
        rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result_pose=self.pose.process(rgb_frame)
        result_face=self.face_detection.process(rgb_frame)

        #ランドマーク描画
        if result_pose.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, result_pose.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )

        #顔検出描画
        if result_face.detections:
            print("顔あり")
            for detection in result_face.detections:
                bbox=detection.location_data.relative_bounding_box
                h,w,_=frame.shape
                x,y,width,height=int(bbox.xmin*w), int(bbox.ymin*h), int(bbox.width*w), int(bbox.height*h)
                cv2.rectangle(frame, (x,y), (x+width, y+height), (0, 255, 0), 2)

        cv2.imshow("debug picture", frame)
        cv2.waitKey(0)
       
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
