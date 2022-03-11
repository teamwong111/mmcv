# Copyright (c) OpenMMLab. All rights reserved.
import numpy as np
import pytest
import torch

_USING_PARROTS = True
try:
    from parrots.autograd import gradcheck
except ImportError:
    from torch.autograd import gradcheck
    _USING_PARROTS = False

# torch.set_printoptions(precision=8, threshold=100)

inputs = [
    ([[1., 0], [0, 1.]], [0, 1]),
    ([[1., 0, -1.], [0, 1., 2.]], [2, 1]),
    ([[1e-6, 2e-6, 3e-6], [4e-6, 5e-5, 6e-4], [7e-3, 8e-2, 9e-1]], [1, 2, 0]),
]

softmax_outputs = [(0.00566451, [[-0.00657264, 0.00657264],
                                 [0.00657264, -0.00657264]]),
                   (0.34956908, [[0.10165970, 0.03739851, -0.13905823],
                                 [0.01227554, -0.10298023, 0.09070466]]),
                   (0.15754992, [[0.02590877, -0.05181759, 0.02590882],
                                 [0.02589641, 0.02589760, -0.05179400],
                                 [-0.07307514, 0.02234372, 0.05073142]])]

sigmoid_outputs = [(0.13562961, [[-0.00657264, 0.11185755],
                                 [0.11185755, -0.00657264]]),
                   (1.10251057, [[0.28808805, 0.11185755, -0.09602935],
                                 [0.11185755, -0.00657264, 0.40376765]]),
                   (0.42287254, [[0.07457182, -0.02485716, 0.07457201],
                                 [0.07457211, 0.07457669, -0.02483728],
                                 [-0.02462499, 0.08277918, 0.18050370]])]


class Testfocalloss(object):

    def _test_softmax(self, dtype=torch.float, device='cpu'):
        from mmcv.ops import SoftmaxFocalLoss
        alpha = 0.25
        gamma = 2.0
        for case, output in zip(inputs, softmax_outputs):
            np_x = np.array(case[0])
            np_y = np.array(case[1])
            np_x_grad = np.array(output[1])

            x = torch.from_numpy(np_x).to(device).type(dtype)
            x.requires_grad_()
            y = torch.from_numpy(np_y).to(device).long()

            model = SoftmaxFocalLoss(gamma, alpha, None, 'mean')
            loss = model(x, y)
            loss.backward()

            assert np.allclose(loss.data.cpu().numpy(), output[0], 1e-2)
            assert np.allclose(x.grad.data.cpu(), np_x_grad, 1e-2)

    def _test_sigmoid(self, dtype=torch.float, device='cpu'):
        from mmcv.ops import SigmoidFocalLoss
        alpha = 0.25
        gamma = 2.0
        for case, output in zip(inputs, sigmoid_outputs):
            np_x = np.array(case[0])
            np_y = np.array(case[1])
            np_x_grad = np.array(output[1])

            x = torch.from_numpy(np_x).to(device).type(dtype)
            x.requires_grad_()
            y = torch.from_numpy(np_y).to(device).long()

            model = SigmoidFocalLoss(gamma, alpha, None, 'mean')
            loss = model(x, y)
            loss.backward()

            assert np.allclose(loss.data.cpu().numpy(), output[0], 1e-2)
            assert np.allclose(x.grad.data.cpu(), np_x_grad, 1e-2)

    def _test_grad_softmax(self, dtype=torch.float, device='cpu'):
        from mmcv.ops import SoftmaxFocalLoss
        alpha = 0.25
        gamma = 2.0
        for case in inputs:
            np_x = np.array(case[0])
            np_y = np.array(case[1])

            x = torch.from_numpy(np_x).to(device).type(dtype)
            x.requires_grad_()
            y = torch.from_numpy(np_y).to(device).long()

            floss = SoftmaxFocalLoss(gamma, alpha)
            if _USING_PARROTS:
                # gradcheck(floss, (x, y),
                #           no_grads=[y])
                pass
            else:
                gradcheck(floss, (x, y), eps=1e-2, atol=1e-2)

    def _test_grad_sigmoid(self, dtype=torch.float, device='cpu'):
        from mmcv.ops import SigmoidFocalLoss
        alpha = 0.25
        gamma = 2.0
        for case in inputs:
            np_x = np.array(case[0])
            np_y = np.array(case[1])

            x = torch.from_numpy(np_x).to(device).type(dtype)
            x.requires_grad_()
            y = torch.from_numpy(np_y).to(device).long()

            floss = SigmoidFocalLoss(gamma, alpha)
            if _USING_PARROTS:
                # gradcheck(floss, (x, y),
                #           no_grads=[y])
                pass
            else:
                gradcheck(floss, (x, y), eps=1e-2, atol=1e-2)

    @pytest.mark.parametrize('device', [
        'cpu',
        pytest.param(
            'cuda',
            marks=pytest.mark.skipif(
                not torch.cuda.is_available(),
                reason='requires CUDA support')),
    ])
    def test_softmax_float(self, device):
        self._test_softmax(torch.float, device)

    @pytest.mark.parametrize('device', [
        'cpu',
        pytest.param(
            'cuda',
            marks=pytest.mark.skipif(
                not torch.cuda.is_available(),
                reason='requires CUDA support')),
    ])
    def test_sigmoid_float(self, device):
        self._test_sigmoid(torch.float, device)

    def test_softmax_half(self):
        self._test_softmax(torch.half, 'cuda')

    def test_sigmoid_half(self):
        self._test_softmax(torch.half, 'cuda')

    @pytest.mark.parametrize('device', [
        'cpu',
        pytest.param(
            'cuda',
            marks=pytest.mark.skipif(
                not torch.cuda.is_available(),
                reason='requires CUDA support')),
    ])
    def test_grad_softmax_float(self, device):
        self._test_grad_softmax(torch.float, device)

    @pytest.mark.parametrize('device', [
        'cpu',
        pytest.param(
            'cuda',
            marks=pytest.mark.skipif(
                not torch.cuda.is_available(),
                reason='requires CUDA support')),
    ])
    def test_grad_sigmoid_float(self, device):
        self._test_grad_sigmoid(torch.float, device)
