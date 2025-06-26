import argparse
import time
from pathlib import Path

import blobconverter
import cv2
"""
DepthAIとは深度とAIを組み合わせて使うための見込みプラットフォーム
OAK-D, OAK-1に対応 AKARIには"OAK-D-LITE"が搭載
Python, C++対応
"""
import depthai as dai
import numpy as np
from utils.priorbox import PriorBox
from utils.utils import draw

OPENVINO_VERSION = '2021.4'

class FACE():
    def __init__(self, pipeline):
        self.face_nn = pipeline.create(dai.node.NeuralNetwork)
        self.face_nn.setBlobPath(blobconverter.from_zoo(
            name="face-detection-retail-0004",
            version=OPENVINO_VERSION,
            shaves=4
        )) 

    def face_nn(self):
        return self.face_nn


# def face(pipeline, devic, camera) -> bool:
#     face_nn = pipeline.create(dai.node.NeuralNetwork)
#     face_nn.setBlobPath(blobconverter.from_zoo(
#         name="face-detection-retail-0004",
#         version=OPENVINO_VERSION,
#         shaves=4
#     )) 

#     face_nn_xout = pipeline.create(dai.node.XLinkOut)
#     face_nn_xout.setStreamName("face_nn")
#     face_nn.out.link(face_nn_xout.input)

#     face_nn = device.getOutputQueue("face_nn")

#     # bboxes = np.array(face_nn.get().getFirstLayerFp16())

#     # get all layers　返ってくる
#     conf = np.array(face_nn.getLayerFp16("conf")).reshape((1076, 2))
#     iou = np.array(face_nn.getLayerFp16("iou")).reshape((1076, 1))
#     loc = np.array(face_nn.getLayerFp16("loc")).reshape((1076, 14))




# # cam.preview.link(face_nn.onput)