import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView
from segmentation.models import *
from segmentation.forms import AddCTForm, LayerSelectForm
import cv2
from segmentation.Model.segmentation_tool import Segmentation, get_color_transp_ims
import numpy as np
from PIL import Image
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse
import magic


PATH_TO_MODEL = 'segmentation/Model/Unet_efficientnetb0.pth'


def index(request):
    context = {'title': '42 EPOCHS'}
    return render(request, 'segmentation/index.html', context=context)


def save_output_path(out, name: str, pk: int):
    im = Image.fromarray(np.uint8(out)).convert('RGB')
    global_save_path = os.path.join(settings.MEDIA_ROOT, 'images')
    save_path = os.path.join(global_save_path, name + str(pk) + '.png')

    im.save(save_path)
    return save_path


def save_output_path_segments(out, name: str, pk: int):
    im = Image.fromarray(np.uint8(out)).convert('RGBA')
    global_save_path = os.path.join(settings.MEDIA_ROOT, 'images')
    save_path = os.path.join(global_save_path, name + str(pk) + '.png')

    # im.save(save_path, format='PNG')
    cv2.imwrite(save_path, out)
    return save_path


class AddCT(CreateView):
    form_class = AddCTForm
    template_name = 'segmentation/addpage.html'
    raise_exception = True

    def form_valid(self, form):
        print(form.cleaned_data)
        ct = form.save()

        img = cv2.imread(ct.ct_image.path)
        print(ct.ct_image.path)
        try:
            print(img.shape)
        except Exception:
            path = os.path.join(settings.MEDIA_ROOT, 'tmp')
            path = os.path.join(path, 'temporary.png')
            img = cv2.imread(path)
        if img.shape[0] > img.shape[1]:
            diff = img.shape[0] - img.shape[1]
            diff1 = diff // 2
            diff2 = diff1 if diff % 2 == 0 else diff1 - 1
            img = img[0 + diff1:img.shape[0] - diff2, 0:img.shape[1]]
        elif img.shape[0] < img.shape[1]:
            diff = img.shape[1] - img.shape[0]
            diff1 = diff // 2
            diff2 = diff1 if diff % 2 == 0 else diff1 - 1
            img = img[0:img.shape[0], 0 + diff1:img.shape[1] - diff2]

        print(img.shape)

        img = cv2.resize(img, (512, 512))
        # print('BEFORE CHANNEL CHANGE')
        # print(' -------------- ' + str(img.shape) + ' --------------')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # print('AFTER CHANNEL CHANGE')
        # print(' -------------- ' + str(img.shape) + ' --------------')

        img = np.float32(img)

        x = Segmentation(img, path_to_model=PATH_TO_MODEL)
        (percentage1, title1), (percentage2, title2), out, category, semantic_map, orig_im = x.main()

        images = get_color_transp_ims(orig_im, semantic_map, [0, 1, 2], [[0, 255, 255, 255], [0, 0, 255, 255], [255, 0, 0, 255]])

        # new_images = []
        # for image in images:


        print(str(title1) + ' ' + str(percentage1) + ' % ')
        print(str(title2) + ' ' + str(percentage2) + ' % ')
        print('Predicted category is - CT-', str(category))

        # out = out * 255
        # print('OUT SHAPE')
        # out = out.astype(np.uint8)

        save_path = save_output_path(out=out, name='segmented_image_', pk=ct.pk)

        ct.segmented_image = save_path
        ct.damage = percentage1 + percentage2
        ct.ground_glass = percentage1
        ct.consolidation = percentage2
        ct.category = category

        ct.ground_glass_im = save_output_path_segments(out=images[0], name='ground_glass_image_', pk=ct.pk)
        ct.consolidation_im = save_output_path_segments(out=images[1], name='consolidation_image_', pk=ct.pk)
        ct.lung_other_im = save_output_path_segments(out=images[2], name='lung_other_image_', pk=ct.pk)
        ct.save()

        return redirect('result/' + str(ct.id))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка КТ'
        return context


class ShowSegmented(DetailView, FormView):
    model = CT
    template_name = 'segmentation/result.html'
    pk_url_kwarg = 'ct_pk'
    context_object_name = 'ct'
    form_class = LayerSelectForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Результат'
        context['download_url'] = 'download/' + str(self.model.pk)
        return context

    def form_valid(self, form):
        print(form.cleaned_data)

        ct = CT.objects.get(pk=self.kwargs['ct_pk'])
        img = cv2.imread(ct.ct_image.path)
        img = cv2.resize(img, (512, 512))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        added_im = img

        if form.cleaned_data['ground_glass']:
            ground_glass_im = cv2.imread(ct.ground_glass_im.path)
            consolidation_im = cv2.cvtColor(ground_glass_im, cv2.COLOR_BGR2BGRA)
            added_im = cv2.addWeighted(added_im, 1, consolidation_im, 1, 0)

        if form.cleaned_data['consolidation']:
            consolidation_im = cv2.imread(ct.consolidation_im.path)
            consolidation_im = cv2.cvtColor(consolidation_im, cv2.COLOR_BGR2BGRA)
            added_im = cv2.addWeighted(img, 1, consolidation_im, 1, 0)

        if form.cleaned_data['lung_other']:
            lung_other_im = cv2.imread(ct.lung_other_im.path)
            lung_other_im = cv2.cvtColor(lung_other_im, cv2.COLOR_BGR2BGRA)
            added_im = cv2.addWeighted(added_im, 1, lung_other_im, 1, 0)

        cv2.imwrite(ct.segmented_image.path, added_im)

        image_buffer = open(ct.segmented_image.path, "rb").read()
        content_type = magic.from_buffer(image_buffer, mime=True)
        response = HttpResponse(image_buffer, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(ct.segmented_image.path)
        return response
