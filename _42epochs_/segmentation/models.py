from django.db import models


class CT(models.Model):
    ct_image = models.ImageField(upload_to="images", verbose_name="Исходное КТ-изображение", null=True)
    segmented_image = models.ImageField(upload_to="segments/%Y/",  verbose_name="Сегментированное изображение", null=True)
    mask = models.ImageField(upload_to="masks",  verbose_name="Маска", null=True)
    damage = models.IntegerField(verbose_name='Процент поражения', default=0)
    ground_glass = models.IntegerField(verbose_name='Ground glass', default=0, null=True)
    consolidation = models.IntegerField(verbose_name='Consolidation ', default=0, null=True)

    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self):
        return f'#Процент поражения: {self.damage}'

    class Meta:
        verbose_name = 'Томография'
        verbose_name_plural = 'Томографии'
        ordering = ['id']
