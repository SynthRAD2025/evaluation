#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import SimpleITK
import numpy as np
from totalsegmentator.python_api import totalsegmentator as ts
import totalsegmentator
from typing import Optional
# from skimage.metrics import peak_signal_noise_ratio, structural_similarity
# from skimage.util.arraycrop import crop
import nibabel as nib
import os
import torch
import SimpleITK
from monai.metrics import DiceMetric, HausdorffDistanceMetric

class SegmentationMetrics():
    def __init__(self):
        # Use fixed wide dynamic range
        self.dynamic_range = [-1024., 3000.]
    
    def score_patient(self, prediction_path, ground_truth_path, mask_path, segmentation_path):        
        # Calculate image metrics

        # print('WEights dir', totalsegmentator.config.get_totalseg_dir())

        gt_seg = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(segmentation_path))
        current_patnum = str(ground_truth_path).split('/')[-1].split('.')[0]
        sitk_mask = SimpleITK.ReadImage(mask_path)
        mask = SimpleITK.GetArrayFromImage(sitk_mask)
        prediction = np.where(mask == 0, -1024, 0)
        maskimg = SimpleITK.GetImageFromArray(prediction)
        maskimg.SetSpacing(sitk_mask.GetSpacing())
        maskimg.SetOrigin(sitk_mask.GetOrigin())
        if os.path.isfile(f'/tmp/currentinput_{current_patnum}.nii.gz'):
            os.remove(f'/tmp/currentinput_{current_patnum}.nii.gz')
        SimpleITK.WriteImage(maskimg, f'/tmp/currentinput_{current_patnum}.nii.gz')

        out_file = f"/output/seg_{str(ground_truth_path).split('/')[-1]}"[:-3] + "nii.gz"
        # print(out_file, ground_truth_path)
        pred_seg = ts(input=f'/tmp/currentinput_{current_patnum}.nii.gz', output=None, ml=True, fast=True, skip_saving=True, nr_thr_resamp=6, nr_thr_saving=6, verbose=False, quiet=True)
        # print('PRED SEG SHAPE', pred_seg.shape)
        if os.path.isfile(f'/tmp/currentinput_{current_patnum}.nii.gz'):
            os.remove(f'/tmp/currentinput_{current_patnum}.nii.gz')

        # print(pred_seg)
        nib.save(pred_seg, out_file)
        pred_seg = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(out_file))


        gt_seg = torch.from_numpy(gt_seg)
        pred_seg = torch.from_numpy(pred_seg)

        classes = gt_seg.unique()
        gt_tensor = torch.zeros(1, len(classes), *gt_seg.shape)
        pred_tensor = torch.zeros(1, len(classes), *gt_seg.shape)
        for (i, c) in enumerate(classes):
            gt_tensor[:, i, ...] = (gt_seg == c)
            pred_tensor[:, i, ...] = (pred_seg == c)

        dice = self.dice(gt_tensor, pred_tensor)
        hd95 = self.hausdorff(gt_tensor, pred_tensor)
        # print(gt_seg.shape, pred_seg.shape)
        return {
            'dice': dice,
            'HD95': hd95
        }

        # prediction = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(prediction_path))
        # ground_truth = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(ground_truth_path))
        # mask = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(mask_path))
        
        # mae_value = self.mae(ground_truth,
        #                      prediction,
        #                      mask)
        
        # psnr_value = self.psnr(ground_truth,
        #                        prediction,
        #                        mask,
        #                        use_population_range=True)
        
        # ssim_value = self.ssim(ground_truth,
        #                        prediction, 
        #                        mask)
        # return {
        #     'mae': mae_value,
        #     'ssim': ssim_value,
        #     'psnr': psnr_value
        # }
    def dice(self, gt_tensor, pred_tensor):
        metric = DiceMetric(include_background=True, reduction="mean", get_not_nans=False)
        metric(pred_tensor, gt_tensor)
        value = metric.aggregate().item()
        return value

    def hausdorff(self, gt_tensor, pred_tensor):
        metric = HausdorffDistanceMetric(include_background=True, reduction="mean", percentile=95, get_not_nans=False)
        metric(pred_tensor, gt_tensor, spacing=3)
        value = metric.aggregate().item()
        return value