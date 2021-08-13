from django.urls import path
from segmentation.views import *

urlpatterns = [
    path('', index),
]