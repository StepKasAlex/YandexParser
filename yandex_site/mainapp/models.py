from django.db import models


class ApartmentInfo(models.Model):
    rooms_info = models.PositiveSmallIntegerField(verbose_name='количество квартир')
    total_area = models.PositiveSmallIntegerField(verbose_name='общая площадь')
    living_space = models.PositiveSmallIntegerField(verbose_name='жилая площадь')
    kitchen_space = models.PositiveSmallIntegerField(verbose_name='площадь кухни')
    floor = models.PositiveSmallIntegerField(verbose_name='этаж')
    is_balcony = models.BooleanField(verbose_name='наличие балкона')
    house_type = models.CharField(max_length=50, verbose_name='тип дома (материал)', null=True)
    finishing = models.CharField(max_length=50, verbose_name='отделка', null=True)
    is_parking = models.CharField(max_length=50, verbose_name='Наличие парковки', null=True)
    is_cctv = models.BooleanField(verbose_name='наличие видеонаблюдения', null=True)
    is_concierge = models.CharField(max_length=50, verbose_name='наличие консьержа', null=True)
    fenced_area = models.BooleanField(verbose_name='огороженная территория', null=True)
    distance_nearest_metro = models.CharField(max_length=25, verbose_name='Расстояние до ближайшей станции',
                                              default='Не определено')
    distance_nearest_ground_transport = models.CharField(max_length=25,
                                                         verbose_name='Расстояние до ближайшей остановки наземного транспорта')
    created_at = models.DateField(verbose_name='время создания', auto_now_add=True)


class Task(models.Model):
    apartment_params_config = models.JSONField(verbose_name='Конфиг с разметкой для параметров апартаментов')
    main_page_config = models.JSONField(verbose_name='Конфиг для главной страницы с настройкой параметров')
    apartments_page_config = models.JSONField(verbose_name='Конфиг для страницы с квартирами')
    apartment_page_config = models.JSONField(verbose_name='Конфиг для страницы с квартирой')
    status = models.PositiveSmallIntegerField(verbose_name='статус')
    created_at = models.DateField(verbose_name='Дата создания', auto_created=True)
