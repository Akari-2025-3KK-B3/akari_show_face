import argparse
import time
from pathlib import Path

import blobconverter
"""
DepthAIとは深度とAIを組み合わせて使うための見込みプラットフォーム
OAK-D, OAK-1に対応 AKARIには"OAK-D-LITE"が搭載
Python, C++対応
"""
import depthai as dai

OPENVINO_VERSION = '2021.4'

class FACE():
    def __init__(self, pipeline):
        self.face_nn = pipeline.create(dai.node.NeuralNetwork)
        self.face_nn.setBlobPath(blobconverter.from_zoo(
            name="face-detection-retail-0004",
            version=OPENVINO_VERSION,
            shaves=4
        )) 

    def get_face_nn(self):
        return self.face_nn



#     face_nn_xout = pipeline.create(dai.node.XLinkOut)
#     face_nn_xout.setStreamName("face_nn")
#     face_nn.out.link(face_nn_xout.input)

#     face_nn = device.getOutputQueue("face_nn")

#     # bboxes = np.array(face_nn.get().getFirstLayerFp16())

#     # get all layers　返ってくる
#     conf = np.array(face_nn.getLayerFp16("conf")).reshape((1076, 2))
#     iou = np.array(face_nn.getLayerFp16("iou")).reshape((1076, 1))
#     loc = np.array(face_nn.getLayerFp16("loc")).reshape((1076, 14))