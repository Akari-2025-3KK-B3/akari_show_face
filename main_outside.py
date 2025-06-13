#!/usr/bin/env python
# -*- coding: utf-8 -*-

#外部PCからの実行コード

import time

from akari_client import AkariClient
from akari_client.config import (
   AkariClientConfig,
   JointManagerGrpcConfig,
   M5StackGrpcConfig,
)

from rmtp import RMTP

def main() -> None:
   """
   メイン関数
   """
   # AKARI本体のIPアドレスを指定する。
   # 実際のAKARIのIPアドレスに合わせて変更すること。
   akari_ip = "172.31.14.11"#ドロピク
   # portは初期設定のままであれば51001固定
   akari_port = "51001"
   akari_endpoint = f"{akari_ip}:{akari_port}"

   joint_config: JointManagerGrpcConfig = JointManagerGrpcConfig(
      type="grpc", endpoint=akari_endpoint
   )
   m5_config: M5StackGrpcConfig = M5StackGrpcConfig(
      type="grpc", endpoint=akari_endpoint
   )
   akari_client_config = AkariClientConfig(
      joint_manager=joint_config, m5stack=m5_config
   )

   RMTP(akari_client_config).akari_random_move()
   # # akari_client_configを引数にしてAkariClientを作成する。
   # akari = AkariClient(akari_client_config)

   # # 処理を記載。下記は例
   # joints = akari.joints
   # # サーボトルクをONする。
   # joints.enable_all_servo()
   # # 初期位置に移動する。
   # joints.move_joint_positions(sync=True, pan=0.3, tilt=0.3)


if __name__ == "__main__":
   main()