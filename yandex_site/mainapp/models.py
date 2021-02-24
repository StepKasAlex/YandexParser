from django.db import models


class ApartmentInfo(models.Model):
    price = models.CharField(max_length=255, verbose_name='цена', blank=True, null=True)
    rooms_info = models.CharField(max_length=255, verbose_name='количество квартир', blank=True, null=True)
    total_area = models.CharField(max_length=255, verbose_name='общая площадь', blank=True, null=True)
    living_space = models.CharField(max_length=255, verbose_name='жилая площадь', blank=True, null=True)
    kitchen_space = models.CharField(max_length=255, verbose_name='площадь кухни', blank=True, null=True)
    floor = models.CharField(max_length=255, verbose_name='этаж', blank=True, null=True)
    is_balcony = models.CharField(max_length=255, verbose_name='наличие балкона', blank=True, null=True)
    house_type = models.CharField(max_length=255, verbose_name='тип дома (материал)', blank=True, null=True)
    house_name = models.CharField(max_length=255, verbose_name='название ЖК', blank=True, null=True)
    finishing = models.CharField(max_length=255, verbose_name='отделка', blank=True, null=True)
    is_parking = models.CharField(max_length=255, verbose_name='Наличие парковки', blank=True, null=True)
    is_cctv = models.CharField(max_length=255, verbose_name='наличие видеонаблюдения', blank=True, null=True)
    is_concierge = models.CharField(max_length=255, verbose_name='наличие консьержа', blank=True, null=True)
    fenced_area = models.CharField(max_length=255, verbose_name='огороженная территория', blank=True, null=True)
    distance_nearest_metro = models.CharField(max_length=255, verbose_name='Расстояние до ближайшей станции',
                                              blank=True)
    created_at = models.DateField(verbose_name='время создания', auto_now_add=True),
    apartment_link = models.CharField(max_length=255, default=0, verbose_name='Ссылка на объявление квартиры')


class Task(models.Model):
    main_page_config = models.JSONField(verbose_name='Конфиг с разметкой для параметров апартаментов')
    apartments_page_config = models.JSONField(verbose_name='Конфиг для главной страницы с настройкой параметров')
    apartment_page_sections_config = models.JSONField(verbose_name='Конфиг для страницы с квартирами')
    apartment_page_config = models.JSONField(verbose_name='Конфиг для страницы с квартирой')
    status = models.PositiveSmallIntegerField(verbose_name='статус')
    created_at = models.DateField(verbose_name='Дата создания', auto_now_add=True)
