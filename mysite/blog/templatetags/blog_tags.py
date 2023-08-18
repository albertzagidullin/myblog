from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def get_most_commented_posts(count=5):
    '''результат сохраняется в конкретно-прикладной переменной,
     используя аргумент as, за которым следует имя переменной.
     В качестве шаблонного тега используется {% get_most_commented_posts as most_commented_posts %},
      чтобы сохранить результат шаблонного тега в новой переменной с именем most_commented_posts.
       Затем возвращенные посты отображаются, используя HTML-элемент в виде неупорядоченного списка.
       '''
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=3):
    '''
    шаблонный тег который позаоляет увидеть на панели последние три поста
    '''
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
