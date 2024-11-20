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
from nibabel.nifti1 import Nifti1Image


class SegmentationMetrics():
    def __init__(self):
        # Use fixed wide dynamic range
        self.dynamic_range = [-1024., 3000.]
    
    def score_patient(self, synthetic_ct_location, mask, gt_segmentation, patient_id, orientation=None):        
        # Calculate segmentation metrics
        # Perform segmentation using TotalSegmentator, enforce the orientation of the ground-truth on the output
        with torch.no_grad():
            pred_seg = ts(input=synthetic_ct_location, output=None, orientation=orientation, ml=True, fast=True, skip_saving=True, nr_thr_resamp=1, nr_thr_saving=1, verbose=False, quiet=True)

        # Retrieve the data in the NiftiImage from nibabel
        if isinstance(pred_seg, Nifti1Image):
            pred_seg = np.array(pred_seg.get_fdata())


        assert pred_seg.shape == gt_segmentation.shape

        # Convert to PyTorch tensors for MONAI
        gt_seg = gt_segmentation.cpu().detach() if torch.is_tensor(gt_segmentation) else torch.from_numpy(gt_segmentation).cpu().detach()
        pred_seg = pred_seg.cpu().detach() if torch.is_tensor(pred_seg) else torch.from_numpy(pred_seg).cpu().detach()

        # Convert to one-hot tensors
        classes = gt_seg.unique()
        gt_tensor = torch.zeros(1, len(classes), *gt_seg.shape)
        pred_tensor = torch.zeros(1, len(classes), *gt_seg.shape)
        for (i, c) in enumerate(classes):
            gt_tensor[:, i, ...] = (gt_seg == c)
            pred_tensor[:, i, ...] = (pred_seg == c)


        if orientation is not None:
            spacing, origin, direction = orientation
        else:
            spacing=None

        # Compute the metrics
        dice = self.dice(gt_tensor, pred_tensor)
        hd95 = self.hausdorff(gt_tensor, pred_tensor, spacing=spacing)
        return {
            'dice': dice,
            'HD95': hd95
        }

    def dice(self, gt_tensor, pred_tensor):
        with torch.no_grad():
            metric = DiceMetric(include_background=True, reduction="mean", get_not_nans=False)
            metric(pred_tensor, gt_tensor)
            value = metric.aggregate().item()
            metric.reset()
            return value

    def hausdorff(self, gt_tensor, pred_tensor, spacing=None):
        with torch.no_grad():
            metric = HausdorffDistanceMetric(include_background=True, reduction="mean", percentile=95, get_not_nans=False)
            metric(pred_tensor, gt_tensor, spacing=spacing) # TODO, if fix orientation issue, also remove this reversal 
            value = metric.aggregate().item()
            metric.reset()
            return value