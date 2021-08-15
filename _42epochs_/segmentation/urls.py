from django.urls import path
from segmentation.views import *

urlpatterns = [
    path('', index, name='home'),
    path('form/', AddCT.as_view(), name='form')
]