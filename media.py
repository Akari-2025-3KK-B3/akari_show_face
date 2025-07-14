#random movement take picture
#本体と外部PCとの共通コード

from akari_client import AkariClient
from akari_client.color import Color, Colors
from akari_client.position import Positions
import depthai as dai
import cv2
import random
import time
import mediapipe as mp


class Media():

    def __init__(self, acc=None) -> None:
        #回数カウント変数
        self.suc_cnt=0
        #hell mode flag
        self.hell_flag=False
        #難易度設定のフラッグ
        self.level_flag=False
         #--mediapipe settings--
        self.mp_pose=mp.solutions.pose
        mp_face=mp.solutions.face_detection
        self.pose=self.mp_pose.Pose()
        self.face_detection=mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)


        # OAK-Dのパイプライン作成
        self.pipeline = dai.Pipeline()

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

        #外部PCの場合のAkariClientのインスタンス化
        if acc != None:
            self.akari = AkariClient(acc)
        else:#本体からのインスタンス化
            self.akari = AkariClient()
            
        
        #self.m5の設定
        self.m5=self.akari.m5stack
        self.joints = self.akari.joints
        self.joints.set_servo_enabled(pan=True, tilt=True)

        self.m5.set_display_text(text="難易度を設定してください",size=2, pos_x=Positions.CENTER, pos_y=Positions.CENTER)
        self.m5.set_display_text(text="弱", pos_x=Positions.LEFT, pos_y=Positions.BOTTOM, refresh=False)
        self.m5.set_display_text(text="中", pos_x=Positions.CENTER, pos_y=Positions.BOTTOM, refresh=False)
        self.m5.set_display_text(text="強", pos_x=Positions.RIGHT, pos_y=Positions.BOTTOM, refresh=False)
        #速度の設定
        for i in range(9):
            self.m5.set_display_text(str(len(range(9))-i), pos_x=Positions.RIGHT, pos_y=Positions.TOP, refresh=False)

            data=self.m5.get()
            if data["button_a"]:
                self.level_flag=True
                self.joints.set_joint_velocities(pan=4, tilt=4)
                self.m5.set_display_text(text="弱", pos_x=Positions.CENTER, pos_y=Positions.CENTER)
                time.sleep(1)
                break
            elif data["button_b"]:
                self.level_flag=True
                self.joints.set_joint_velocities(pan=6, tilt=6)
                self.m5.set_display_text(text="中", pos_x=Positions.CENTER, pos_y=Positions.CENTER)
                time.sleep(1)
                break
            elif data["button_c"]:
                self.level_flag=True
                self.joints.set_joint_velocities(pan=8, tilt=8)
                self.m5.set_display_text(text="強", pos_x=Positions.CENTER, pos_y=Positions.CENTER)
                time.sleep(1)
                break
                
            time.sleep(1)

        if self.level_flag == False:
            self.m5.set_display_text(text="Hell", pos_x=Positions.CENTER, pos_y=Positions.CENTER)
            self.hell_flag=True
            time.sleep(1)


        for i in range(3):
            self.m5.set_display_text(str(len(range(3))-i), size=10)
            time.sleep(1)
            if i==2:
                self.m5.set_display_text("")
        
    
    #ランダムに首を動かす
    def akari_random_move(self)->None:
        #ランダムなループ
        loop_num = int(random.uniform(1,10))
        for i in range(loop_num):

            #hellの場合速度をランダムにする
            if self.hell_flag:
                ran=int(random.uniform(1,10))
                self.joints.set_joint_velocities(pan=ran, tilt=ran)

            rpan = random.uniform(-1,1)
            rtilt = random.uniform(-0.5,0.5)
            self.joints.move_joint_positions(pan=rpan, tilt=rtilt)
            time.sleep(0.7)
        time.sleep(0.5)
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
            self.suc_cnt+=1
            self.m5.set_display_text(str(self.suc_cnt), size=10, pos_x=Positions.CENTER, pos_y=Positions.CENTER)
            print("顔あり")
            for detection in result_face.detections:
                bbox=detection.location_data.relative_bounding_box
                h,w,_=frame.shape
                x,y,width,height=int(bbox.xmin*w), int(bbox.ymin*h), int(bbox.width*w), int(bbox.height*h)
                cv2.rectangle(frame, (x,y), (x+width, y+height), (0, 255, 0), 2)
            self.akari_random_move()
        
        cv2.imshow("debug picture", frame)
        cv2.waitKey(0)


    def close(self):
        if self.device:
            self.device.close()
