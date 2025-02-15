# Copyright (c) OpenMMLab. All rights reserved.
from functools import partial

import pytest
import torch

from openprotein.core import average_performance, mAP
from openprotein.models.losses.accuracy import Accuracy, accuracy_numpy


def test_mAP():
    target = torch.Tensor([[1, 1, 0, -1], [1, 1, 0, -1], [0, -1, 1, -1],
                           [0, 1, 0, -1]])
    pred = torch.Tensor([[0.9, 0.8, 0.3, 0.2], [0.1, 0.2, 0.2, 0.1],
                         [0.7, 0.5, 0.9, 0.3], [0.8, 0.1, 0.1, 0.2]])

    # target and pred should both be np.ndarray or torch.Tensor
    with pytest.raises(TypeError):
        target_list = target.tolist()
        _ = mAP(pred, target_list)

    # target and pred should be in the same shape
    with pytest.raises(AssertionError):
        target_shorter = target[:-1]
        _ = mAP(pred, target_shorter)

    assert mAP(pred, target) == pytest.approx(68.75, rel=1e-2)

    target_no_difficult = torch.Tensor([[1, 1, 0, 0], [0, 1, 0, 0],
                                        [0, 0, 1, 0], [1, 0, 0, 0]])
    assert mAP(pred, target_no_difficult) == pytest.approx(70.83, rel=1e-2)


def test_average_performance():
    target = torch.Tensor([[1, 1, 0, -1], [1, 1, 0, -1], [0, -1, 1, -1],
                           [0, 1, 0, -1], [0, 1, 0, -1]])
    pred = torch.Tensor([[0.9, 0.8, 0.3, 0.2], [0.1, 0.2, 0.2, 0.1],
                         [0.7, 0.5, 0.9, 0.3], [0.8, 0.1, 0.1, 0.2],
                         [0.8, 0.1, 0.1, 0.2]])

    # target and pred should both be np.ndarray or torch.Tensor
    with pytest.raises(TypeError):
        target_list = target.tolist()
        _ = average_performance(pred, target_list)

    # target and pred should be in the same shape
    with pytest.raises(AssertionError):
        target_shorter = target[:-1]
        _ = average_performance(pred, target_shorter)

    assert average_performance(pred, target) == average_performance(
        pred, target, thr=0.5)
    assert average_performance(pred, target, thr=0.5, k=2) \
        == average_performance(pred, target, thr=0.5)
    assert average_performance(
        pred, target, thr=0.3) == pytest.approx(
            (31.25, 43.75, 36.46, 33.33, 42.86, 37.50), rel=1e-2)
    assert average_performance(
        pred, target, k=2) == pytest.approx(
            (43.75, 50.00, 46.67, 40.00, 57.14, 47.06), rel=1e-2)


def test_accuracy():
    pred_tensor = torch.tensor([[0.1, 0.2, 0.4], [0.2, 0.5, 0.3],
                                [0.4, 0.3, 0.1], [0.8, 0.9, 0.0]])
    target_tensor = torch.tensor([2, 0, 0, 0])
    pred_array = pred_tensor.numpy()
    target_array = target_tensor.numpy()

    acc_top1 = 50.
    acc_top2 = 75.

    compute_acc = Accuracy(topk=1)
    assert compute_acc(pred_tensor, target_tensor) == acc_top1
    assert compute_acc(pred_array, target_array) == acc_top1

    compute_acc = Accuracy(topk=(1, ))
    assert compute_acc(pred_tensor, target_tensor)[0] == acc_top1
    assert compute_acc(pred_array, target_array)[0] == acc_top1

    compute_acc = Accuracy(topk=(1, 2))
    assert compute_acc(pred_tensor, target_array)[0] == acc_top1
    assert compute_acc(pred_tensor, target_tensor)[1] == acc_top2
    assert compute_acc(pred_array, target_array)[0] == acc_top1
    assert compute_acc(pred_array, target_array)[1] == acc_top2

    with pytest.raises(AssertionError):
        compute_acc(pred_tensor, 'other_type')

    # test accuracy_numpy
    compute_acc = partial(accuracy_numpy, topk=(1, 2))
    assert compute_acc(pred_array, target_array)[0] == acc_top1
    assert compute_acc(pred_array, target_array)[1] == acc_top2
