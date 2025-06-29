import numpy as np
from itertools import product

class PriorBox:
    def __init__(self, input_shape=(300, 300), output_shape=(300, 300), variance=[0.1, 0.2]):
        self.min_sizes = [[10, 16, 24], [32, 48], [64, 96], [128, 192, 256]]
        self.steps = [8, 16, 32, 64]
        self.input_shape = input_shape  # NN input size
        self.output_shape = output_shape  # original image size
        self.variance = variance

        self.feature_maps = [
            [int(np.ceil(input_shape[1] / step)), int(np.ceil(input_shape[0] / step))]
            for step in self.steps
        ]

        self.priors = self.generate_priors()

    def generate_priors(self):
        anchors = []
        for k, f_map in enumerate(self.feature_maps):
            min_sizes = self.min_sizes[k]
            for i, j in product(range(f_map[0]), range(f_map[1])):
                for min_size in min_sizes:
                    s_kx = min_size / self.input_shape[0]
                    s_ky = min_size / self.input_shape[1]
                    cx = (j + 0.5) * self.steps[k] / self.input_shape[0]
                    cy = (i + 0.5) * self.steps[k] / self.input_shape[1]
                    anchors.append([cx, cy, s_kx, s_ky])
        return np.clip(np.array(anchors), 0.0, 1.0)  # shape: (1076, 4)
