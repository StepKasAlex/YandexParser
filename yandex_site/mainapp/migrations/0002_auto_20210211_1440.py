# Generated by Django 3.1.6 on 2021-02-11 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='created_at',
            field=models.DateField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]
