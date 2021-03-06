from django.contrib import admin

# Register your models here.
from .models import *


class CTAdmin(admin.ModelAdmin):
    list_display = ('ct_image',
                    'segmented_image',
                    'ground_glass',
                    'consolidation',
                    'damage',
                    'category',
                    'time_create',)


admin.site.site_title = 'Админка'
admin.site.site_header = 'Админка сайта'

admin.site.register(CT, CTAdmin)