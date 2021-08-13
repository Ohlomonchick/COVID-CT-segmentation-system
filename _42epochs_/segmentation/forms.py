from django import forms
from django.core.exceptions import ValidationError

from .models import *


class AddCTForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Категория не выбрана"

    class Meta:
        model = CT
        fields = ['ct_image']
        widgets = {
            # 'title': forms.TextInput(attrs={'class': 'form-input'}),
            # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            # 'ct_image': forms.
        }

    # def clean_image(self):
    #     image = self.cleaned_data['ct_image']
    #     if len(image) > 200000:
    #         raise ValidationError('Размер файла превышает ....')
    #
    #     return image