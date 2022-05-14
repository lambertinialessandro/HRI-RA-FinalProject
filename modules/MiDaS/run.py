"""Compute depth maps for images in the input folder.
"""

import open3d


import os
import glob
import torch
import utils
import cv2
import argparse

import numpy as np
import matplotlib.pyplot as plt

from torchvision.transforms import Compose
from midas.dpt_depth import DPTDepthModel
from midas.midas_net import MidasNet
from midas.midas_net_custom import MidasNet_small
from midas.transforms import Resize, NormalizeImage, PrepareForNet


import platform
input_idx = 0
capture_api = None
if platform.system() == 'Windows':
    input_idx = 1
    capture_api = cv2.CAP_DSHOW


class DeepMonocular():
    def __init__(self, model_path, model_type="large", optimize=True, bits=1):
        self.model_path = model_path
        self.model_type = model_type
        self.optimize = optimize
        self.bits = bits

        self._build_model()

    def _build_model(self):
        print("initialize")

        # select device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("device: %s" % self.device)

        # load network
        if self.model_type == "dpt_large": # DPT-Large
            self.model = DPTDepthModel(
                path=self.model_path,
                backbone="vitl16_384",
                non_negative=True,
            )
            net_w, net_h = 384, 384
            resize_mode = "minimal"
            normalization = NormalizeImage(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        elif self.model_type == "dpt_hybrid": #DPT-Hybrid
            self.model = DPTDepthModel(
                path=self.model_path,
                backbone="vitb_rn50_384",
                non_negative=True,
            )
            net_w, net_h = 384, 384
            resize_mode="minimal"
            normalization = NormalizeImage(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        elif self.model_type == "midas_v21":
            self.model = MidasNet(
                self.model_path,
                non_negative=True
            )
            net_w, net_h = 384, 384
            resize_mode="upper_bound"
            normalization = NormalizeImage(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            )
        elif self.model_type == "midas_v21_small":
            self.model = MidasNet_small(
                self.model_path,
                features=64,
                backbone="efficientnet_lite3",
                exportable=True,
                non_negative=True,
                blocks={'expand': True}
            )
            net_w, net_h = 256, 256
            resize_mode="upper_bound"
            normalization = NormalizeImage(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            )
        else:
            print(f"model_type '{self.model_type}' not implemented, use: --model_type large")
            assert False

        self.transform = Compose(
            [
                Resize(
                    net_w,
                    net_h,
                    resize_target=None,
                    keep_aspect_ratio=True,
                    ensure_multiple_of=32,
                    resize_method=resize_mode,
                    image_interpolation_method=cv2.INTER_CUBIC,
                ),
                normalization,
                PrepareForNet(),
            ]
        )

        self.model.eval()

        if self.optimize==True:
            if self.device == torch.device("cuda"):
                self.model = self.model.to(memory_format=torch.channels_last)
                self.model = self.model.half()

        self.model.to(self.device)

    def run_on_camera(self, input_idx=0, capture_api=None):
        cap = cv2.VideoCapture(input_idx, capture_api)

        try:
            while cap.isOpened():
                success, base_img = cap.read()
                img = cv2.cvtColor(base_img, cv2.COLOR_BGR2RGB) / 255.0
                out = self._compute_depth(img)

                cv2.imshow('image', base_img)
                cv2.imshow('Depth Map', out)

                # rgbd_image = open3d.geometry.RGBDImage.create_from_color_and_depth(
                #     open3d.geometry.Image(base_img), open3d.geometry.Image(out))
                # Camera intrinsic parameters built into Open3D for Prime Sense
                # camera_intrinsic = open3d.camera.PinholeCameraIntrinsic(
                #     open3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)
                # Create the point cloud from images and camera intrisic parameters
                #pcd = open3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, camera_intrinsic)

                # Flip it, otherwise the pointcloud will be upside down
                #pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

                #pcd.paint_uniform_color([1, 0.706, 0])
                #open3d.visualization.draw_geometries([pcd])#, zoom=0.5)

                #open3d.io.write_point_cloud("prova.ply", pcd)

                key = cv2.waitKey(10)
                if key == 27: # "esc"
                    break
                elif key == 113: # "q"
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def run_on_file(self, input_path, output_path):
        img_names = glob.glob(os.path.join(input_path, "*.jpeg"))
        num_images = len(img_names)

        os.makedirs(output_path, exist_ok=True)

        print("start processing")
        for ind, img_name in enumerate(img_names):
            print("  processing {} ({}/{})".format(img_name, ind + 1, num_images))
            img = utils.read_image(img_name)
            out = self._compute_depth(img)

            # output
            filename = os.path.join(
                output_path, os.path.splitext(os.path.basename(img_name))[0]
            )
            utils.write_depth(filename, out, bits=self.bits)

        print("finished")

    def _compute_depth(self, img):
        img_input = self.transform({"image": img})["image"]

        with torch.no_grad():
            sample = torch.from_numpy(img_input).to(self.device).unsqueeze(0)
            if self.optimize and self.device == torch.device("cuda"):
                sample = sample.to(memory_format=torch.channels_last)
                sample = sample.half()
            prediction = self.model.forward(sample)
            prediction = (
                torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                )
                .squeeze()
                .cpu()
                .numpy()
            )

            max_val = prediction.max()
            min_val = prediction.min()
            depth = 1/prediction*1000

            depth_min = depth.min()
            depth_max = depth.max()

            out = max_val * (depth - depth_min) / (depth_max - depth_min) + min_val
        return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_path', default='input',
        help='folder with input images')
    parser.add_argument('-o', '--output_path', default='output',
        help='folder for output images')
    parser.add_argument('-m', '--model_weights', default=None,
        help='path to the trained weights of model')
    parser.add_argument('-t', '--model_type', default='dpt_hybrid', # midas_v21_small
        help='model type: dpt_large, dpt_hybrid, midas_v21_large or midas_v21_small')

    parser.add_argument('--optimize', dest='optimize', action='store_true')
    parser.add_argument('--no-optimize', dest='optimize', action='store_false')
    parser.set_defaults(optimize=True)

    args = parser.parse_args()

    default_models = {
        "midas_v21_small": "weights/midas_v21_small-70d6b9c8.pt",
        "midas_v21": "weights/midas_v21-f6b98070.pt",
        "dpt_large": "weights/dpt_large-midas-2f21e586.pt",
        "dpt_hybrid": "weights/dpt_hybrid-midas-501f0c75.pt",
    }

    if args.model_weights is None:
        args.model_weights = default_models[args.model_type]

    # set torch options
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    dm = DeepMonocular(args.model_weights, args.model_type, args.optimize, bits=1)

    # compute depth maps
    #dm.run_on_camera()

    # compute depth maps
    dm.run_on_file(args.input_path, args.output_path)


