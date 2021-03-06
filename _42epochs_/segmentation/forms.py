import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import *

import patoolib
import shutil


# Функция проверки формата изображения
def image_check(image):
    if not (str(image)[-3:] == 'png' or str(image)[-3:] == 'jpg' or image[-4:] == 'jpeg'):
        raise ValidationError('Доступна обработка только .png и .jpg изображений')


class AddCTForm(forms.ModelForm):
    """Форма загрузки КТ для сегментации"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ct_image'].empty_label = "Изображение не загружено"

    class Meta:
        model = CT
        fields = ['ct_image']
        widgets = {
            'ct_image': forms.FileInput(attrs={'class': 'uploaded-file'})
        }

    def clean_ct_image(self):
        image = self.files['ct_image']
        image_check(image=image)

        return image


class ArchiveForm(forms.ModelForm):
    """
    Форма загрузки архива для сегментации
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archive_obj'].empty_label = "Архив не загружен"

    class Meta:
        model = Archive
        fields = ['archive_obj']

        widgets = {
            'archive_obj': forms.FileInput(attrs={'class': 'uploaded-file'})
        }

    def clean_archive_obj(self):
        """
        Проверяет, действительно ли все файлы архива являются изображениями
        """
        archive = self.files['archive_obj']
        arch_path = os.path.join(settings.MEDIA_ROOT, 'archives')
        arch_path = os.path.join(arch_path, str(archive))
        arch_path = os.path.normpath(arch_path)

        if not (str(archive)[-3:] == 'zip' or str(archive)[-3:] == 'rar' or str(archive)[-4:] == 'jpeg'):
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


class LayerSelectForm(forms.ModelForm):
    ground_glass = forms.BooleanField(label='Матовое стекло', required=False, widget=forms.CheckboxInput(
        attrs={'checked': 'checked', 'class': 'ground_glass_checkbox layer_checkbox'}))
    ground_glass_color = forms.CharField(label='', max_length=7,  required=False, widget=forms.TextInput(
        attrs={'type': 'color', 'class': 'color-pick'}), initial='#FFFF00')

    consolidation = forms.BooleanField(label='Консолидация', required=False, widget=forms.CheckboxInput(
        attrs={'checked': 'checked', 'class': 'consolidation_checkbox layer_checkbox'}))
    consolidation_color = forms.CharField(label='', max_length=7,  required=False, widget=forms.TextInput(
        attrs={'type': 'color', 'class': 'color-pick'}), initial='#FF0000')

    lung_other = forms.BooleanField(label='Остальная часть лёгкого',  required=False, widget=forms.CheckboxInput(
        attrs={'class': 'lung_other_checkbox layer_checkbox'}))
    lung_other_color = forms.CharField(label='', max_length=7, widget=forms.TextInput(
        attrs={'type': 'color', 'class': 'color-pick'}), initial='#0000FF')

    only_mask = forms.BooleanField(label='Только маска', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'lung_other_checkbox layer_checkbox'}))

    class Meta:
        model = CT
        fields = []