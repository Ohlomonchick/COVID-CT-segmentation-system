import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
import numpy as np
import cv2
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import *

import patoolib
import shutil


def image_check(image):
    # path = image.temporary_file_path()
    if not (str(image)[-3:] == 'png' or str(image)[-3:] == 'jpg' or image[-4:] == 'jpeg'):
        raise ValidationError('Доступна обработка только .png и .jpg изображений')

    if type(image) != str:
        tmp_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
        path = os.path.join(tmp_path, 'temporary.png')
        if os.path.isdir(tmp_path):
            shutil.rmtree(tmp_path)

        os.mkdir(tmp_path)
        tmp_file = default_storage.save('tmp/temporary.png', ContentFile(image.read()))
        path = os.path.join(settings.MEDIA_ROOT, tmp_file)


        print(path)

        pic = cv2.imread(path)
    else:
        pic = cv2.imread(image)

    if pic.shape[0] < 256:
        raise ValidationError('Необходимо изображение размером 256x256 и больше')
    # if pic.shape[0] != pic.shape[1]:
    a = max(pic.shape[0:2])
    b = min(pic.shape[0:2])
    if b * 1.2 < a:
        raise ValidationError('Необходимо изображение с соотношением сторон 1 к 1')


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
        image_check(image=image)
        # os.remove(path)

        # cv2.imwrite('../media/lungs/' + str(image)[:-4] + '.png', pic)

        return image


class ArchiveForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archive_obj'].empty_label = "Архив не загружен"

    class Meta:
        model = Archive
        fields = ['archive_obj']

        widgets = {
            # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'archive_obj': forms.FileInput(attrs={'class': 'uploaded-file'})
        }

    def clean_archive_obj(self):
        archive = self.files['archive_obj']
        arch_path = os.path.join(settings.MEDIA_ROOT, 'archives')
        arch_path = os.path.join(arch_path, str(archive))
        arch_path = os.path.normpath(arch_path)

        if not (str(archive)[-3:] == 'zip' or str(archive)[-3:] == 'rar' or str(archive)[-4:] == 'jpeg'):
            # os.remove(arch_path)
            raise ValidationError('Доступна обработка только .zip и .rar файлов')

        unzip_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, 'tmp_arch'))
        if os.path.isdir(unzip_path):
            shutil.rmtree(unzip_path)
            os.mkdir(unzip_path)
        tmp_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, 'tmp'))
        if os.path.isdir(tmp_path):
            shutil.rmtree(tmp_path)
            os.mkdir(tmp_path)
        default_storage.save(os.path.join(tmp_path, str(archive)), ContentFile(archive.read()))

        patoolib.extract_archive(os.path.join(tmp_path, str(archive)), outdir=unzip_path)
        for file in os.listdir(unzip_path):
            file_path = os.path.normpath(os.path.join(unzip_path, file))
            image_check(file_path)

        return archive


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