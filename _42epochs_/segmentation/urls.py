from django.urls import path
from django.views.decorators.http import require_POST

from segmentation.views import *

urlpatterns = [
    path('', AddCT.as_view(), name='home'),
    # path('form/', AddCT.as_view(), name='form'),
    path('result/<slug:ct_pk>', ShowSegmented.as_view(), name='result'),
    # path('result/', ShowFormLayerSelect.as_view(), name='my_form_view_url'),
    path('archive', AddArchive.as_view(), name='load_archive')
]