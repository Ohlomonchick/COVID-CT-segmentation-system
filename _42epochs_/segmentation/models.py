from django.db import models


class CT(models.Model):
    ct_image = models.ImageField(upload_to="images", verbose_name="Выберите файл", null=True)
    segmented_image = models.ImageField(upload_to="segments/%Y/",  verbose_name="Сегментированное изображение", null=True)
    mask = models.ImageField(upload_to="masks",  verbose_name="Маска", null=True)
    damage = models.IntegerField(verbose_name='Процент поражения', default=0)
    ground_glass = models.IntegerField(verbose_name='Ground glass', default=0, null=True)
    consolidation = models.IntegerField(verbose_name='Consolidation ', default=0, null=True)
    category = models.IntegerField(verbose_name='Consolidation ', default=0, null=True)

    ground_glass_im = models.ImageField(upload_to="segments/%Y/", verbose_name="Сегментированное изображение",
                                        null=True)
    consolidation_im = models.ImageField(upload_to="segments/%Y/", verbose_name="Сегментированное изображение",
                                        null=True)
    lung_other_im = models.ImageField(upload_to="segments/%Y/", verbose_name="Сегментированное изображение",
                                         null=True)

    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    semantic_map = models.BinaryField(verbose_name="Семантическая карта", null=True)

    is_archive = models.ForeignKey('Archive', on_delete=models.PROTECT,
                                   verbose_name="Архив, к которому принадлежит (если принадлежит)", null=True)

    def __str__(self):
        return f'#Процент поражения: {self.damage}'

    class Meta:
        verbose_name = 'Томография'
        verbose_name_plural = 'Томографии'
        ordering = ['id']


class Archive(models.Model):
    archive_obj = models.FileField(upload_to='archives', verbose_name="Выберите файл", null=True)

    class Meta:
        verbose_name = 'Пакет томографий'
        verbose_name_plural = 'Томографии'
        ordering = ['id']