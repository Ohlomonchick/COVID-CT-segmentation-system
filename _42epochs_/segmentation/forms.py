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
            # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'ct_image': forms.FileInput(attrs={'class': 'uploaded-file'})
        }

    def clean_ct_image(self):
        image = self.files['ct_image']
        path = os.path.join(settings.MEDIA_ROOT, 'tmp')
        path = os.path.join(path, 'temporary.png')
        if os.path.exists(path):
            os.remove(path)
        # path = image.temporary_file_path()
        if not (str(image)[-3:] == 'png' or str(image)[-3:] == 'jpg' or str(image)[-4:] == 'jpeg'):
            raise ValidationError('Доступна обработка только .png и .jpg изображений')

        tmp_file = default_storage.save('tmp/temporary.png', ContentFile(image.read()))
        path = os.path.join(settings.MEDIA_ROOT, tmp_file)

        print(path)

        pic = cv2.imread(path)
        if pic.shape[0] < 256:
            raise ValidationError('Нужно изображение размером 256x256 и больше')
        # if pic.shape[0] != pic.shape[1]:
        a = max(pic.shape[0:2])
        b = min(pic.shape[0:2])
        if b * 1.1 < a:
            raise ValidationError('Нужно изображение с соотношением сторон 1 к 1')
        # os.remove(path)

        # cv2.imwrite('../media/lungs/' + str(image)[:-4] + '.png', pic)

        return image


class ArchiveForm(forms.ModelForm):
  class Meta:
    model = Archive
    fields = ['archive_obj']

    widgets = {
        # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
        'archive_obj': forms.FileInput(attrs={'class': 'uploaded-file'})
    }


class LayerSelectForm(forms.Form):
    ground_glass = forms.BooleanField(label='Матовое стекло', required=False, widget=forms.CheckboxInput(
        attrs={'checked': 'checked', 'class': 'ground_glass_checkbox layer_checkbox'}))
    ground_glass_color = forms.CharField(label='', max_length=7, widget=forms.TextInput(
        attrs={'type': 'color', 'class': 'color-pick'}), initial='#FFFF00')

    consolidation = forms.BooleanField(label='Консолидация', required=False, widget=forms.CheckboxInput(
        attrs={'checked': 'checked', 'class': 'consolidation_checkbox layer_checkbox'}))
    consolidation_color = forms.CharField(label='', max_length=7, widget=forms.TextInput(
        attrs={'type': 'color', 'class': 'color-pick'}), initial='#FF0000')

    lung_other = forms.BooleanField(label='Остальная часть лёгкого', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'lung_other_checkbox layer_checkbox'}))
    lung_other_color = forms.CharField(label='', max_length=7, widget=forms.TextInput(
        attrs={'type': 'color', 'class': 'color-pick'}), initial='#0000FF')