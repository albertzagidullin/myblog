from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.contrib.postgres.search import TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm

# Create your views here.
# class PostListView(ListView):
#    queryset = Post.published.all()
#    context_object_name = 'posts'
#    paginate_by = 3
#    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    '''
    1 -  Представление принимает опциональный параметр tag_slug, значение
    которого по умолчанию равно None.
     Этот параметр будет передан в URL-адресе

     2 - внутри представления формируется изначальный набор запросов,
     извлекающий все опубликованные посты, и если имеется слаг данного тега,
     то берется обьект Tag с данным слагом ,ипользуя функцию сокращенного доступа get_object_or_404

     3 - затем список постов фильтруется по постам,
     которые содержат данный тег. Поскольку здесь используется взаимосвязь многие-ко-многим,
     необходимо фильтровать записи по тегам, содержащимся в заданном списке,
     который в данном случае содержит только один элемент.
     Здесь используется операция __in поиска по полю.
     Взаимосвязи многие-комногим возникают,
     когда несколько объектов модели ассоциированы с  несколькими объектами другой модели.
      В  нашем приложении пост может иметь несколько тегов,
      и тег может быть связан с несколькими постами.
     '''
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts, 'tag': tag, })


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'form': form})


def post_share(request, post_id):
    """извлечь пост по id """
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        """форма была передана на обработку """
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # поля формы прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read"  f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'fanisovich.a@gmail.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form})


@require_POST
def post_comment(request, post_id):
    '''
    определили представление post_comment, которое принимает объект request и переменную post_id в качестве параметров.
     Мы будем использовать это представление, чтобы управлять передачей поста на обработку.
     Мы ожидаем, что форма будет передаваться с  использованием HTTP-метода POST.
      Мы используем предоставляемый веб-фреймворком Django декоратор require_POST,
       чтобы разрешить запросы методом POST только для этого представления.
        Django позволяет ограничивать разрешенные для представлении HTTP-методы.
        Если пытаться обращаться к представлению посредством любого другого HTTP-метода,
         то Django будет выдавать ошибку HTTP 405 (Метод не разрешен).
    В этом представлении реализованы следующие ниже действия
    1 По id поста извлекается опубликованный пост, используя функцию сокращенного доступа get_object_or_404()

    2 Определяется переменная comment с изначальным значением None.
     Указанная переменная будет использоваться для хранения комментарного объекта при его создании

    3 Создается экземпляр формы, используя переданные на обработку POSTданные,
     и  проводится их валидация методом is_valid().
     Если форма невалидна, то шаблон прорисовывается с ошибками валидации

    4)Если форма валидна, то создается новый объект Comment,
    вызывая метод save() формы, и назначается переменной new_comment, как показано comment = form.save(commit=False)

    5)Метод save() создает экземпляр модели, к которой форма привязана,
    и сохраняет его в базе данных. Если вызывать его, используя commit=False,
    то экземпляр модели создается, но не сохраняется в базе данных. Такой
    подход позволяет видоизменять объект перед его окончательным сохранением

    6)Пост назначается созданному комментарию: comment.post = post

    7)Новый комментарий создается в базе данных путем вызова его метода
    save(): comment.save()
    '''
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    # коммент был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # создать обьект класса Comment, не сохраняя его в бд
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
                ).filter(similarity__gt=0.1).order_by('-similarity')

    return  render(request,
                   'blog/post/search.html',
                   {'form': form,
                    'query': query,
                    'results': results})

'''В приведенном выше представлении сначала создается экземпляр формы 
SearchForm.
 Для проверки того, что форма была передана на обработку,
  в словаре request.GET отыскивается параметр query.
Форма отправляется методом GET, а  не методом POST,
чтобы результирующий URL-адрес содержал параметр query и им было легко делиться.
После передачи формы на обработку создается ее экземпляр,
используя переданные данные GET, и  проверяется валидность данных формы.
Если форма валидна, то с помощью конкретноприкладного экземпляра SearchVector,
сформированного с использованием полей title и body, выполняется поиск опубликованных постов'''