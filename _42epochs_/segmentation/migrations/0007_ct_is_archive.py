# Generated by Django 3.2.6 on 2021-09-20 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('segmentation', '0006_archive'),
    ]

    operations = [
        migrations.AddField(
            model_name='ct',
            name='is_archive',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='segmentation.archive', verbose_name='Архив, к которому принадлежит (если принадлежит)'),
        ),
    ]
