from django.urls import path
from segmentation.views import *

urlpatterns = [
    path('', index, name='home'),
    path('form/', AddCT.as_view(), name='form'),
    path('form/result/<slug:ct_pk>/', ShowSegmented.as_view(), name='result')
]