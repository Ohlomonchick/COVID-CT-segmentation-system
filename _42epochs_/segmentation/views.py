from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from segmentation.models import *
from segmentation.forms import AddCTForm


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
