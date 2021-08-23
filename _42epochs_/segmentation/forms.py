import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
import numpy as np
import cv2
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import *


class AddCTForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ct_image'].empty_label = "Изображение не загружено"

    class Meta:
        model = CT
        fields = ['ct_image']
        widgets = {

            'title': forms.TextInput(attrs={'class': 'uploaded-file'}),
            # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'ct_image': forms.FileInput(attrs={'class': 'uploaded-file'})
        }

    def clean_ct_image(self):
        image = self.files['ct_image']
        # path = image.temporary_file_path()
        if not (str(image)[-3:] == 'png' or str(image)[-3:] == 'jpg'):
            raise ValidationError('Доступна обработка только .png и .jpg изображений')

        tmp_file = default_storage.save('tmp/temporary.' + str(image)[-3:], ContentFile(image.read()))
        path = os.path.join(settings.MEDIA_ROOT, tmp_file)

        print(path)

        pic = cv2.imread(path)
        if pic.shape[0] < 256:
            raise ValidationError('Нужно изображение размером 256x256 и больше')
        if pic.shape[0] != pic.shape[1]:
            raise ValidationError('Нужно изображение с соотношением сторон 1 к 1')
        os.remove(path)

        # cv2.imwrite('../media/lungs/' + str(image)[:-4] + '.png', pic)

        return image