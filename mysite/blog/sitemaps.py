from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    '''
    определили конкретно-прикладную карту сайта,
    унаследовав класс Sitemap модуля sitemaps.
     Атрибуты changefreq и  priority указывают частоту изменения страниц постов и
      их релевантность на веб-сайте (максимальное значение равно 1)
    '''
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        '''
        Метод items() возвращает набор запросов QuerySet объектов,
        подлежащих включению в эту карту сайта.
        По умолчанию Django вызывает метод get_absolute_url() по каждому объекту,
        чтобы получить его URL-адрес.
        '''
        return Post.published.all()

    def lastmod(self, obj):
        '''
        Метод lastmod получает каждый возвращаемый методом items()
        объект и возвращает время последнего изменения объекта.
        '''
        return obj.updated
