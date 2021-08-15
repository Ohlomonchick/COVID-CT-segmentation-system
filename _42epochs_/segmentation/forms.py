from django import forms
from django.core.exceptions import ValidationError

from .models import *


class AddCTForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ct_image'].empty_label = "Изображение не загружено"

    class Meta:
        model = CT
        fields = ['ct_image']
        widgets = {

            # 'title': forms.TextInput(attrs={'class': 'form-input'}),
            # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'ct_image': forms.FileInput(attrs={'class': 'form-input'})
        }

    def clean_ct_image(self):
        image = self.cleaned_data['ct_image']
        if image.height() > 256:
            raise ValidationError('Нужна картинка 256x256 и больше')
        if image.height() != image.width():
            raise ValidationError('Нужна картинка 1 к 1')

        return image