#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import SimpleITK
import numpy as np
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
from ts_utils import MinialTotalSegmentator

class SegmentationMetrics():
    def __init__(self, debug=False):
        # Use fixed wide dynamic range
        self.debug = debug
        self.dynamic_range = [-1024., 3000.]
        self.my_ts = MinialTotalSegmentator(verbose=self.debug)

    
    def score_patient(self, synthetic_ct_location, mask, gt_segmentation, patient_id, orientation=None):        
        # Calculate segmentation metrics
        # Perform segmentation using TotalSegmentator, enforce the orientation of the ground-truth on the output

        #BEFORE environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'd47f3a4364cd', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.10', 'PYTHON_SHA256': '07a4356e912900e61a15cb0949a06c4a05012e213ecd6b4e84d0f67aabbee372', 'PYTHONUNBUFFERED': '1', 'HOME': '/home/user', 'GDCM_RESOURCES_PATH': '/home/user/.local/lib/python3.11/site-packages/_gdcm/XML'})

        # print('BEFORE', os.environ)
        with torch.no_grad():
            pred_seg=self.my_ts.score_patient(synthetic_ct_location, orientation)
            # pred_seg = ts(input=synthetic_ct_location, output=None, orientation=orientation, ml=True, fast=True, skip_saving=True, nr_thr_resamp=1, nr_thr_saving=1, verbose=False, quiet=True)
        # print('AFTER', os.environ)
        #AFTER environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'd47f3a4364cd', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.10', 'PYTHON_SHA256': '07a4356e912900e61a15cb0949a06c4a05012e213ecd6b4e84d0f67aabbee372', 'PYTHONUNBUFFERED': '1', 'HOME': '/home/user', 'GDCM_RESOURCES_PATH': '/home/user/.local/lib/python3.11/site-packages/_gdcm/XML', 'nnUNet_raw': '/home/user/.totalsegmentator/nnunet/results', 'nnUNet_preprocessed': '/home/user/.totalsegmentator/nnunet/results', 'nnUNet_results': '/home/user/.totalsegmentator/nnunet/results', 'KMP_DUPLICATE_LIB_OK': 'True', 'KMP_INIT_AT_FORK': 'FALSE'})

        # Retrieve the data in the NiftiImage from nibabel
        if isinstance(pred_seg, Nifti1Image):
            pred_seg = np.array(pred_seg.get_fdata())


        assert pred_seg.shape == gt_segmentation.shape

        # Convert to PyTorch tensors for MONAI
        gt_seg = gt_segmentation.cpu().detach() if torch.is_tensor(gt_segmentation) else torch.from_numpy(gt_segmentation).cpu().detach()
        pred_seg = pred_seg.cpu().detach() if torch.is_tensor(pred_seg) else torch.from_numpy(pred_seg).cpu().detach()

        # Convert to one-hot tensors
        classes = gt_seg.unique()
        if orientation is not None:
            spacing, origin, direction = orientation
        else:
            spacing=None
        
        # list of metrics to evaluate
        metrics = [
            {
                'name': 'DICE',
                'f':DiceMetric(include_background=True, reduction="mean", get_not_nans=False)
            }, {
                'name': 'HD95',
                'f': HausdorffDistanceMetric(include_background=True, reduction="mean", percentile=95, get_not_nans=False),
                'kwargs': {'spacing': spacing}
            }
        ]

        # Evaluate each one-hot metric 
        for c in classes:
            gt_tensor = (gt_seg == c).view(1, 1, *gt_seg.shape)
            est_tensor = (pred_seg == c).view(1, 1, *pred_seg.shape)
            for metric in metrics:
                metric['f'](est_tensor, gt_tensor, **metric['kwargs'] if 'kwargs' in metric else {})

        # aggregate the mean metrics for the patient over the classes
        result = {}
        for metric in metrics:
            result[metric['name']] = metric['f'].aggregate().item()
            metric['f'].reset()
        return result
