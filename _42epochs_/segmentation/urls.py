from django.urls import path

from .views import *

urlpatterns = [
    path('', AddCT.as_view(), name='home'),
    path('result/<slug:ct_pk>', ShowSegmented.as_view(), name='result'),
    path('archive', AddArchive.as_view(), name='load_archive')
]