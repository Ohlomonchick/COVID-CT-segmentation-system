import os
import zipfile

import torch
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import *
from .forms import AddCTForm, LayerSelectForm, ArchiveForm
import cv2
from .Model.segmentation_tool import Segmentation, get_color_transp_ims, MyEnsemble
import numpy as np
from PIL import Image
from django.conf import settings
from django.http import HttpResponse
import magic
import pickle
import base64
import patoolib
import shutil


PATH_TO_MODEL = 'segmentation/Model/Unet_7_epochs_0_644.pth'
main_model = torch.load(PATH_TO_MODEL)


def index(request):
    """
    Отображение главной страницы по шаблону index.html
    """
    context = {'title': '42 EPOCHS'}
    return render(request, 'segmentation/index.html', context=context)


# функции сохранения изображений в папку media
def save_output_path(out, name: str, pk: int):
    im = Image.fromarray(np.uint8(out)).convert('RGB')
    global_save_path = os.path.join(settings.MEDIA_ROOT, 'images')
    save_path = os.path.normpath(os.path.join(global_save_path, name + str(pk) + '.png'))

    im.save(save_path)
    return save_path


def save_output_path_segments(out, name: str, pk: int):
    global_save_path = os.path.join(settings.MEDIA_ROOT, 'images')
    save_path = os.path.normpath(os.path.join(global_save_path, name + str(pk) + '.png'))

    cv2.imwrite(save_path, out)
    return save_path


# перевод информации о цвете из hex в rgb
def hex2bgr(h: str):
    h = h.lstrip('#')
    rgb = list(int(h[i:i + 2], 16) for i in (0, 2, 4))

    bgr = rgb[::-1]

    return bgr


def process_image(path, ct, archive=None, create=True):
    """
    Основной процесс загрузки и подготовки изображений к сегментации.
    После сегментации сохраняет маски и полученную информацию в базу данных
    """
    img = cv2.imread(path)
    try:
        shape = str(img.shape)
    except Exception:
        path = os.path.join(settings.MEDIA_ROOT, 'tmp')
        path = os.path.join(path, 'temporary.png')
        img = cv2.imread(path)

    img = cv2.resize(img, (512, 512))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = np.float32(img)

    x = Segmentation(img, model_ens=main_model)
    (percentage1, title1), (percentage2, title2), out, category, semantic_map, orig_im = x.main()

    images = get_color_transp_ims(orig_im, semantic_map, [0, 1, 2], [[0, 0, 0, 255], [0, 0, 0, 255], [0, 0, 0, 255]])

    save_path = save_output_path(out=out, name='segmented_image_', pk=ct.pk)

    ct.segmented_image = save_path
    ct.damage = percentage1 + percentage2
    # print(percentage1, percentage2, ct.damage)
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


def image_for_download(channels, colors, ct, archive=False, only_mask=False):
    """
    Наложение масок на изображение исходя из выбора пользователя, подготовка к скачиванию
    """
    img = cv2.imread(ct.ct_image.path)
    img = cv2.resize(img, (512, 512))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if archive:
        if 0 in channels and ct.ground_glass == 0:
            channels = [x for x in channels if x != 0]
        if 1 in channels and ct.consolidation == 0:
            channels = [x for x in channels if x != 1]

        colors = [colors[channel] for channel in channels]

    np_bytes = base64.b64decode(ct.semantic_map)
    semantic_map = pickle.loads(np_bytes)
    added_im = Segmentation.put_masks(img, semantic_map, channels, colors, only_mask=only_mask)

    cv2.imwrite(ct.segmented_image.path, added_im)


