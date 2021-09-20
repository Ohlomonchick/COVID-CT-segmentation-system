import os

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from segmentation.models import *
from segmentation.forms import AddCTForm, LayerSelectForm, ArchiveForm
import cv2
from segmentation.Model.segmentation_tool import Segmentation, get_color_transp_ims
import numpy as np
from PIL import Image
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse
import magic
import pickle
import base64
import patoolib
import shutil


PATH_TO_MODEL = 'segmentation/Model/Unet_efficientnetb0.pth'


def index(request):
    context = {'title': '42 EPOCHS'}
    return render(request, 'segmentation/index.html', context=context)


def save_output_path(out, name: str, pk: int):
    im = Image.fromarray(np.uint8(out)).convert('RGB')
    global_save_path = os.path.join(settings.MEDIA_ROOT, 'images')
    save_path = os.path.normpath(os.path.join(global_save_path, name + str(pk) + '.png'))

    im.save(save_path)
    return save_path


def save_output_path_segments(out, name: str, pk: int):
    # im = Image.fromarray(np.uint8(out)).convert('RGBA')
    global_save_path = os.path.join(settings.MEDIA_ROOT, 'images')
    save_path = os.path.normpath(os.path.join(global_save_path, name + str(pk) + '.png'))

    # im.save(save_path, format='PNG')
    cv2.imwrite(save_path, out)
    return save_path


def hex2bgr(h: str):
    h = h.lstrip('#')
    rgb = list(int(h[i:i + 2], 16) for i in (0, 2, 4))

    bgr = rgb[::-1]

    return bgr


def process_image(path, ct, archive=None):
    img = cv2.imread(path)
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

    # print(img.shape)

    img = cv2.resize(img, (512, 512))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = np.float32(img)

    x = Segmentation(img, path_to_model=PATH_TO_MODEL)
    (percentage1, title1), (percentage2, title2), out, category, semantic_map, orig_im = x.main()

    images = get_color_transp_ims(orig_im, semantic_map, [0, 1, 2], [[0, 0, 0, 255], [0, 0, 0, 255], [0, 0, 0, 255]])

    print(str(title1) + ' ' + str(percentage1) + ' % ')
    print(str(title2) + ' ' + str(percentage2) + ' % ')
    print('Predicted category is - CT-', str(category))

    save_path = save_output_path(out=out, name='segmented_image_', pk=ct.pk)

    ct.segmented_image = save_path
    ct.damage = percentage1 + percentage2
    ct.ground_glass = percentage1
    ct.consolidation = percentage2
    ct.category = category

    ct.ground_glass_im = save_output_path_segments(out=images[0], name='ground_glass_image_', pk=ct.pk)
    ct.consolidation_im = save_output_path_segments(out=images[1], name='consolidation_image_', pk=ct.pk)
    ct.lung_other_im = save_output_path_segments(out=images[2], name='lung_other_image_', pk=ct.pk)

    np_bytes = pickle.dumps(semantic_map)
    np_base64 = base64.b64encode(np_bytes)
    ct.semantic_map = np_base64

    if archive:
        ct.is_archive = archive

    ct.save()


class AddCT(CreateView):
    form_class = AddCTForm
    template_name = 'segmentation/addpage.html'
    raise_exception = True

    def form_valid(self, form):
        print(form.cleaned_data)
        ct = form.save()
        process_image(path=ct.ct_image.path, ct=ct)
        return redirect('result/' + str(ct.id))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка КТ'
        return context


class AddArchive(CreateView):
    form_class = ArchiveForm
    template_name = 'segmentation/addarchive.html'
    raise_exception = True
    success_url = 'home'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка Архивом'
        return context

    def form_valid(self, form):
        archive = form.save()
        archive.save()
        unzip_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, 'tmp_arch'))
        if os.path.isdir(unzip_path):
            shutil.rmtree(unzip_path)
            os.mkdir(unzip_path)
        tmp_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, 'tmp'))
        if os.path.isdir(tmp_path):
            shutil.rmtree(tmp_path)
            os.mkdir(tmp_path)
        default_storage.save(os.path.join(tmp_path, str(archive.archive_obj)), ContentFile(archive.archive_obj.read()))

        if os.path.isdir(unzip_path):
            shutil.rmtree(unzip_path)
        os.mkdir(unzip_path)
        patoolib.extract_archive(os.path.join(tmp_path, str(archive.archive_obj)), outdir=unzip_path)

        main_processed = False
        ct_main = CT(damage=0, is_archive=archive)
        ct_main.save()

        for file in os.listdir(unzip_path):
            file_path = os.path.normpath(os.path.join(unzip_path, file))
            print(file_path)
            if not main_processed:
                with open(file_path, 'rb') as f:
                    ct_main.ct_image.save(file, f)
                process_image(path=file_path, ct=ct_main, archive=archive)
                main_processed = True
            else:
                ct = CT(damage=0, is_archive=archive)
                with open(file_path, 'rb') as f:
                    ct.ct_image.save(file, f)
                process_image(path=file_path, ct=ct, archive=archive)

        print(archive.archive_obj)
        return redirect('result/' + str(ct_main.id))


class ShowSegmented(DetailView, FormView):
    model = CT
    template_name = 'segmentation/result.html'
    pk_url_kwarg = 'ct_pk'
    context_object_name = 'ct'
    form_class = LayerSelectForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Результат'
        if context['ct'].consolidation == 0:
            context['form'].fields.pop('consolidation_color')
            context['form'].fields.pop('consolidation')
        if context['ct'].ground_glass == 0:
            context['form'].fields.pop('ground_glass_color')
            context['form'].fields.pop('ground_glass')
        print(context['form'].fields)
        return context

    def form_valid(self, form):
        print(form.cleaned_data)

        ct = CT.objects.get(pk=self.kwargs['ct_pk'])
        img = cv2.imread(ct.ct_image.path)
        img = cv2.resize(img, (512, 512))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        channels = []

        if form.cleaned_data['ground_glass']:
            channels.append(0)

        if form.cleaned_data['consolidation']:
            channels.append(1)

        if form.cleaned_data['lung_other']:
            channels.append(2)

        colors = [hex2bgr(form.cleaned_data['ground_glass_color']),
                  hex2bgr(form.cleaned_data['consolidation_color']),
                  hex2bgr(form.cleaned_data['lung_other_color'])]
        colors = [colors[channel] for channel in channels]
        print(channels, colors)

        np_bytes = base64.b64decode(ct.semantic_map)
        semantic_map = pickle.loads(np_bytes)

        added_im = Segmentation.put_masks(img, semantic_map, channels, colors)

        cv2.imwrite(ct.segmented_image.path, added_im)

        image_buffer = open(ct.segmented_image.path, "rb").read()
        content_type = magic.from_buffer(image_buffer, mime=True)
        response = HttpResponse(image_buffer, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(ct.segmented_image.path)
        return response
