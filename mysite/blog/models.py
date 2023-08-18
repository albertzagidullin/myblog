from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset() \
            .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    '''
    Менеджер tags позволит добавлять, извлекать и удалять теги из объектов Post
    '''
    class Status(models.TextChoices):  # поле статуса которое позволяет упрвалять
        # #статусом постов 'черновик - draft', 'опубликован - published'
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year,
                                                 self.publish.month,
                                                 self.publish.day,
                                                 self.slug])


class Comment(models.Model):
    '''
    foreignkey - связь с моделью post,
    Указанная взаимосвязь многие к-одному определена в  модели Comment,
     потому что каждый комментарий будет делаться к одному посту,
      и каждый пост может содержать несколько комментариев
      аттрибут related name позволяет назначать имя атрибуту,
       который используется для связи от обьекта комментария к нему,
       потом легче будет извлекать коммент посредстовм comment.post
       active - Мы определили булево поле active,
        чтобы управлять статусом комментариев.
        Данное поле позволит деактивировать неуместные комментариИ
        вручную с  помощью сайта администрирования.
        Мы используем параметр default=True, чтобы указать,
        что по умолчанию все комментарии активны.

    '''
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Комментарий от {self.name} к {self.post}'