def zip_dir(path, zipfile_handler):
    """
    Функция запаковки архива для скачивания
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            zipfile_handler.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


class AddCT(CreateView):
    """
    - Класс обработки запросов с страницы загрузки изображения для сегментации
    """
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
    """
    - Класс обработки запросов с страницы загрузки архива для сегментации

    Производит распаковку архива и обработку каждого изображения в нём
    """
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

        # print(archive.archive_obj)
        return redirect('result/' + str(ct_main.id))


class ShowSegmented(CreateView):
    """
    - Обработчик страницы с выводом сегментированного изображения
    """
    form_class = LayerSelectForm
    model = CT
    template_name = 'segmentation/result.html'
    pk_url_kwarg = 'ct_pk'
    context_object_name = 'ct'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Производит подготовку формы перед её выводом
        в зависимости от того, был ли загружен архив или одно изображение
        """
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        ct = CT.objects.get(pk=self.kwargs['ct_pk'])
        context['ct'] = ct
        context.pop('object')
        print(context)
        context['title'] = 'Результат'
        print(context['form'].fields)
        if not ct.is_archive:
            if context['ct'].consolidation == 0:
                context['form'].fields['consolidation_color'].widget.attrs['disabled'] = True
                context['form'].fields['consolidation'].widget.attrs['disabled'] = True
                context['form'].fields['consolidation_color'].widget.attrs['style'] = 'display: none;'
                context['form'].fields['consolidation'].widget.attrs['style'] = 'display: none;'
                context['form'].fields['consolidation'].label = ''
            if context['ct'].ground_glass == 0:
                context['form'].fields['ground_glass_color'].widget.attrs['disabled'] = True
                context['form'].fields['ground_glass'].widget.attrs['disabled'] = True
                context['form'].fields['ground_glass_color'].widget.attrs['style'] = 'display: none;'
                context['form'].fields['ground_glass'].widget.attrs['style'] = 'display: none;'
                context['form'].fields['ground_glass'].label = ''
            print(context['form'].fields)
        context['ct'].save()
        return context

    def form_valid(self, form):
        """
        1. Производит получение информаци из формы
        2. Производит вызов функций обработки изображения и подготовки его к скачиванию

        Если был загружен архив, то производит формирование архива с отсегментированными изображениями КТ и
        файлами с описанием поражений, а также подготовку архива к скачиванию
        """
        ct = CT.objects.get(pk=self.kwargs['ct_pk'])

        channels = []
        if form.cleaned_data['ground_glass']:
            channels.append(0)

        if form.cleaned_data['consolidation']:
            channels.append(1)

        if form.cleaned_data['lung_other']:
            channels.append(2)
        if not ct.is_archive:
            colors = [hex2bgr(form.cleaned_data['ground_glass_color']) if ct.ground_glass != 0 else None,
                      hex2bgr(form.cleaned_data['consolidation_color']) if ct.consolidation != 0 else None,
                      hex2bgr(form.cleaned_data['lung_other_color'])]
            colors = [colors[channel] for channel in channels]
            arch = False
        else:
            colors = [hex2bgr(form.cleaned_data['ground_glass_color']),
                      hex2bgr(form.cleaned_data['consolidation_color']),
                      hex2bgr(form.cleaned_data['lung_other_color'])]
            colors = [colors[channel] for channel in channels]
            arch = True

        if ct.is_archive:
            archive_cts = CT.objects.all().filter(is_archive=ct.is_archive)
            zip_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, 'tmp_arch'))
            if os.path.isdir(zip_path):
                shutil.rmtree(zip_path)
            os.mkdir(zip_path)
            for found_ct in archive_cts:
                name = os.path.basename(found_ct.ct_image.path)[:-4] + '.png'
                new_path = os.path.join(zip_path, name)
                found_ct.segmented_image = os.path.normpath(new_path)
                image_for_download(channels=channels, colors=colors, ct=found_ct, archive=arch, only_mask=form.cleaned_data['only_mask'])

                description_name = name[:-4] + '.txt'
                description = f"""Общий процент процент поражения: {found_ct.damage}%
Категория: КТ-{found_ct.category}\n"""
                description += f"""Процент поражения Ground Glass (Матовое стекло): {found_ct.ground_glass}% | Цвет маски: {form.cleaned_data['ground_glass_color']}\n""" * (
                        found_ct.ground_glass != 0)
                description += f"Процент поражения Consolidation (Матовое стекло): {found_ct.consolidation}% | Цвет маски: {form.cleaned_data['consolidation_color']}\n" * (
                        found_ct.consolidation != 0)

                with open(os.path.join(zip_path, description_name), encoding='utf-8', mode='w') as description_f:
                    description_f.write(description)

            zip_handler = zipfile.ZipFile('tmp.zip', 'w', zipfile.ZIP_DEFLATED)
            zip_dir(zip_path, zip_handler)
            zip_handler.close()

            file_buffer = open('tmp.zip', "rb").read()
            content_type = magic.from_buffer(file_buffer, mime=True)
            response = HttpResponse(file_buffer, content_type=content_type)
            filename = 'segmented_images_' + str(ct.id) + '.zip'
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        else:
            image_for_download(channels=channels, colors=colors, ct=ct, only_mask=form.cleaned_data['only_mask'])

            image_buffer = open(ct.segmented_image.path, "rb").read()
            content_type = magic.from_buffer(image_buffer, mime=True)
            response = HttpResponse(image_buffer, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(ct.segmented_image.path)

        return response


