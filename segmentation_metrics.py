#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import totalsegmentator
from typing import Optional
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

        self.classes_to_use = {
            "AB": [
                2, # kidney right
                3, # kidney left
                5, # liver
                6, # stomach
                *range(10, 14+1), #lungs
                *range(26, 50+1), #vertebrae
                51, #heart
                79, # spinal cord
                *range(92, 115+1), # ribs
                116 #sternum
            ],
            "HN": [
                15, # esophagus
                16, # trachea
                17, # thyroid
                *range(26, 50+1), #vertebrae
                79, #spinal cord
                90, # brain
                91, # skull
            ],
            "TH": [
                2, # kidney right
                3, # kidney left
                5, # liver
                6, # stomach
                *range(10, 14+1), #lungs
                *range(26, 50+1), #vertebrae
                51, #heart
                79, # spinal cord
                *range(92, 115+1), # ribs
                116 #sternum
            ]
        }

    
    def score_patient(self, synthetic_ct_location, mask, gt_segmentation, patient_id, orientation=None):        
        # Calculate segmentation metrics
        # Perform segmentation using TotalSegmentator, enforce the orientation of the ground-truth on the output

        anatomy = patient_id[1:3].upper()
        with torch.no_grad():
            pred_seg=self.my_ts.score_patient(synthetic_ct_location, orientation)

        # Retrieve the data in the NiftiImage from nibabel
        if isinstance(pred_seg, Nifti1Image):
            pred_seg = np.array(pred_seg.get_fdata())


        assert pred_seg.shape == gt_segmentation.shape

        # Convert to PyTorch tensors for MONAI
        gt_seg = gt_segmentation.cpu().detach() if torch.is_tensor(gt_segmentation) else torch.from_numpy(gt_segmentation).cpu().detach()
        pred_seg = pred_seg.cpu().detach() if torch.is_tensor(pred_seg) else torch.from_numpy(pred_seg).cpu().detach()


        assert gt_seg.shape == pred_seg.shape
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

        has_classes = any((gt_seg == c).sum() > 0 for c in self.classes_to_use[anatomy])
        result = {}

        if has_classes:
            # Evaluate each one-hot metric 
            for c in self.classes_to_use[anatomy]:
                gt_tensor = (gt_seg == c).view(1, 1, *gt_seg.shape)
                if gt_tensor.sum() == 0:
                    if self.debug:
                        print(f"No {c} in {patient_id}")
                    continue
                est_tensor = (pred_seg == c).view(1, 1, *pred_seg.shape)
                for metric in metrics:
                    metric['f'](est_tensor, gt_tensor, **metric['kwargs'] if 'kwargs' in metric else {})

            # aggregate the mean metrics for the patient over the classes
            for metric in metrics:
                result[metric['name']] = metric['f'].aggregate().item()
                metric['f'].reset()

        else:
            print(f"Warning: patient {patient_id} has no selected classes for anatomy {anatomy}")
            for metric in metrics:
                result[metric['name']] = 0
        return result
