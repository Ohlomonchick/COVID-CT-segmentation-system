#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import torch

from segmentation.Model.segmentation_tool import MyEnsemble


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_42epochs_.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


# Подгрузка ансамбля, старт системы
if __name__ == '__main__':
    PATH_TO_MODEL = './segmentation/Model/Unet_7_epochs_0_644.pth'

    path_to_load1 = './segmentation/Model/Unet_efficientnetb0.pth'
    model1 = torch.load(path_to_load1)
    path_to_load2 = './segmentation/Model/PSPNet_efficientnetb1_cross_entropy_loss_14_epochs.pth'
    model2 = torch.load(path_to_load2)

    MODEL_ENS = MyEnsemble(model1, model2)
    main()
