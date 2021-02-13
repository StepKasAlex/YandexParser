# Generated by Django 3.1.6 on 2021-02-13 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartmentinfo',
            name='kitchen_space',
            field=models.FloatField(blank=True, verbose_name='площадь кухни'),
        ),
        migrations.AlterField(
            model_name='apartmentinfo',
            name='living_space',
            field=models.FloatField(blank=True, verbose_name='жилая площадь'),
        ),
        migrations.AlterField(
            model_name='apartmentinfo',
            name='total_area',
            field=models.FloatField(blank=True, verbose_name='общая площадь'),
        ),
    ]
