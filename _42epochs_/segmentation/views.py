import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from segmentation.models import *
from segmentation.forms import AddCTForm
import cv2
from segmentation.Model.segmentation_tool import Segmentation
import numpy as np
from PIL import Image
from django.conf import settings

PATH_TO_MODEL = 'segmentation/Model/Unet_efficientnetb0.pth'


def index(request):
    context = {'title': '42 EPOCHS'}
    return render(request, 'segmentation/index.html', context=context)


class AddCT(CreateView):
    form_class = AddCTForm
    template_name = 'segmentation/addpage.html'
    raise_exception = True

    def form_valid(self, form):
        print(form.cleaned_data)
        # TODO вызывать сегментацию изображения
        ct = form.save()

        img = cv2.imread(ct.ct_image.path)
        img = cv2.resize(img, (512, 512))
        # print('BEFORE CHANNEL CHANGE')
        # print(' -------------- ' + str(img.shape) + ' --------------')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # print('AFTER CHANNEL CHANGE')
        # print(' -------------- ' + str(img.shape) + ' --------------')

        img = np.float32(img)

        x = Segmentation(img, path_to_model=PATH_TO_MODEL)
        (percentage1, title1), (percentage2, title2), out = x.main()

        print(str(title1) + ' ' + str(percentage1) + ' % ')
        print(str(title2) + ' ' + str(percentage2) + ' % ')

        # out = out * 255
        # print('OUT SHAPE')
        # out = out.astype(np.uint8)
        im = Image.fromarray(np.uint8(out)).convert('RGB')
        print(out)

        save_path = os.path.join(settings.MEDIA_ROOT, 'images')
        save_path = os.path.join(save_path, 'segmented_image_' + str(ct.pk) + '.png')
        im.save(save_path)

        ct.segmented_image = save_path
        ct.damage = percentage1 + percentage2
        ct.ground_glass = percentage1
        ct.consolidation = percentage2
        ct.save()

        return redirect('result/' + str(ct.id))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка КТ'
        return context


class ShowSegmented(DetailView):
    model = CT
    template_name = 'segmentation/result.html'
    pk_url_kwarg = 'ct_pk'
    context_object_name = 'ct'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Результат'
        return context
