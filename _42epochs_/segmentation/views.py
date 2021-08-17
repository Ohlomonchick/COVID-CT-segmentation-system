from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from segmentation.forms import AddCTForm


def index(request):
    return render(request, 'segmentation/index.html')


class AddCT(CreateView):
    form_class = AddCTForm
    template_name = 'segmentation/addpage.html'
    success_url = reverse_lazy('home')
    raise_exception = True

    def form_valid(self, form):
        print(form.cleaned_data)
        form.save()
        # TODO вызывать сегментацию изображения
        return redirect('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка КТ'
        return context
